from django.urls import path
from tickets import views


urlpatterns = [
    path("ticket_new/", views.tickets_new, name="ticket_new"),
    path("ticket/<int:ticket_id>", views.ticket_detail, name="ticket_detail"),
    path("ticket_edit/<int:ticket_id>", views.ticket_edit, name="ticket_edit"),
    path("tickets/", views.ticket_list, name="ticket_list")
]