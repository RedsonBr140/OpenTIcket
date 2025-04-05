import os
import logging
from celery import shared_task
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import gettext as _

from tickets.models import Ticket

logger = logging.getLogger(__name__)


@shared_task
def send_ticket_email_task(ticket_id, absolute_uri):
    """
    Task to send an email notification to all admin users about a new ticket.

    Args:
        ticket_id (int): The ID of the ticket.
        absolute_uri (str): The base URL to construct the ticket detail link.
    """
    try:
        # Fetch admin users' email addresses
        admins_emails = list(
            User.objects.filter(is_staff=True).values_list("email", flat=True)
        )
        if not admins_emails:
            logger.warning("No admin users found to send the email.")
            return

        # Construct the ticket detail URL
        ticket_url = f"{absolute_uri}{reverse('ticket_detail', args=[ticket_id])}"

        ticket = Ticket.objects.get(id=ticket_id)

        # Render email content
        html_content = render_to_string(
            "email/ticket_notification.html",
            {"ticket": ticket, "reverse_url": ticket_url},
        )
        plain_text = strip_tags(html_content)

        # Get the email sender from environment variables
        email_host_user = os.getenv("EMAIL_HOST_USER")
        if not email_host_user:
            logger.error("EMAIL_HOST_USER environment variable is not set.")
            return

        # Create and send the email
        email = EmailMultiAlternatives(
            subject=_("New Ticket"),
            body=plain_text,
            from_email=email_host_user,
            to=admins_emails,
        )
        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(f"Email sent for ticket ID {ticket_id} to {admins_emails}")

    except Exception as e:
        logger.exception(f"Failed to send email for ticket ID {ticket_id}: {e}")
        raise
