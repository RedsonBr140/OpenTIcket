import json
from django.shortcuts import render
from django.views.generic import ListView, View
from calendar import month_name
from tickets.models import Ticket
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count


from django.db.models.functions import TruncMonth
from django.db.models import Count
from calendar import month_name
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        context = {}

        # Resumo
        context["total_tickets"] = Ticket.objects.count()
        context["new_tickets"] = Ticket.objects.filter(
            created_at__week=timezone.now().isocalendar()[1]
        ).count()
        context["pending_tickets"] = Ticket.objects.filter(status="in_progress").count()
        context["closed_tickets"] = Ticket.objects.filter(status="resolved").count()

        # Últimos tickets
        context["latest_tickets"] = Ticket.objects.order_by("-created_at")[:5]

        # Usuários com mais tickets
        top_users = (
            Ticket.objects.values("author__username")
            .annotate(count=Count("id"))
            .order_by("-count")[:5]
        )
        context["top_users"] = [
            (item["author__username"], item["count"]) for item in top_users
        ]

        # Dados do gráfico: tickets resolvidos por mês no último ano
        resolved = (
            Ticket.objects.filter(status="resolved")
            .annotate(month=TruncMonth("resolved_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        # Preparar dados para Chart.js
        labels = []
        data = []
        for entry in resolved:
            month = entry["month"].month
            labels.append(month_name[month])
            data.append(entry["count"])

        context["chart_labels"] = json.dumps(labels)
        context["chart_data"] = json.dumps(data)

        return render(request, "dashboard.html", context)


class HomeView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = "index.html"
    context_object_name = "tickets"

    def get_queryset(self):
        return Ticket.objects.filter(author=self.request.user)
