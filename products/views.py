from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm, RegisterForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST


def home(request):
    product = Product.objects.select_related("owner").prefetch_related("categories")
    return render(request, "products/home.html", {"products": product})

@login_required
@permission_required("products.add_product", raise_exception=True)
def product_form(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save()
            form.save_m2m()
            return redirect("product_form")
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

        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            form.save_m2m()
            return redirect("home")

    else:
        form = ProductForm(instance=product)

    return render(request, "products/product_form.html", {"form": form})

def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect("home")
    
    else:
        form = RegisterForm()

    return render(request, "products/register.html", {"form" : form})

def user_login(request):
    next_url = request.POST.get("next") or request.GET.get("next")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()
            login(request, user)

            if next_url and url_has_allowed_host_and_scheme(
                url=next_url,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            ):
                return redirect(next_url)

            return redirect("home")
    else:
        form = AuthenticationForm()

    return render(request, "products/login.html", {"form": form, "next": next_url})

@login_required
@require_POST
def user_logout(request):
    logout(request)
    return redirect("home")

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("home")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "products/change_password.html", {"form":form})
