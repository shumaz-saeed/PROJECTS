from django.db import models
from django.conf import settings # To refer to the AUTH_USER_MODEL
from django.utils import timezone

class Project(models.Model):
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Task(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # If user is deleted, task remains but assigned_to becomes NULL
        null=True,
        blank=True,
        related_name='tasks'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    STATUS_CHOICES = (
        ('To-Do', 'To-Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='To-Do')
    deadline = models.DateField(null=True, blank=True)
    priority = models.IntegerField(default=0, help_text="Higher number means higher priority (e.g., 0=Low, 1=Medium, 2=High)")
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['project__name', 'deadline', 'priority', 'title']

    def __str__(self):
        return f"{self.title} ({self.project.name})"
