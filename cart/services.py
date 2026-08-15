from django.core.exceptions import ValidationError
from django.db import transaction

from products.models import Product

from .models import Cart, CartItem


def get_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@transaction.atomic
def add_item(user, product_id, quantity):
    product = Product.objects.select_for_update().get(pk=product_id)
    if product.status != Product.Status.PUBLISHED or not product.is_available:
        raise ValidationError("This product is not currently available.")
    cart = get_cart(user)
    item, created = CartItem.objects.select_for_update().get_or_create(
        cart=cart, product=product, defaults={"quantity": quantity}
    )
    if not created:
        item.quantity += quantity
    if item.quantity > product.stock:
        raise ValidationError(f"Only {product.stock} unit(s) of {product.name} are available.")
    item.save()
    return cart


@transaction.atomic
def update_item(user, item_id, quantity):
    item = CartItem.objects.select_for_update().select_related("product").get(pk=item_id, cart__user=user)
    if quantity > item.product.stock:
        raise ValidationError(f"Only {item.product.stock} unit(s) of {item.product.name} are available.")
    item.quantity = quantity
    item.save(update_fields=("quantity", "updated_at"))
    return item.cart
