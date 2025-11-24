from django.urls import include, path
from rest_framework import routers

from . import ckan_backwards_compatible, views

router = routers.DefaultRouter()
router.register(r"reporting-orgs", views.ReportingOrgViewSet)
router.register(r"datasets", views.DatasetViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("limited-ckan-compatible/", include(ckan_backwards_compatible.urlpatterns)),
]
