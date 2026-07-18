from django import forms
from .models import Product

class ProductForm(forms.Form):
    name = forms.CharField(max_length=100)
    description = forms.CharField()
    price = forms.DecimalField()
    stock = forms.IntegerField()
    is_available = forms.BooleanField(required=False)