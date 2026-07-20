from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Product
from .forms import ProductForm


def home(request):
    product = Product.objects.all()
    return render(request, "products/home.html", {"products": product})

def product_form(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            print("Form is Valid")
            form.save()
            print("Product saved successfully")
            return redirect("product_form")
        else:
            print("Form is Invalid")
            print(form.errors)
    else:
        form = ProductForm()
     
    context = {"form": form}
    return render(request, "products/product_Form.html", context)

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'Post':
        form = ProductForm(request.Post, instance=product)

        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm(instance=product)
    
    return render(request, "products/product_form.html", {"form":form})
