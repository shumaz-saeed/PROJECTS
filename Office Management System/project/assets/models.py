from django.db import models
from django.conf import settings # To refer to the AUTH_USER_MODEL
from django.utils import timezone

class Asset(models.Model):
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # If user is deleted, asset becomes unassigned
        null=True,
        blank=True,
        related_name='assigned_assets'
    )

    STATUS_CHOICES = (
        ('in-use', 'In Use'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
        ('available', 'Available'), # Added for clarity
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    # You could add fields like 'maintenance_due_date', 'warranty_expiry_date' etc.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        if self.assigned_to:
            return f"{self.name} ({self.serial_number or 'N/A'}) - Assigned to {self.assigned_to.username}"
        return f"{self.name} ({self.serial_number or 'N/A'}) - {self.get_status_display()}"
