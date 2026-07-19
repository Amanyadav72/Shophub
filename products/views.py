from django.shortcuts import render
from django.http import HttpResponse
from .models import Product
from django.shortcuts import get_object_or_404
from .forms import ProductForm


def home(request):
    product = Product.objects.all()
    return render(request, "products/home.html", {"products": product})

def product_form(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            print("Form is Valid")
            product = Product(
                name=form.cleaned_data["name"],
                description=form.cleaned_data["description"],
                price=form.cleaned_data["price"],
                stock=form.cleaned_data["stock"],
                is_available=form.cleaned_data["is_available"],
            )
            product.save()
        else:
            print("Form is Invalid")
            print(form.errors)
    else:
        form = ProductForm()
     
    context = {"form": form}
    return render(request, "products/product_Form.html", context)
