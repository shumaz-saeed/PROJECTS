from django.db import models
from django.conf import settings # To refer to the AUTH_USER_MODEL
from django.utils import timezone
import os 
class Document(models.Model):
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploaded_documents'
    )
    title = models.CharField(max_length=255)
    # FileField stores the file path relative to MEDIA_ROOT
    file = models.FileField(upload_to='documents/') # Files will be stored in MEDIA_ROOT/documents/
    uploaded_at = models.DateTimeField(auto_now_add=True)

    DEPARTMENT_CHOICES = (
        ('HR', 'Human Resources'),
        ('Finance', 'Finance'),
        ('IT', 'Information Technology'),
        ('Marketing', 'Marketing'),
        ('Operations', 'Operations'),
        ('General', 'General'),
    )
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='General')

    ACCESS_LEVEL_CHOICES = (
        ('public', 'Public (All Users)'),
        ('private', 'Private (Department Specific)'),
    )
    access_level = models.CharField(max_length=10, choices=ACCESS_LEVEL_CHOICES, default='public')

    class Meta:
        ordering = ['-uploaded_at'] # Order by most recent document

    def __str__(self):
        return f"{self.title} ({self.department})"

    def filename(self):
        return os.path.basename(self.file.name)
