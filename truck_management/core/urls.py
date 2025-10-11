from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DriverViewSet, TruckViewSet, DestinationViewSet, DeliveryTaskViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'drivers', DriverViewSet)
router.register(r'trucks', TruckViewSet)
router.register(r'destinations', DestinationViewSet)
router.register(r'delivery-tasks', DeliveryTaskViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
