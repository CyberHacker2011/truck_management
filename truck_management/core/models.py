from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Driver(models.Model):
    """
    Driver model representing truck drivers in the logistics system.
    """
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_mission', 'On Mission'),
    ]
    
    name = models.CharField(max_length=100, help_text="Driver's full name")
    phone = models.CharField(max_length=20, help_text="Driver's contact phone number")
    license_number = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Driver's license number"
    )
    experience_years = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(50)],
        help_text="Years of driving experience"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='available',
        help_text="Current driver status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Driver'
        verbose_name_plural = 'Drivers'
    
    def __str__(self):
        return f"{self.name} ({self.license_number})"


class Truck(models.Model):
    """
    Truck model representing vehicles in the logistics fleet.
    """
    STATUS_CHOICES = [
        ('idle', 'Idle'),
        ('in_use', 'In Use'),
    ]
    
    FUEL_TYPE_CHOICES = [
        ('diesel', 'Diesel'),
        ('gasoline', 'Gasoline'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    ]
    
    plate_number = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Truck's license plate number"
    )
    model = models.CharField(max_length=100, help_text="Truck model and make")
    capacity_kg = models.PositiveIntegerField(
        help_text="Maximum cargo capacity in kilograms"
    )
    fuel_type = models.CharField(
        max_length=20, 
        choices=FUEL_TYPE_CHOICES, 
        default='diesel',
        help_text="Type of fuel used"
    )
    current_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='idle',
        help_text="Current truck status"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['plate_number']
        verbose_name = 'Truck'
        verbose_name_plural = 'Trucks'
    
    def __str__(self):
        return f"{self.model} ({self.plate_number})"


class Destination(models.Model):
    """
    Destination model representing delivery locations.
    """
    name = models.CharField(max_length=200, help_text="Destination name or business name")
    address = models.TextField(help_text="Full address of the destination")
    latitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        help_text="Latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        help_text="Longitude coordinate"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Destination'
        verbose_name_plural = 'Destinations'
    
    def __str__(self):
        return f"{self.name} - {self.address}"


class DeliveryTask(models.Model):
    """
    DeliveryTask model representing delivery assignments.
    """
    STATUS_CHOICES = [
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    driver = models.ForeignKey(
        Driver, 
        on_delete=models.CASCADE, 
        related_name='delivery_tasks',
        help_text="Driver assigned to this task"
    )
    truck = models.ForeignKey(
        Truck, 
        on_delete=models.CASCADE, 
        related_name='delivery_tasks',
        help_text="Truck assigned to this task"
    )
    destinations = models.ManyToManyField(
        Destination, 
        related_name='delivery_tasks',
        help_text="Destinations for this delivery task"
    )
    product_name = models.CharField(
        max_length=200, 
        help_text="Name of the product being delivered"
    )
    product_weight = models.PositiveIntegerField(
        help_text="Weight of the product in kilograms"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='assigned',
        help_text="Current status of the delivery task"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Delivery Task'
        verbose_name_plural = 'Delivery Tasks'
    
    def __str__(self):
        return f"Task {self.id}: {self.product_name} - {self.driver.name}"
    
    def save(self, *args, **kwargs):
        """
        Override save to update driver and truck status when task is assigned.
        """
        if self.status == 'assigned':
            self.driver.status = 'on_mission'
            self.driver.save()
            self.truck.current_status = 'in_use'
            self.truck.save()
        elif self.status == 'completed':
            self.driver.status = 'available'
            self.driver.save()
            self.truck.current_status = 'idle'
            self.truck.save()
        
        super().save(*args, **kwargs)
