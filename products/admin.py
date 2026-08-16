from django.contrib import admin
from .models import Product, Category, SellerProfile
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id","name"]
    search_fields = ["name"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "owner", "status", "stock", "created_at", "updated_at", "price"]
    search_fields = ["name", "description"]
    list_filter = ["status"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at","id"]

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ["id","user","phone"]
    search_fields = ["user__username", "phone"]
