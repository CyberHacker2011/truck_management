from rest_framework import serializers
from .models import Company, Driver, Truck, Destination, DeliveryTask
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']



class DriverSerializer(serializers.ModelSerializer):
    """
    Serializer for Driver model with all fields and validation.
    """
    class Meta:
        model = Driver
        fields = [
            'id', 'company', 'name', 'phone', 'license_number', 
            'experience_years', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_license_number(self, value):
        """
        Validate that license number is unique.
        """
        company = self.initial_data.get('company') or getattr(self.instance, 'company_id', None)
        qs = Driver.objects.all()
        if company:
            qs = qs.filter(company_id=company)
        if qs.filter(license_number=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Driver with this license number already exists.")
        return value


class TruckSerializer(serializers.ModelSerializer):
    """
    Serializer for Truck model with all fields and validation.
    """
    class Meta:
        model = Truck
        fields = [
            'id', 'company', 'plate_number', 'model', 'capacity_kg', 
            'fuel_type', 'current_status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_plate_number(self, value):
        """
        Validate that plate number is unique.
        """
        company = self.initial_data.get('company') or getattr(self.instance, 'company_id', None)
        qs = Truck.objects.all()
        if company:
            qs = qs.filter(company_id=company)
        if qs.filter(plate_number=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Truck with this plate number already exists.")
        return value


class DestinationSerializer(serializers.ModelSerializer):
    """
    Serializer for Destination model with all fields and validation.
    """
    class Meta:
        model = Destination
        fields = [
            'id', 'company', 'name', 'address', 'latitude', 'longitude', 
            'is_base_location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_latitude(self, value):
        """
        Validate latitude is within valid range.
        """
        if not -90 <= value <= 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value
    
    def validate_longitude(self, value):
        """
        Validate longitude is within valid range.
        """
        if not -180 <= value <= 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value


class DeliveryTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for DeliveryTask model with nested relationships.
    """
    driver_name = serializers.CharField(source='driver.name', read_only=True)
    truck_plate = serializers.CharField(source='truck.plate_number', read_only=True)
    destinations_list = DestinationSerializer(source='destinations', many=True, read_only=True)
    destination_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of destination IDs for this task"
    )
    
    class Meta:
        model = DeliveryTask
        fields = [
            'id', 'company', 'driver', 'truck', 'destinations', 'destination_ids',
            'driver_name', 'truck_plate', 'destinations_list',
            'product_name', 'product_weight', 'status', 'route_data', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'route_data', 'company']
    
    def validate(self, data):
        """
        Validate that driver and truck are available for assignment.
        """
        driver = data.get('driver')
        truck = data.get('truck')
        
        if driver and driver.status != 'available':
            raise serializers.ValidationError(
                f"Driver {driver.name} is not available (current status: {driver.status})"
            )
        
        if truck and truck.current_status != 'idle':
            raise serializers.ValidationError(
                f"Truck {truck.plate_number} is not available (current status: {truck.current_status})"
            )
        
        # Validate product weight doesn't exceed truck capacity
        product_weight = data.get('product_weight')
        if truck and product_weight and product_weight > truck.capacity_kg:
            raise serializers.ValidationError(
                f"Product weight ({product_weight}kg) exceeds truck capacity ({truck.capacity_kg}kg)"
            )
        
        return data
    
    def create(self, validated_data):
        """
        Create delivery task. Handle M2M destinations safely.
        """
        # Remove destination_ids from validated_data as it's handled in the view
        destination_ids = validated_data.pop('destination_ids', None)
        # Also pop 'destinations' to avoid passing M2M into create(**kwargs)
        destinations_m2m = validated_data.pop('destinations', None)
        task = DeliveryTask.objects.create(**validated_data)
        
        # If destinations provided as objects, set them
        if destinations_m2m is not None:
            task.destinations.set(destinations_m2m)
        
        # If destination_ids provided, set them (view may also handle this)
        if destination_ids:
            destinations = Destination.objects.filter(id__in=destination_ids)
            task.destinations.set(destinations)
        
        return task
    
    def update(self, instance, validated_data):
        """
        Update delivery task with destinations.
        """
        destination_ids = validated_data.pop('destination_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if destination_ids is not None:
            destinations = Destination.objects.filter(id__in=destination_ids)
            instance.destinations.set(destinations)
        
        return instance


class TaskAssignmentSerializer(serializers.Serializer):
    """
    Specialized serializer for task assignment endpoint.
    """
    driver_id = serializers.IntegerField()
    truck_id = serializers.IntegerField()
    destination_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of destination IDs (minimum 1 required)"
    )
    product_name = serializers.CharField(max_length=200)
    product_weight = serializers.IntegerField(min_value=1)
    
    def validate_driver_id(self, value):
        """
        Validate driver exists and is available.
        """
        try:
            driver = Driver.objects.get(id=value)
            if driver.status != 'available':
                raise serializers.ValidationError(
                    f"Driver {driver.name} is not available (current status: {driver.status})"
                )
            return value
        except Driver.DoesNotExist:
            raise serializers.ValidationError("Driver not found.")
    
    def validate_truck_id(self, value):
        """
        Validate truck exists and is available.
        """
        try:
            truck = Truck.objects.get(id=value)
            if truck.current_status != 'idle':
                raise serializers.ValidationError(
                    f"Truck {truck.plate_number} is not available (current status: {truck.current_status})"
                )
            return value
        except Truck.DoesNotExist:
            raise serializers.ValidationError("Truck not found.")
    
    def validate_destination_ids(self, value):
        """
        Validate all destinations exist.
        """
        if not value:
            raise serializers.ValidationError("At least one destination is required.")
        
        existing_destinations = Destination.objects.filter(id__in=value)
        if len(existing_destinations) != len(value):
            missing_ids = set(value) - set(existing_destinations.values_list('id', flat=True))
            raise serializers.ValidationError(f"Destinations not found: {list(missing_ids)}")
        
        return value
    
    def validate(self, data):
        """
        Validate product weight against truck capacity and company consistency.
        """
        truck_id = data.get('truck_id')
        driver_id = data.get('driver_id')
        product_weight = data.get('product_weight')
        
        if truck_id and product_weight:
            truck = Truck.objects.get(id=truck_id)
            if product_weight > truck.capacity_kg:
                raise serializers.ValidationError(
                    f"Product weight ({product_weight}kg) exceeds truck capacity ({truck.capacity_kg}kg)"
                )
        
        # Validate that driver and truck belong to the same company
        if driver_id and truck_id:
            driver = Driver.objects.get(id=driver_id)
            truck = Truck.objects.get(id=truck_id)
            if driver.company != truck.company:
                raise serializers.ValidationError(
                    "Driver and truck must belong to the same company"
                )
        
        return data
