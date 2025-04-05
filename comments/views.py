from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DeleteView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CommentForm, ReplyForm
from tickets.models import Ticket
from .models import Comment, Reply


class CommentCreateView(LoginRequiredMixin, FormView):
    form_class = CommentForm
    template_name = "comments/form.html"

    def form_valid(self, form):
        ticket = get_object_or_404(Ticket, pk=self.kwargs["pk"])
        comment = form.save(commit=False)
        comment.author = self.request.user
        comment.ticket = ticket
        comment.save()
        return redirect("ticket_detail", pk=ticket.pk)


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    success_url = "/ticket/{ticket_id}"
    template_name = "comments/confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ticket_id"] = self.get_object().ticket.id
        return context

    def get(self, request, *args, **kwargs):
        comment = self.get_object()

        print(comment.author)
        print(request.user)
        if not request.user.is_staff or comment.author != request.user:
            return render(request, "authorization_error.html")
        return super().get(request, *args, **kwargs)


class ReplyCreateView(LoginRequiredMixin, FormView):
    form_class = ReplyForm
    template_name = "comments/form.html"

    def form_valid(self, form):
        comment = get_object_or_404(Comment, pk=self.kwargs["pk"])
        reply = form.save(commit=False)
        reply.author = self.request.user
        reply.comment = comment
        reply.save()
        return redirect("ticket_detail", pk=comment.ticket.pk)


class ReplyDeleteView(LoginRequiredMixin, DeleteView):
    model = Reply
    template_name = "comments/confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comment"] = self.get_object()
        context["ticket_id"] = self.get_object().comment.ticket.id
        return context

    def get_success_url(self):
        reply = self.get_object()
        return reverse("ticket_detail", kwargs={"pk": reply.comment.ticket.pk})

    def get(self, request, *args, **kwargs):
        reply = self.get_object()

        if not request.user.is_staff or reply.author != request.user:
            return render(request, "authorization_error.html")
        return super().get(request, *args, **kwargs)
