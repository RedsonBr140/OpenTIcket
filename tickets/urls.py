from django.urls import path
from .views import *


urlpatterns = [
    path("ticket_new/", TicketCreateView.as_view(), name="ticket_new"),
    path("ticket/<int:pk>", TicketDetailView.as_view(), name="ticket_detail"),
    path("ticket_edit/<int:pk>", TicketEditView.as_view(), name="ticket_edit"),
    path("tickets/", TicketListView.as_view(), name="ticket_list"),
    path("ticket/<int:pk>/comment/", CommentCreateView.as_view(), name="add_comment"),
    path("comment/<int:pk>/reply/", ReplyCreateView.as_view(), name="add_reply"),
    path("reply/<int:pk>/delete/", ReplyDeleteView.as_view(), name="delete_reply"),
    path("comment/<int:pk>/delete/", CommentDeleteView.as_view(), name="delete_comment"),
]
