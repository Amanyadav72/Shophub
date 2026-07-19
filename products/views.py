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
        print("Form Submitted")

    form = ProductForm()     
    context = {"form": form}
    return render(request, "products/product_create.html", context)
