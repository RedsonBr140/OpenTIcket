from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, include
from django.conf.urls.static import static
from OpenTIcket import settings
from .views import DashboardView, HomeView
from django.utils.translation import gettext as _
from django.conf import settings


urlpatterns = [
    path("dashboard", staff_member_required(DashboardView.as_view()), name="dashboard"),
    path("", HomeView.as_view(), name="home"),
    path("", include("tickets.urls")),
    path("", include("comments.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("avatar/", include("avatar.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = _("OpenTIcket's admin page")
admin.site.site_title = "OpenTIcket"
