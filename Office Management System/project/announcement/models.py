from django.db import models
from django.conf import settings # To refer to the AUTH_USER_MODEL
from django.utils import timezone

class Announcement(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='announcements'
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    VISIBILITY_CHOICES = (
        ('all', 'All Users'),
        ('manager', 'Managers Only'),
        ('employee', 'Employees Only'),
    )
    visible_to = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='all')

    class Meta:
        ordering = ['-created_at'] # Order by most recent announcement

    def __str__(self):
        return f"{self.title} by {self.created_by.username}"

