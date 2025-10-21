from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Company, Driver, Truck, Destination, DeliveryTask, CompanyAdmin, DriverUser
from .serializers import (
    CompanySerializer, DriverSerializer, TruckSerializer, DestinationSerializer, 
    DeliveryTaskSerializer, TaskAssignmentSerializer
)
from .services.openroute_service import OpenRouteService
def get_user_company(request):
    user = request.user
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return None
    if hasattr(user, 'company_admin'):
        return user.company_admin.company
    if hasattr(user, 'driver_user'):
        return user.driver_user.driver.company
    return None


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAdminUser]

from .maps_utils import (
    calculate_route_google_maps, calculate_route_yandex_maps,
    optimize_delivery_route, get_geocoding_info, reverse_geocoding
)


class DriverViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Driver CRUD operations.
    """
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter drivers by status if provided.
        """
        user_company = get_user_company(self.request)
        queryset = Driver.objects.all()
        if user_company:
            queryset = queryset.filter(company=user_company)
        status_filter = self.request.query_params.get('status', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

    def perform_create(self, serializer):
        user_company = get_user_company(self.request)
        if not (self.request.user.is_superuser or hasattr(self.request.user, 'company_admin')):
            raise permissions.PermissionDenied('Only company admins can create drivers')
        serializer.save(company=user_company)

    def perform_update(self, serializer):
        user_company = get_user_company(self.request)
        instance = self.get_object()
        if not (self.request.user.is_superuser or (hasattr(self.request.user, 'company_admin') and instance.company_id == user_company.id)):
            raise permissions.PermissionDenied('Not allowed')
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get all available drivers.
        """
        user_company = get_user_company(request)
        available_drivers = Driver.objects.filter(status='available')
        if user_company:
            available_drivers = available_drivers.filter(company=user_company)
        serializer = self.get_serializer(available_drivers, many=True)
        return Response(serializer.data)


class TruckViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Truck CRUD operations.
    """
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter trucks by status if provided.
        """
        user_company = get_user_company(self.request)
        queryset = Truck.objects.all()
        if user_company:
            queryset = queryset.filter(company=user_company)
        status_filter = self.request.query_params.get('status', None)
        fuel_type_filter = self.request.query_params.get('fuel_type', None)
        
        if status_filter:
            queryset = queryset.filter(current_status=status_filter)
        
        if fuel_type_filter:
            queryset = queryset.filter(fuel_type=fuel_type_filter)
        
        return queryset

    def perform_create(self, serializer):
        user_company = get_user_company(self.request)
        if not (self.request.user.is_superuser or hasattr(self.request.user, 'company_admin')):
            raise permissions.PermissionDenied('Only company admins can create trucks')
        serializer.save(company=user_company)

    def perform_update(self, serializer):
        user_company = get_user_company(self.request)
        instance = self.get_object()
        if not (self.request.user.is_superuser or (hasattr(self.request.user, 'company_admin') and instance.company_id == user_company.id)):
            raise permissions.PermissionDenied('Not allowed')
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get all available trucks.
        """
        user_company = get_user_company(request)
        available_trucks = Truck.objects.filter(current_status='idle')
        if user_company:
            available_trucks = available_trucks.filter(company=user_company)
        serializer = self.get_serializer(available_trucks, many=True)
        return Response(serializer.data)


class DestinationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Destination CRUD operations.
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Search destinations by name or address.
        """
        user_company = get_user_company(self.request)
        queryset = Destination.objects.all()
        if user_company:
            queryset = queryset.filter(company=user_company)
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(address__icontains=search)
            )
        
        return queryset

    def perform_create(self, serializer):
        user_company = get_user_company(self.request)
        if not (self.request.user.is_superuser or hasattr(self.request.user, 'company_admin')):
            raise permissions.PermissionDenied('Only company admins can create destinations')
        serializer.save(company=user_company)

    def perform_update(self, serializer):
        user_company = get_user_company(self.request)
        instance = self.get_object()
        if not (self.request.user.is_superuser or (hasattr(self.request.user, 'company_admin') and instance.company_id == user_company.id)):
            raise permissions.PermissionDenied('Not allowed')
        serializer.save()


class DeliveryTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DeliveryTask CRUD operations.
    """
    queryset = DeliveryTask.objects.select_related('driver', 'truck').prefetch_related('destinations')
    serializer_class = DeliveryTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Filter tasks by status, driver, or truck if provided.
        Drivers should only see their own tasks; company admins see their company's tasks.
        """
        queryset = DeliveryTask.objects.select_related('driver', 'truck').prefetch_related('destinations')
        # Drivers are scoped to their own tasks only
        if self.request.user.is_authenticated and hasattr(self.request.user, 'driver_user'):
            return queryset.filter(driver=self.request.user.driver_user.driver)
        # Company admins are scoped to their company
        user_company = get_user_company(self.request)
        if user_company:
            queryset = queryset.filter(company=user_company)
        status_filter = self.request.query_params.get('status', None)
        driver_filter = self.request.query_params.get('driver', None)
        truck_filter = self.request.query_params.get('truck', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if driver_filter:
            queryset = queryset.filter(driver_id=driver_filter)
        
        if truck_filter:
            queryset = queryset.filter(truck_id=truck_filter)
        
        return queryset

    def perform_create(self, serializer):
        user_company = get_user_company(self.request)
        if not (self.request.user.is_superuser or hasattr(self.request.user, 'company_admin')):
            raise permissions.PermissionDenied('Only company admins can create tasks')
        task = serializer.save(company=user_company)
        
        # Handle destinations if provided
        destination_ids = self.request.data.get('destination_ids', [])
        if destination_ids:
            destinations = Destination.objects.filter(
                id__in=destination_ids,
                company=user_company
            )
            task.destinations.set(destinations)
        
        # Generate route after creation if destinations exist
        destination_points = list(task.destinations.all())
        if destination_points:
            try:
                api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
                google_maps = OpenRouteService(api_key)
                coords = [(float(d.latitude), float(d.longitude)) for d in destination_points]
                route_json = google_maps.build_circular_route(coords)
                task.route_data = route_json
                task.save()
            except Exception as exc:
                # Keep task creation even if routing fails
                task.route_data = {
                    'error': 'routing_failed',
                    'message': str(exc)
                }
                task.save()


    def perform_update(self, serializer):
        """Ensure updates respect company scoping."""
        user_company = get_user_company(self.request)
        instance = self.get_object()
        if not (self.request.user.is_superuser or (hasattr(self.request.user, 'company_admin') and instance.company_id == (user_company.id if user_company else None))):
            raise permissions.PermissionDenied('Not allowed')
        serializer.save()

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def task_create_view(request):
    """
    Create a task, generate Yandex route, and save it.
    """
    user_company = get_user_company(request)
    if not (request.user.is_superuser or hasattr(request.user, 'company_admin')):
        return Response({'detail': 'Only company admins can create tasks'}, status=status.HTTP_403_FORBIDDEN)

    # Validate driver and truck belong to user's company
    driver_id = request.data.get('driver')
    truck_id = request.data.get('truck')
    if not driver_id or not truck_id:
        return Response({'detail': 'driver and truck are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        driver = Driver.objects.get(id=driver_id)
        truck = Truck.objects.get(id=truck_id)
    except (Driver.DoesNotExist, Truck.DoesNotExist):
        return Response({'detail': 'driver or truck not found'}, status=status.HTTP_400_BAD_REQUEST)

    if user_company and (driver.company_id != user_company.id or truck.company_id != user_company.id):
        return Response({'detail': 'Driver and truck must belong to your company'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = DeliveryTaskSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    task = serializer.save(company=user_company)

    destination_ids = request.data.get('destination_ids') or []
    if destination_ids:
        # Filter destinations by company to ensure security
        destinations = Destination.objects.filter(
            id__in=destination_ids,
            company=user_company
        )
        task.destinations.set(destinations)

    # Generate route
    destination_points = list(task.destinations.all())
    if destination_points:
        try:
            api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
            google_maps = OpenRouteService(api_key)
            coords = [(float(d.latitude), float(d.longitude)) for d in destination_points]
            route_json = google_maps.build_circular_route(coords)
            task.route_data = route_json
            task.save()
        except Exception as exc:
            task.route_data = {
                'error': 'routing_failed',
                'message': str(exc)
            }
            task.save()

    return Response(DeliveryTaskSerializer(task).data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def task_detail_view(request, pk: int):
    """
    Return full task info, including route_data, company-isolated.
    """
    user_company = get_user_company(request)
    qs = DeliveryTask.objects.select_related('driver', 'truck').prefetch_related('destinations')
    if user_company:
        qs = qs.filter(company=user_company)
    elif hasattr(request.user, 'driver_user'):
        qs = qs.filter(driver=request.user.driver_user.driver)

    task = get_object_or_404(qs, pk=pk)
    return Response(DeliveryTaskSerializer(task).data)

    def perform_update(self, serializer):
        user_company = get_user_company(self.request)
        instance = self.get_object()
        if not (self.request.user.is_superuser or (hasattr(self.request.user, 'company_admin') and instance.company_id == user_company.id)):
            raise permissions.PermissionDenied('Not allowed')
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def assign(self, request):
        """
        Assign a new delivery task to a driver and truck.
        """
        serializer = TaskAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            # Create the delivery task
            user_company = get_user_company(request)
            if user_company is None and not request.user.is_superuser:
                return Response({'error': 'Company context required'}, status=status.HTTP_403_FORBIDDEN)
            
            # Get driver and truck objects
            driver = Driver.objects.get(id=serializer.validated_data['driver_id'])
            truck = Truck.objects.get(id=serializer.validated_data['truck_id'])
            
            task = DeliveryTask.objects.create(
                company=user_company,
                driver=driver,
                truck=truck,
                product_name=serializer.validated_data['product_name'],
                product_weight=serializer.validated_data['product_weight'],
                status='assigned'
            )
            
            # Add destinations with company filtering
            destination_ids = serializer.validated_data['destination_ids']
            destinations = Destination.objects.filter(
                id__in=destination_ids,
                company=user_company
            )
            task.destinations.set(destinations)
            
            # Return the created task
            task_serializer = DeliveryTaskSerializer(task)
            return Response(task_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """
        Start a delivery task (change status to in_progress).
        """
        task = self.get_object()
        if task.status != 'assigned':
            return Response(
                {'error': 'Task must be in assigned status to start'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'in_progress'
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Complete a delivery task (change status to completed).
        """
        task = self.get_object()
        if task.status not in ['assigned', 'in_progress']:
            return Response(
                {'error': 'Task must be in assigned or in_progress status to complete'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        task.status = 'completed'
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get all active delivery tasks (assigned or in_progress).
        """
        active_tasks = self.get_queryset().filter(status__in=['assigned', 'in_progress'])
        serializer = self.get_serializer(active_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def optimize_route(self, request, pk=None):
        """
        Optimize delivery route for a task using maps API.
        """
        task = self.get_object()
        
        # Get task destinations
        destinations = task.destinations.all()
        if not destinations.exists():
            return Response(
                {'error': 'No destinations found for this task'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare coordinates for optimization
        destination_coords = [
            (dest.latitude, dest.longitude) for dest in destinations
        ]
        
        # Get API provider and key from request or settings
        api_provider = request.data.get('api_provider', 'google')
        api_key = request.data.get('api_key', None)
        
        try:
            # Optimize route
            optimized_route = optimize_delivery_route(
                start_location=(0, 0),  # You might want to get garage location
                delivery_locations=destination_coords,
                api_provider=api_provider,
                api_key=api_key
            )
            
            return Response(optimized_route)
            
        except Exception as e:
            return Response(
                {'error': f'Route optimization failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def calculate_route(self, request):
        """
        Calculate route between multiple destinations.
        """
        destinations = request.data.get('destinations', [])
        api_provider = request.data.get('api_provider', 'google')
        api_key = request.data.get('api_key', None)
        
        if not destinations:
            return Response(
                {'error': 'No destinations provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if api_provider == 'google':
                result = calculate_route_google_maps(
                    origin=(0, 0),  # You might want to get garage location
                    destinations=destinations,
                    api_key=api_key
                )
            elif api_provider == 'yandex':
                result = calculate_route_yandex_maps(
                    origin=(0, 0),  # You might want to get garage location
                    destinations=destinations,
                    api_key=api_key
                )
            else:
                return Response(
                    {'error': 'Invalid API provider. Use "google" or "yandex"'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': f'Route calculation failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def geocode_address(self, request):
        """
        Get coordinates for an address.
        """
        address = request.data.get('address')
        api_provider = request.data.get('api_provider', 'google')
        api_key = request.data.get('api_key', None)
        
        if not address:
            return Response(
                {'error': 'Address is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = get_geocoding_info(
                address=address,
                api_provider=api_provider,
                api_key=api_key
            )
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': f'Geocoding failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def reverse_geocode(self, request):
        """
        Get address for coordinates.
        """
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        api_provider = request.data.get('api_provider', 'google')
        api_key = request.data.get('api_key', None)
        
        if not latitude or not longitude:
            return Response(
                {'error': 'Latitude and longitude are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            result = reverse_geocoding(
                latitude=latitude,
                longitude=longitude,
                api_provider=api_provider,
                api_key=api_key
            )
            return Response(result)
            
        except Exception as e:
            return Response(
                {'error': f'Reverse geocoding failed: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
