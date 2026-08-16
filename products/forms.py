from django import forms
from .models import Product, SellerProfile
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    pass


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "image", "description", "price", "stock", "categories", "status"]
    
        widgets = {
        "description": forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Add Product Description"
                  }
                ),
            }
   

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ["phone", "address", "bio"]
        widgets = {"address": forms.Textarea(attrs={"rows": 3})}
