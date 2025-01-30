from django import forms
from tickets import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        departments = models.Department.objects.all()
        self.fields['department'].widget.choices = [(dept.id, dept.name) for dept in departments]
        self.fields['department'].widget.attrs = {'class': 'form-control bg-dark text-light'}
    class Meta:
        model = models.Ticket
        fields = [
            'title',
            'description',
            # 'priority',
            'department'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'id': 'quill-editor'}),
            'department': forms.Select()
        }
    def clean_description(self):
        description = self.cleaned_data['description']
        if description == "<p><br></p>" or not description:
            raise forms.ValidationError(_('You need to provide a description!'))
        return description
    
    def clean_department(self):
        # Get the submitted value
        department = self.cleaned_data['department']
        try:
            # Ensure the department exists in the database
            models.Department.objects.get(id=department.id)
        except models.Department.DoesNotExist:
            raise forms.ValidationError("Invalid department selected.")
        return department
    
class TicketEditForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ['status', 'priority', 'assigned_to', 'resolution_notes']

    # Ensure that 'status' and 'priority' are restricted to valid choices
    status = forms.ChoiceField(choices=models.Ticket.STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select bg-dark text-light'}))
    priority = forms.ChoiceField(choices=models.Ticket.PRIORITY_CHOICES, widget=forms.Select(attrs={'class': 'form-select bg-dark text-light'}))
    
    # 'assigned_to' will use a ModelChoiceField to get users
    assigned_to = forms.ModelChoiceField(required=False, queryset=User.objects.filter(is_staff=True), widget=forms.Select(attrs={'class': 'form-select bg-dark text-light'}))

    # 'resolution_notes' will be a CharField, with the initial value set to the current resolution notes of the ticket
    resolution_notes = forms.CharField(
        widget=forms.HiddenInput(), required=False
    )

    def __init__(self, *args, **kwargs):
        # Populating the form with any existing ticket instance if available
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Set the initial value for the fields.
            self.fields['status'].initial = self.instance.status
            self.fields['priority'].initial = self.instance.priority
            self.fields['assigned_to'].initial = self.instance.assigned_to
            self.fields['resolution_notes'].initial = self.instance.resolution_notes