from django.utils.timezone import localtime

from django import forms
from tickets import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


        # Populate departments field
        departments = models.Department.objects.all()
        self.fields['department'].widget.choices = [
            (dept.id, dept.name) for dept in departments]
        self.fields['department'].widget.attrs = {
            'class': 'form-control bg-dark text-light'}

        # Populate companies field
        companies = models.Company.objects.all()
        self.fields['company'].widget.choices = [
            (comp.id, comp.name) for comp in companies
        ]
        self.fields['company'].widget.attrs = {
            'class': 'form-control bg-dark text-light'
        }

    class Meta:
        model = models.Ticket
        fields = [
            'title',
            'description',
            'department',
            'company',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control bg-dark text-light border-secondary', 'placeholder': _("Enter ticket title")}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'id': 'quill-editor'}),
            'department': forms.Select(),
            'company': forms.Select()
        }

    def clean_description(self):
        description = self.cleaned_data['description']
        if description == "<p><br></p>" or not description:
            raise forms.ValidationError(
                _('You need to provide a description!'))
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
        fields = ['status', 'priority', 'assigned_to',
                  'resolution_notes',]

    # Ensure that 'status' and 'priority' are restricted to valid choices
    status = forms.ChoiceField(choices=models.Ticket.STATUS_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select bg-dark text-light', 'id': 'status'}))
    priority = forms.ChoiceField(choices=models.Ticket.PRIORITY_CHOICES, widget=forms.Select(
        attrs={'class': 'form-select bg-dark text-light'}))

    # 'assigned_to' will use a ModelChoiceField to get users
    assigned_to = forms.ModelChoiceField(required=False, queryset=User.objects.filter(
        is_staff=True), widget=forms.Select(attrs={'class': 'form-select bg-dark text-light'}))

    # 'resolution_notes' will be a CharField, with the initial value set to the current resolution notes of the ticket
    resolution_notes = forms.CharField(
        widget=forms.HiddenInput(), required=False
    )

    resolved_at = forms.DateTimeField(
        required=False, widget=forms.DateInput(attrs={'class': 'form-control bg-dark text-light', 'type': 'datetime-local'}))

    def __init__(self, *args, **kwargs):
        # Populating the form with any existing ticket instance if available
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Set the initial value for the fields.
            self.fields['status'].initial = self.instance.status
            self.fields['priority'].initial = self.instance.priority
            self.fields['assigned_to'].initial = self.instance.assigned_to
            self.fields['resolution_notes'].initial = self.instance.resolution_notes
            self.fields['resolved_at'].initial = localtime(self.instance.resolved_at).strftime("%Y-%m-%dT%H:%M") if self.instance.resolved_at else None

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('resolved_at'):
            instance.resolved_at = self.cleaned_data['resolved_at']
        else:
            instance.resolved_at = None  # Set to None if the field is empty

        if commit:
            instance.save()
        return instance


class TicketListFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[('', _('All Status'))] + models.Ticket.STATUS_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-light'})
    )
    priority = forms.ChoiceField(
        choices=[('', _('All Priorities'))] + models.Ticket.PRIORITY_CHOICES, required=False,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-light'})
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select bg-dark text-light'})
    )
    search_query = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'form-control bg-dark text-light border-secondary'})
    )

    initial_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date', 'class':'form-control bg-dark text-light'}))
    end_date = forms.DateField(required=False, widget=forms.TextInput(attrs={'type': 'date', 'class':'form-control bg-dark text-light'}))

    def clean_search_field(self):
        return self.cleaned_data["search_field"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.data.get('status'):
            self.fields['status'].initial = ''
        if not self.data.get('priority'):
            self.fields['priority'].initial = ''
