import os

from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

@shared_task
def send_ticket_email_task(ticket_id, absolute_uri):
    # Getting the admins' emails for sending the notification.
    admins = User.objects.filter(is_staff=True)
    admins_emails = [admin.email for admin in admins]
    reverse_url = absolute_uri + reverse("ticket_detail", args=[ticket_id])

    html_content = render_to_string(
        "email/ticket_notification.html", {"ticket_id": ticket_id, "reverse_url": reverse_url}
    )
    plain_text = strip_tags(html_content)

    email = EmailMultiAlternatives(
        _("New Ticket"),
        plain_text,
        os.environ.get("EMAIL_HOST_USER"),
        admins_emails,
    )
    email.attach_alternative(html_content, "text/html")
    email.send()