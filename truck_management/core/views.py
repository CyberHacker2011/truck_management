from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Driver, Truck, Destination, DeliveryTask
from .serializers import (
    DriverSerializer, TruckSerializer, DestinationSerializer, 
    DeliveryTaskSerializer, TaskAssignmentSerializer
)
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
    
    def get_queryset(self):
        """
        Filter drivers by status if provided.
        """
        queryset = Driver.objects.all()
        status_filter = self.request.query_params.get('status', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get all available drivers.
        """
        available_drivers = Driver.objects.filter(status='available')
        serializer = self.get_serializer(available_drivers, many=True)
        return Response(serializer.data)


class TruckViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Truck CRUD operations.
    """
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    
    def get_queryset(self):
        """
        Filter trucks by status if provided.
        """
        queryset = Truck.objects.all()
        status_filter = self.request.query_params.get('status', None)
        fuel_type_filter = self.request.query_params.get('fuel_type', None)
        
        if status_filter:
            queryset = queryset.filter(current_status=status_filter)
        
        if fuel_type_filter:
            queryset = queryset.filter(fuel_type=fuel_type_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Get all available trucks.
        """
        available_trucks = Truck.objects.filter(current_status='idle')
        serializer = self.get_serializer(available_trucks, many=True)
        return Response(serializer.data)


class DestinationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Destination CRUD operations.
    """
    queryset = Destination.objects.all()
    serializer_class = DestinationSerializer
    
    def get_queryset(self):
        """
        Search destinations by name or address.
        """
        queryset = Destination.objects.all()
        search = self.request.query_params.get('search', None)
        
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(address__icontains=search)
            )
        
        return queryset


class DeliveryTaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DeliveryTask CRUD operations.
    """
    queryset = DeliveryTask.objects.select_related('driver', 'truck').prefetch_related('destinations')
    serializer_class = DeliveryTaskSerializer
    
    def get_queryset(self):
        """
        Filter tasks by status, driver, or truck if provided.
        """
        queryset = DeliveryTask.objects.select_related('driver', 'truck').prefetch_related('destinations')
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
    
    @action(detail=False, methods=['post'])
    def assign(self, request):
        """
        Assign a new delivery task to a driver and truck.
        """
        serializer = TaskAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            # Create the delivery task
            task_data = {
                'driver_id': serializer.validated_data['driver_id'],
                'truck_id': serializer.validated_data['truck_id'],
                'product_name': serializer.validated_data['product_name'],
                'product_weight': serializer.validated_data['product_weight'],
                'status': 'assigned'
            }
            
            task = DeliveryTask.objects.create(**task_data)
            
            # Add destinations
            destination_ids = serializer.validated_data['destination_ids']
            destinations = Destination.objects.filter(id__in=destination_ids)
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
