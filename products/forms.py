from django import forms
from .models import Product
from django.contrib.auth.forms import UserCreationForm

class RegisterForm(UserCreationForm):
    pass


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "image","description", "price", "stock", "categories","is_available","status"]
    
        widgets = {
        "description": forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Add Product Description"
                  }
                ),
            }
   
    def clean_stock(self):
        stock = self.cleaned_data["stock"]
        if stock < 0:
            raise forms.ValidationError("Stock cannot be negative.")
        return stock
