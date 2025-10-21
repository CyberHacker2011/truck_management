from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
class Company(models.Model):
    """
    Represents a tenant/company. All core data is scoped to a company.
    """
    name = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class CompanyAdmin(models.Model):
    """
    Role linking a Django user to a company admin.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_admin')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='admins')

    def __str__(self):
        return f"Admin {self.user.username} @ {self.company.name}"


class DriverUser(models.Model):
    """
    Role linking a Django user to a specific driver.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_user')
    driver = models.OneToOneField('Driver', on_delete=models.CASCADE, related_name='user_account')

    def __str__(self):
        return f"DriverUser {self.user.username} -> {self.driver.name}"


class Driver(models.Model):
    """
    Driver model representing truck drivers in the logistics system.
    """
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('on_mission', 'On Mission'),
    ]
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='drivers')
    name = models.CharField(max_length=100, help_text="Driver's full name")
    phone = models.CharField(max_length=20, help_text="Driver's contact phone number")
    license_number = models.CharField(
        max_length=50,
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
        constraints = [
            models.UniqueConstraint(fields=['company', 'license_number'], name='uniq_driver_company_license')
        ]
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
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='trucks')
    plate_number = models.CharField(
        max_length=20,
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
        constraints = [
            models.UniqueConstraint(fields=['company', 'plate_number'], name='uniq_truck_company_plate')
        ]
        verbose_name = 'Truck'
        verbose_name_plural = 'Trucks'
    
    def __str__(self):
        return f"{self.model} ({self.plate_number})"


class Destination(models.Model):
    """
    Destination model representing delivery locations.
    """
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='destinations')
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
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='delivery_tasks')
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
    # Stores full Yandex route JSON (coordinates, distance, duration)
    route_data = models.JSONField(null=True, blank=True)
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
        # Only update status if this is a new task or status is changing
        is_new = self.pk is None
        status_changed = False
        
        if not is_new:
            try:
                old_task = DeliveryTask.objects.get(pk=self.pk)
                status_changed = old_task.status != self.status
            except DeliveryTask.DoesNotExist:
                status_changed = True
        
        if is_new or status_changed:
            if self.status == 'assigned':
                # Only update if driver and truck are available
                if self.driver.status == 'available' and self.truck.current_status == 'idle':
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
