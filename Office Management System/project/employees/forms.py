from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, EmployeeProfile
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role',)

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'is_superuser')

class EmployeeProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeProfile
        exclude = ('user',)
        widgets = {
            'join_date': forms.DateInput(attrs={'type': 'date'}),
        }

