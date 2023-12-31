# Third Party Libraries
from rest_framework import routers

# Django Libraries
from django.urls import include, path

# App Modules
from .views import ManufacturerViewSet, PropellantViewSet, SupplierViewSet

# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r"suppliers", SupplierViewSet)
router.register(r"manufacturers", ManufacturerViewSet)
router.register(r"propellants", PropellantViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(router.urls)),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]
