from django.urls import path
from . import views


urlpatterns = [
    path("", views.home, name="home"),
    path("product-form/", views.product_form, name="product_form"),
    path("product/<int:pk>/edit/", views.edit_product, name="edit_product"),
]