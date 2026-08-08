from django.shortcuts import render, redirect, get_object_or_404
from .models import Product
from .forms import ProductForm, RegisterForm
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q

class ProductListView(ListView):
    model = Product
    template_name = "products/home.html"
    context_object_name = "products"
    paginate_by = 4

    def get_queryset(self):
        user = self.request.user

        if not user.is_authenticated:
            qs = Product.objects.published().prefetch_related("categories")
        elif user.is_superuser:
            qs = Product.objects.all().select_related("owner").prefetch_related("categories")
        elif user.has_perm("products.add_product"):
            qs = Product.objects.by_owner(user).select_related("owner").prefetch_related("categories")
        else:
            qs = Product.objects.published().select_related("owner").prefetch_related("categories")

        search_query = self.request.GET.get('q')
        category_filter = self.request.GET.get('category')
        ordering = self.request.GET.get('ordering')
        if search_query:
            qs = qs.filter(
                Q(name__icontains=search_query) | Q(description__icontains=search_query) | Q(categories__name__icontains=search_query)
                ).distinct()
        if category_filter:
            qs =qs.filter(categories__name=category_filter)
        if ordering:
            if ordering in ['price','-price','-created_at']:
                qs = qs.order_by(ordering)

        return qs
    
         
'''
def home(request):
    product = Product.objects.published().select_related("owner").prefetch_related("categories")
    return render(request, "products/home.html", {"products": product})
'''


class ProductDetailView(DetailView):
    model = Product
    template_name = "products/product_detail.html"
    context_object_name = "product"


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin,CreateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_Form.html"
    success_url = reverse_lazy("product_form")    # Redirects back to the empty form as you requested
    permission_required = "products.add_product"  # This replaces the @permission_required decorator

    def form_valid(self, form):
        # 1. Attach the logged-in user to the product
        form.instance.owner = self.request.user

        try:
            form.instance.full_clean()
        except ValidationError as exc:
            for feild, errors in exc.message_dict.items():
                for error in errors:
                    form.add_error(feild, error)
            return self.form_invalid(form) # 2. Run your custom model validations (like the out-of-stock check)
        # 3. Save to database
        return super().form_valid(form)

'''
@login_required
@permission_required("products.add_product", raise_exception=True)
def product_form(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            try:
                product.full_clean()
            except ValidationError as exc:
                for field, errors in exc.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
                return render(request, "products/product_Form.html", {"form":form})
 
            product.save()
            form.save_m2m()
            return redirect("product_form")
    else:
        form = ProductForm()
     
    context = {"form": form}
    return render(request, "products/product_Form.html", context)
'''


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "products/product_Form.html"
    success_url = reverse_lazy("home")
    permission_required = "products.change_product"

    def test_func(self):
        # self.get_object() fetches the product we are trying to edit
        product = self.get_object()
        # Return True only if the logged-in user is the owner
        return product.owner == self.request.user

    def form_valid(self, form):
            try:
                form.instance.full_clean()
            except ValidationError as exc:
                for feild, errors in exc.message_dict.items():
                    for error in errors:
                        form.add_error(feild, error)
                return self.form_invalid(form)
            return super().form_valid(form)

'''
@login_required
@permission_required("products.change_product", raise_exception=True)
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            product = form.save(commit=False)
            try:
                product.full_clean()
            except ValidationError as exc:
                for field, errors in exc.message_dict.items():
                    for error in errors:
                        form.add_error(field, error)
                return render(request, "products/product_Form.html", {"form":form})
             
            product.save()
            form.save_m2m()
            return redirect("product_form")            
    else:
        form = ProductForm(instance=product)
    return render(request, "products/product_form.html", {"form": form})
'''


class ProductDeleteView(LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = "products/product_confirm_delete.html"
    success_url = reverse_lazy("home")
    permission_required = "products.delete_product"

    def test_func(self):
        # Exact same object-level security as UpdateView!
        product = self.get_object()
        return product.owner == self.request.user
    
    
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
