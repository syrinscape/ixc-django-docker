from importlib import import_module
import os

from django.conf import settings
from django.urls import include, re_path
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView

admin.autodiscover()

urlpatterns = [
    # Test error templates.
    re_path(r"^404/$", TemplateView.as_view(template_name="404.html")),
    re_path(r"^500/$", TemplateView.as_view(template_name="500.html")),
]

# Django Admin.
if "django.contrib.admin" in settings.INSTALLED_APPS:
    _prefix = settings.ADMIN_URL.strip("/")
    urlpatterns += [
        re_path(r"^%s/doc/" % _prefix, include("django.contrib.admindocs.urls")),
        re_path(r"^%s/" % _prefix, admin.site.urls),
    ]

# Django Auth.
if "django.contrib.auth" in settings.INSTALLED_APPS:
    urlpatterns += [
        re_path(r"^accounts/", include("django.contrib.auth.urls")),
    ]

# Django Debug Toolbar.
if "debug_toolbar" in settings.INSTALLED_APPS:
    import debug_toolbar

    urlpatterns += [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
    ]

# Auto-include `project` URLs if they are available
checked = []
for module in (
    os.environ.get("PROJECT_URLS"),
    "djangosite.urls",
    "project_urls",
):
    if module:
        checked.append("'%s'" % module)
        try:
            project_urlconf = import_module(module)
        except ImportError:
            continue
        break
else:
    raise ImproperlyConfigured(
        "No project urlconf found. Checked: " + ", ".join(checked)
    )
urlpatterns += [
    re_path(r"^", include(project_urlconf)),
]
