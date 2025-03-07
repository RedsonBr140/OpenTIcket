from django.urls import path
from .views import *


urlpatterns = [
    path("ticket_new/", TicketCreateView.as_view(), name="ticket_new"),
    path("ticket/<int:ticket_id>", ticket_detail, name="ticket_detail"),
    path("ticket_edit/<int:ticket_id>", ticket_edit, name="ticket_edit"),
    path("tickets/", ticket_list, name="ticket_list"),
    path("test_endpoint", test_endpoint.as_view(), name="test_endpoint"),
]
