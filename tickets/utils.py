from django.contrib.auth.models import User
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
import environ
from django.template.loader import render_to_string
from django.utils.translation import gettext as _


class StaffMemberRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


def send_ticket_new_email(request, ticket):
    # Getting the admins emails for sending the notification.
    admins = User.objects.filter(is_staff=True)
    admins_emails = [admin.email for admin in admins]
    reverse_url = request.build_absolute_uri(reverse("ticket_detail", args=[ticket.id]))

    html_content = render_to_string(
        "email/ticket_new.html", {"ticket": ticket, "reverse_url": reverse_url}
    )
    plain_text = strip_tags(html_content)

    email = EmailMultiAlternatives(
        _("New Ticket"),
        plain_text,
        environ.os.environ.get("EMAIL_HOST_USER"),
        admins_emails,
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
