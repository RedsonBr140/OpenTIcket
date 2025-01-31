from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class Department(models.Model):
    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")

    name = models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    class Meta:
        verbose_name = _('Ticket')
        verbose_name_plural = _('Tickets')

    # Basic fields
    title = models.CharField(max_length=100)
    description = models.TextField()
    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STATUS_CHOICES = [
        ('new', _('New')),
        ('in_progress', _('In Progress')),
        ('resolved', _('Resolved')),
        ('canceled', _('Canceled')),
    ]
    PRIORITY_CHOICES = [
        ('low', _('Low')),
        ('medium', _('Medium')),
        ('high', _('High')),
    ]

    # Choice fields
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(
        max_length=10, choices=PRIORITY_CHOICES, default='medium')

    # Fields for tracking resolution
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(null=True, blank=True)

    # Relationships
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tickets')
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, related_name='department', null=True)

    def __str__(self):
        return f"{self.title} - {self.status}"
