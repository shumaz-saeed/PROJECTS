from django import forms
from .models import Project, Task

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date < start_date:
            raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['project', 'assigned_to', 'title', 'description', 'status', 'deadline', 'priority', 'comments']
        widgets = {
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'comments': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optionally, limit assigned_to choices to Employees and Managers
        from employees.models import User # Import here to avoid circular dependency at module level
        self.fields['assigned_to'].queryset = User.objects.filter(role__in=['Employee', 'Manager']).order_by('username')

    def clean(self):
        cleaned_data = super().clean()
        deadline = cleaned_data.get('deadline')
        project_end_date = cleaned_data.get('project').end_date if cleaned_data.get('project') else None

        if deadline and project_end_date and deadline > project_end_date:
            self.add_error('deadline', "Task deadline cannot be after the project's end date.")
        return cleaned_data

