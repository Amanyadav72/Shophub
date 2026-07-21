from django.contrib import admin
from .models import Product
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id","name", "price", "stock", "is_available", "created_at", "updated_at"]
    search_fields = ["name", "description"]
    list_filter = ["is_available"]
    ordering = ["-created_at"]
    readonly_fields = ["created_at", "updated_at","id"]
