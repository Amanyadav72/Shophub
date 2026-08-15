from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from accounts.models import Address
from cart.models import CartItem

from .models import Order, OrderItem


def address_snapshot(address):
    return {
        "recipient_name": address.recipient_name, "phone": address.phone, "line1": address.line1,
        "line2": address.line2, "city": address.city, "state": address.state,
        "postal_code": address.postal_code, "country": address.country,
    }


@transaction.atomic
def checkout(user, address_id):
    address = Address.objects.get(pk=address_id, user=user)
    items = list(CartItem.objects.select_for_update().select_related("product").filter(cart__user=user))
    if not items:
        raise ValidationError("Your cart is empty.")

    subtotal = Decimal("0.00")
    for item in items:
        product = item.product
        if product.status != product.Status.PUBLISHED or not product.is_available:
            raise ValidationError(f"{product.name} is no longer available.")
        if item.quantity > product.stock:
            raise ValidationError(f"Only {product.stock} unit(s) of {product.name} are available.")
        subtotal += product.price * item.quantity

    shipping_cost = Decimal("0.00")
    tax = Decimal("0.00")
    order = Order.objects.create(
        user=user, subtotal=subtotal, shipping_cost=shipping_cost, tax=tax,
        total=subtotal + shipping_cost + tax, shipping_address=address_snapshot(address),
    )
    order_items = []
    for item in items:
        product = item.product
        line_total = product.price * item.quantity
        order_items.append(OrderItem(
            order=order, product=product, product_name=product.name,
            unit_price=product.price, quantity=item.quantity, subtotal=line_total,
        ))
        product.stock -= item.quantity
        if product.stock == 0:
            product.status = product.Status.OUT_OF_STOCK
            product.is_available = False
            product.save(update_fields=("stock", "status", "is_available", "updated_at"))
        else:
            product.save(update_fields=("stock", "updated_at"))
    OrderItem.objects.bulk_create(order_items)
    CartItem.objects.filter(pk__in=[item.pk for item in items]).delete()
    return order
