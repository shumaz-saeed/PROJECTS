from django import forms
from .models import Asset
from employees.models import User # Import User model to filter choices

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'serial_number', 'description', 'purchase_date', 'assigned_to', 'status']
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter assigned_to choices to only include active employees (or all users if preferred)
        self.fields['assigned_to'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['assigned_to'].required = False # Make assigned_to optional in the form

