from django.urls import path
from .views import (
    CommentCreateView,
    CommentDeleteView,
    ReplyCreateView,
    ReplyDeleteView,
)

urlpatterns = [
    path("ticket/<int:pk>/comment/", CommentCreateView.as_view(), name="add_comment"),
    path("comment/<int:pk>/reply/", ReplyCreateView.as_view(), name="add_reply"),
    path("reply/<int:pk>/delete/", ReplyDeleteView.as_view(), name="delete_reply"),
    path(
        "comment/<int:pk>/delete/", CommentDeleteView.as_view(), name="delete_comment"
    ),
]
