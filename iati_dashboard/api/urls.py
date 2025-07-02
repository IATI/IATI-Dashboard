from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"reporting-orgs", views.ReportingOrgViewSet)
router.register(r"datasets", views.DatasetViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
