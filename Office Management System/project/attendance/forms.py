from django import forms
from .models import Attendance, LeaveRequest, PublicHoliday
from django.utils import timezone

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['clock_in', 'clock_out'] 
        widgets = {
            'clock_in': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'clock_out': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        clock_in = cleaned_data.get('clock_in')
        clock_out = cleaned_data.get('clock_out')

        if clock_in and clock_out and clock_out <= clock_in:
            raise forms.ValidationError("Clock-out time must be after clock-in time.")
        return cleaned_data

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date:
            if start_date < timezone.localdate():
                raise forms.ValidationError("Start date cannot be in the past.")
            if end_date < start_date:
                raise forms.ValidationError("End date cannot be before start date.")
        return cleaned_data

class LeaveApprovalForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['status'] 
