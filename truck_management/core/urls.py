from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompanyViewSet, DriverViewSet, TruckViewSet, DestinationViewSet, DeliveryTaskViewSet
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'companies', CompanyViewSet)
router.register(r'drivers', DriverViewSet)
router.register(r'trucks', TruckViewSet)
router.register(r'destinations', DestinationViewSet)
router.register(r'delivery-tasks', DeliveryTaskViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
