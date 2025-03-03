from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from tickets.models import Ticket


@login_required
def home(request):
    tickets = Ticket.objects.all()

    tickets = tickets.filter(author=request.user)
    return render(request, 'index.html', {'tickets': tickets})
