from django import forms
from .models import Announcement

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'content', 'visible_to']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }

