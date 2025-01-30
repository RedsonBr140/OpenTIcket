from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

from .models import Ticket
from tickets.forms import TicketEditForm, TicketForm

@login_required
def tickets_new(request):
    arguments = {}
    if request.method == "POST":
        form = TicketForm(request.POST, request.FILES)

        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.author = request.user
            ticket.save()
            
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
    

    return render(request, 'tickets/ticket_detail.html', {'ticket':ticket})

@login_required
def ticket_list(request):
    status_filter = request.GET.get('status')
    priority_filter = request.GET.get('priority')
    search_query = request.GET.get('search', '')

    tickets = Ticket.objects.all()

    # If the user is not a staff we want them to have access to their tickets only
    if not request.user.is_staff:
        tickets = tickets.filter(author=request.user)

    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if search_query:
        tickets = tickets.filter(title__icontains=search_query)
        

    tickets = tickets.order_by('-updated_at')

    return render(request, 'tickets/ticket_list.html', {"tickets":tickets, 'search_query': search_query})