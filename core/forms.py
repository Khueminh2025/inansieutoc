from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'customer_name', 'email', 'phone',
            'delivery_method', 'address_city', 'address_district', 'address_detail',
            'total_price', 'receive_time'
        ]

        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'phone': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'email': forms.EmailInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'delivery_method': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'address_city': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'address_district': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'address_detail': forms.Textarea(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'total_price': forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'readonly': 'readonly'}),
            'receive_time': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
        }
