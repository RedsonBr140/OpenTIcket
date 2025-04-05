from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext as _
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
