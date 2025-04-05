from django.test import TestCase
from django.contrib.auth.models import User
from tickets.models import Ticket, Company, Department


class TicketModelTest(TestCase):
    def setUp(self):
        # Create related objects
        self.company = Company.objects.create(name="Test Company")
        self.department = Department.objects.create(name="Test Department")
        self.author = User.objects.create_user(username="author", password="password")
        self.assigned_to = User.objects.create_user(
            username="assignee", password="password"
        )

        # Create a Ticket instance
        self.ticket = Ticket.objects.create(
            title="Test Ticket",
            description="This is a test ticket.",
            author=self.author,
            assigned_to=self.assigned_to,
            company=self.company,
            department=self.department,
        )

    def test_ticket_str(self):
        """Test the __str__ method of the Ticket model."""
        self.assertEqual(str(self.ticket), "Test Ticket - new")

    def test_ticket_get_absolute_url(self):
        """Test the get_absolute_url method of the Ticket model."""
        self.assertEqual(self.ticket.get_absolute_url(), f"/ticket/{self.ticket.pk}")

    def test_ticket_default_status(self):
        """Test the default value of the status field."""
        self.assertEqual(self.ticket.status, "new")

    def test_ticket_default_priority(self):
        """Test the default value of the priority field."""
        self.assertEqual(self.ticket.priority, "medium")

    def test_ticket_relationships(self):
        """Test the relationships with Company, Department, and User."""
        self.assertEqual(self.ticket.company, self.company)
        self.assertEqual(self.ticket.department, self.department)
        self.assertEqual(self.ticket.author, self.author)
        self.assertEqual(self.ticket.assigned_to, self.assigned_to)
