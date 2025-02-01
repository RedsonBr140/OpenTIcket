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

    # If the user is not a staff we do not want them to see all tickets.
    if request.user.is_staff:
        tickets = Ticket.objects.all()
    else:
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

        # Apply date range filters
        if initial_date:
            tickets = tickets.filter(created_at__gte=initial_date)
        if end_date:
            tickets = tickets.filter(created_at__lte=end_date)

    tickets = tickets.order_by('-updated_at')

    return render(request, 'tickets/ticket_list.html', {"tickets": tickets, 'form': form})
