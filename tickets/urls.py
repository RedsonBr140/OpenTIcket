from django.urls import path
from .views import *


urlpatterns = [
    path("ticket_new/", TicketCreateView.as_view(), name="ticket_new"),
    path("ticket/<int:pk>", TicketDetailView.as_view(), name="ticket_detail"),
    path("ticket_edit/<int:pk>", TicketEditView.as_view(), name="ticket_edit"),
    path("tickets/", TicketListView.as_view(), name="ticket_list"),
]
