from django.db import models
from django.conf import settings 
from django.utils import timezone

class Attendance(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances'
    )
    date = models.DateField(default=timezone.now) 
    clock_in = models.DateTimeField(null=True, blank=True)
    clock_out = models.DateTimeField(null=True, blank=True)
    working_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('user', 'date') 
        ordering = ['-date', 'user__username'] # Order by most recent date

    def calculate_working_hours(self):
        if self.clock_in and self.clock_out:
            duration = self.clock_out - self.clock_in
            self.working_hours = round(duration.total_seconds() / 3600, 2)
        else:
            self.working_hours = None

    def save(self, *args, **kwargs):
        self.calculate_working_hours() # Calculate hours before saving
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.date}"

class LeaveRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # If approver is deleted, set this field to NULL
        null=True,
        blank=True,
        related_name='approved_leaves'
    )
    approval_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.start_date} to {self.end_date} ({self.status})"

class PublicHoliday(models.Model):
    date = models.DateField(unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"{self.name} on {self.date}"

