from django import forms
from .models import FinishedBag, Client, Order, Feedback


class FinishedBagForm(forms.ModelForm):
    class Meta:
        model = FinishedBag
        fields = ['variety', 'color', 'gsm', 'quantity_bales', 'location']


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'phone', 'email', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['client', 'bag', 'quantity_ordered']

    # Custom validation to check stock BEFORE saving
    def clean(self):
        cleaned_data = super().clean()
        bag = cleaned_data.get("bag")
        quantity = cleaned_data.get("quantity_ordered")

        if bag and quantity:
            # Check if ordering more than available
            if quantity > bag.quantity_bales:
                raise forms.ValidationError(
                    f"Error: Only {bag.quantity_bales} bales of this item are currently in stock."
                )
        return cleaned_data


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['subject', 'message']

        # We customize the labels to sound like a "Roadmap Planning" tool
        labels = {
            'subject': 'Proposed Feature / Module',
            'message': 'Business Details',
        }

        # We add placeholders to guide the user on what to write
        widgets = {
            'subject': forms.TextInput(attrs={
                'placeholder': 'e.g., "Add Raw Materials Section"'
            }),
            'message': forms.Textarea(attrs={
                'placeholder':  "We need a graph to see monthly profit trends.",
                'rows': 5
            }),
        }