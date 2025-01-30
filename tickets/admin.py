from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Department, Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'id', 'status', 'department__name', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'id', 'description', 'author__username', 'department__name')
    ordering = ('-created_at',)

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name', 'id')