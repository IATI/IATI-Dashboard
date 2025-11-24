from django.urls import include, path, re_path
from django.views.generic import TemplateView

from iati_dashboard.api import ckan_backwards_compatible

urlpatterns = [
    path("", TemplateView.as_view(template_name="iatiregistry_org_notice.html")),
    re_path(r"([a-z]{2}/)?api/(3/)?action/", include(ckan_backwards_compatible.urlpatterns)),
]
