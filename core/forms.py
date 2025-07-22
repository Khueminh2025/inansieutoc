from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'phone', 'email', 'notes', 'quantity']  # ❌ Bỏ service & print_option

        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'phone': forms.TextInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'email': forms.EmailInput(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'notes': forms.Textarea(attrs={'class': 'border rounded px-3 py-2 w-full'}),
            'quantity': forms.NumberInput(attrs={'class': 'border rounded px-3 py-2 w-full', 'min': 1}),
        }
