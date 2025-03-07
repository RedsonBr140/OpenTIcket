from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from django.utils.timezone import localtime
from tickets import models


class TicketForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ["title", "description", "department", "company"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control border-secondary",
                    "placeholder": _("Enter ticket title"),
                }
            ),
            "description": forms.Textarea(
                attrs={"class": "form-control", "id": "quill-editor"}
            ),
            "department": forms.Select(attrs={"class": "form-control"}),
            "company": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._populate_department_field()
        self._populate_company_field()

    def _populate_department_field(self):
        departments = models.Department.objects.all()
        self.fields["department"].widget.choices = [
            (dept.id, dept.name) for dept in departments
        ]

    def _populate_company_field(self):
        companies = models.Company.objects.all()
        self.fields["company"].widget.choices = [
            (comp.id, comp.name) for comp in companies
        ]

    def clean_description(self):
        description = self.cleaned_data["description"]
        if description == "<p><br></p>" or not description:
            raise forms.ValidationError(_("You need to provide a description!"))
        return description

    def clean_department(self):
        department = self.cleaned_data["department"]
        if not models.Department.objects.filter(id=department.id).exists():
            raise forms.ValidationError("Invalid department selected.")
        return department


class TicketEditForm(forms.ModelForm):
    class Meta:
        model = models.Ticket
        fields = ["status", "priority", "assigned_to", "resolution_notes"]
        widgets = {
            "status": forms.Select(
                attrs={"class": "form-select bg-dark text-light", "id": "status"}
            ),
            "priority": forms.Select(attrs={"class": "form-select bg-dark text-light"}),
            "assigned_to": forms.Select(
                attrs={"class": "form-select bg-dark text-light"}
            ),
            "resolution_notes": forms.HiddenInput(),
            "resolved_at": forms.DateInput(
                attrs={
                    "class": "form-control bg-dark text-light",
                    "type": "datetime-local",
                }
            ),
        }

    status = forms.ChoiceField(choices=models.Ticket.STATUS_CHOICES)
    priority = forms.ChoiceField(choices=models.Ticket.PRIORITY_CHOICES)
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True), required=False
    )
    resolution_notes = forms.CharField(widget=forms.HiddenInput(), required=False)
    resolved_at = forms.DateTimeField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self._set_initial_values()

    def _set_initial_values(self):
        self.fields["status"].initial = self.instance.status
        self.fields["priority"].initial = self.instance.priority
        self.fields["assigned_to"].initial = self.instance.assigned_to
        self.fields["resolution_notes"].initial = self.instance.resolution_notes
        self.fields["resolved_at"].initial = (
            localtime(self.instance.resolved_at).strftime("%Y-%m-%dT%H:%M")
            if self.instance.resolved_at
            else None
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.resolved_at = self.cleaned_data.get("resolved_at") or None
        if commit:
            instance.save()
        return instance


class TicketListFilterForm(forms.Form):
    status = forms.ChoiceField(
        choices=[("", _("All Status"))] + models.Ticket.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    priority = forms.ChoiceField(
        choices=[("", _("All Priorities"))] + models.Ticket.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(is_staff=True),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    department = forms.ModelChoiceField(
        queryset=models.Department.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    company = forms.ModelChoiceField(
        queryset=models.Company.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    search_query = forms.CharField(
        required=False, widget=forms.TextInput(attrs={"class": "form-control"})
    )
    initial_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"type": "date", "class": "form-control"}),
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.TextInput(attrs={"type": "date", "class": "form-control"}),
    )

    def clean_search_field(self):
        return self.cleaned_data["search_field"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_initial_values()

    def _set_initial_values(self):
        if not self.data.get("status"):
            self.fields["status"].initial = ""
        if not self.data.get("priority"):
            self.fields["priority"].initial = ""
        if not self.data.get("department"):
            self.fields["department"].initial = ""
        if not self.data.get("company"):
            self.fields["company"].initial = ""
