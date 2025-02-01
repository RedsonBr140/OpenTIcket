import os

import openpyxl
from django.http import HttpResponse
from django.urls import reverse
from django.db.models import Q
import environ
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.utils.translation import gettext as _
from django.template.loader import render_to_string
from openpyxl.utils import get_column_letter

from OpenTIcket import settings
from .models import Ticket
from tickets.forms import TicketEditForm, TicketForm, TicketListFilterForm


def send_ticket_new_email(request, ticket):
    # Getting the admins emails for sending the notification.
    admins = User.objects.filter(is_staff=True)
    admins_emails = [admin.email for admin in admins]
    reverse_url = request.build_absolute_uri(
        reverse('ticket_detail', args=[ticket.id]))

    html_content = render_to_string(
        'email/ticket_new.html', {'ticket': ticket, 'reverse_url': reverse_url})
    plain_text = strip_tags(html_content)

    email = EmailMultiAlternatives(
        _("New Ticket"), plain_text, environ.os.environ.get("EMAIL_HOST_USER"), admins_emails)
    email.attach_alternative(html_content, "text/html")
    email.send()


@login_required
def tickets_new(request):
    arguments = {}
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.author = request.user
            ticket.save()

            send_ticket_new_email(request, ticket)

            return redirect('ticket_detail', ticket_id=ticket.id)

    form = TicketForm()

    arguments['form'] = form
    return render(request, 'tickets/ticket_new.html', arguments)


@staff_member_required
def ticket_edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    staff_users = User.objects.filter(is_staff=True)


    arguments = {
        'ticket': ticket,
        'users': staff_users
    }

    if request.method == "POST":
        # For POST requests, bind the form to the submitted data and the ticket instance
        form = TicketEditForm(request.POST, instance=ticket)
        arguments['form'] = form

        if form.is_valid():
            # Save the form directly (no need to manually update the ticket fields)
            form.save()
            return redirect('ticket_detail', ticket_id=ticket_id)

        # If the form is invalid, re-render the page with the form and errors
        return render(request, 'tickets/ticket_edit.html', arguments)
    else:
        # For GET requests, initialize the form with the ticket instance
        form = TicketEditForm(instance=ticket)
        arguments['form'] = form

        return render(request, 'tickets/ticket_edit.html', arguments)


@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)

    if not request.user.is_staff and ticket.author.id is not request.user.id:
        return render(request, 'authorization_error.html')

    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})


@login_required
def ticket_list(request):
    form = TicketListFilterForm(request.GET)
    tickets = Ticket.objects.all()

    if not request.user.is_staff:
        tickets = tickets.filter(author=request.user)

    if form.is_valid():
        status_filter = form.cleaned_data.get('status')
        priority_filter = form.cleaned_data.get('priority')
        assigned_to_filter = form.cleaned_data.get('assigned_to')
        search_query = form.cleaned_data.get('search_query')
        initial_date = form.cleaned_data.get('initial_date')
        end_date = form.cleaned_data.get('end_date')

        if status_filter:
            tickets = tickets.filter(status=status_filter)
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter)
        if assigned_to_filter:
            tickets = tickets.filter(assigned_to=assigned_to_filter)
        if search_query:
            tickets = tickets.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(status__icontains=search_query) |
                Q(priority__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(author__first_name__icontains=search_query)
            )
        if initial_date:
            tickets = tickets.filter(created_at__gte=initial_date)
        if end_date:
            tickets = tickets.filter(created_at__lte=end_date)

    tickets = tickets.order_by('-updated_at')

    # Check for the 'download' parameter to trigger Excel file generation
    if 'download' in request.GET:
        # Prepare the Excel sheet
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = "Tickets"

        # Define the headers for the Excel sheet
        headers = ["ID", "Title", "Description", "Company", "Department", "Status", "Priority", "Assigned To", "Author", "Created At", "Updated At", "Resolved at"]
        sheet.append(headers)

        # Populate the rows with ticket data
        for ticket in tickets:
            row = [
                ticket.id,
                ticket.title,
                ticket.description,
                ticket.company.name,
                ticket.department.name,
                ticket.status,
                ticket.priority,
                ticket.assigned_to.username if ticket.assigned_to else '',
                ticket.author.username,
                ticket.created_at.strftime('%Y-%m-%d %H:%M'),
                ticket.updated_at.strftime('%Y-%m-%d %H:%M'),
                ticket.resolved_at.strftime('%Y-%m-%d %H:%M') if ticket.resolved_at else '---'
            ]
            sheet.append(row)

            # Adjust column widths based on the longest text
            for col_num in range(1, len(headers) + 1):
                max_length = 0
                column = get_column_letter(col_num)
                for row in sheet.iter_rows(min_col=col_num, max_col=col_num):
                    for cell in row:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(cell.value)
                        except:
                            pass
                adjusted_width = (max_length + 2)
                sheet.column_dimensions[column].width = adjusted_width

            # Adjust row height to fit the content
            for row in sheet.iter_rows(min_row=2, max_row=sheet.max_row):
                for cell in row:
                    try:
                        # Check if the row needs to be resized
                        cell_value = str(cell.value)
                        if len(cell_value) > 50:  # Adjust the number as needed
                            sheet.row_dimensions[cell.row].height = 40  # You can adjust the height value
                    except:
                        pass

        # Create an HttpResponse to serve the Excel file
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="tickets.xlsx"'

        # Save the workbook to the response
        workbook.save(response)
        return response

    # TODO: Add pagination

    # Default rendering of ticket list
    return render(request, 'tickets/ticket_list.html', {"tickets": tickets, 'form': form})
