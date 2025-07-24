    # authe/users/forms.py

from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):

        class Meta:
            model = UserProfile
            fields = ['bio', 'website', 'date_of_birth'] 
            widgets = {
                'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            }
    