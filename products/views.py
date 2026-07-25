from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Product
from .forms import ProductForm, RegisterForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required


def home(request):
    product = Product.objects.all()
    print(request.user)
    print(request.user.is_authenticated)
    return render(request, "products/home.html", {"products": product})

@login_required
@permission_required("products.add_product", raise_exception=True)
def product_form(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            print("Form is Valid")
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            print("Product saved successfully")
            return redirect("product_form")
        else:
            print("Form is Invalid")
            print(form.errors)
    else:
        form = ProductForm()
     
    context = {"form": form}
    return render(request, "products/product_Form.html", context)

@login_required
@permission_required("products.change_product", raise_exception=True)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        print("POST received")
        print("FORM VALID:", form.is_valid())
        print("FORM ERRORS:", form.errors)

        if form.is_valid():
            form.save()
            print("PRODUCT UPDATED")
            return redirect("home")

    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_form.html", {"form": form})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            print("Valid user Form")
            form.save()
            return redirect("home")
        else:
            print("Invalid user Form")
    
    else:
        form = RegisterForm()

    return render(request, "products/register.html", {"form" : form})

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            print("Valid user")
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next")
            #longer version for next url
            '''if next_url:
                return redirect(next_url)
            return redirect("home")'''
            return redirect(next_url or "home")
            
        else:
            print(form.errors)
    else:
        form = AuthenticationForm()
    return render(request, "products/login.html", {"form" : form})

def user_logout(request):
    logout(request)
    print("Loged out")
    return redirect("home")

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            print("password Updated Sucessfully")
            return redirect("home")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "products/change_password.html", {"form":form})