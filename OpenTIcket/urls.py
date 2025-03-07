from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from OpenTIcket import settings
from .views import home
from django.utils.translation import gettext as _

urlpatterns = [
    path("", home, name="home"),
    path("", include("tickets.urls")),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
]

admin.site.site_header = _("OpenTIcket's admin page")
admin.site.site_title = "OpenTIcket"
