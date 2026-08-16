from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path("", views.ProductListView.as_view(), name="home"),
    path("my-products/", views.MyProductListView.as_view(), name="my_products"),
    path("my-products/create/", views.ProductCreateView.as_view(), name="product_form"),
    path("my-products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="edit_product"),
    path("my-products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name = "delete_product"),
    path("product-detail/<int:pk>/", views.ProductDetailView.as_view(), name="product_detail"),
    path("register/",views.register, name="register"  ),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("change-password/", views.change_password, name="change_password"),
    path("profile/", views.seller_profile, name="seller_profile"),
    path("profile/edit/", views.seller_profile_edit, name="seller_profile_edit"),
    path(
         "password-reset/",
         auth_views.PasswordResetView.as_view
         (
          template_name="products/password_reset.html",
          email_template_name="products/password_reset_email.html",
          success_url="/password-reset/done/"
         ),
         name="password_reset"
        ),

    path(
         "password-reset/done/",
          auth_views.PasswordResetDoneView.as_view(
          template_name="products/password_reset_done.html"
          ),
          name="password_reset_done"
        ),

    path(
         "reset/<uidb64>/<token>/",
         auth_views.PasswordResetConfirmView.as_view(
         template_name="products/password_reset_confirm.html",
         success_url="/reset/done/"
         ),
         name="password_reset_confirm"
        ),

    path(
         "reset/done/",
         auth_views.PasswordResetCompleteView.as_view(
         template_name="products/password_reset_complete.html"
         ),
         name="password_reset_complete"
        ),
]
