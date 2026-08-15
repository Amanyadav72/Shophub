from django.contrib import admin

from .models import Address, CustomerProfile


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "phone", "updated_at")
    search_fields = ("user__username", "user__email", "phone")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("id", "recipient_name", "user", "city", "is_default")
    list_filter = ("is_default", "address_type", "country")
    search_fields = ("recipient_name", "user__username", "phone", "city")
