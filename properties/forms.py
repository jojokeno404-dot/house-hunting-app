from django import forms
from django.utils import timezone
from .models import Apartment, TourRequest, ApartmentImage


class ApartmentForm(forms.ModelForm):
    class Meta:
        model = Apartment
        fields = [
            'title', 'location', 'price', 'bedrooms',
            'description', 'latitude', 'longitude', 'agent_name', 'agent_phone', 'agent_email'
        ]


class TourRequestForm(forms.ModelForm):
    class Meta:
        model = TourRequest
        fields = ['date']
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
        }

    def clean_date(self):
        selected_date = self.cleaned_data.get('date')
        if selected_date and selected_date < timezone.now().date():
            raise forms.ValidationError("You cannot request a tour for a past date.")
        return selected_date


class ApartmentImageForm(forms.ModelForm):
    image = forms.ImageField(
        required=True,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ApartmentImage
        fields = ['image']