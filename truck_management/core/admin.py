from django.contrib import admin
from .models import Driver, Truck, Destination, DeliveryTask


@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """
    Admin configuration for Driver model with search and filters.
    """
    list_display = ['name', 'license_number', 'phone', 'experience_years', 'status', 'created_at']
    list_filter = ['status', 'experience_years', 'created_at']
    search_fields = ['name', 'license_number', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'phone', 'license_number')
        }),
        ('Professional Information', {
            'fields': ('experience_years', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    """
    Admin configuration for Truck model with search and filters.
    """
    list_display = ['plate_number', 'model', 'capacity_kg', 'fuel_type', 'current_status', 'created_at']
    list_filter = ['current_status', 'fuel_type', 'capacity_kg', 'created_at']
    search_fields = ['plate_number', 'model']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['plate_number']
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('plate_number', 'model', 'capacity_kg', 'fuel_type')
        }),
        ('Status', {
            'fields': ('current_status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    """
    Admin configuration for Destination model with search and filters.
    """
    list_display = ['name', 'address', 'latitude', 'longitude', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'address']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Location Information', {
            'fields': ('name', 'address')
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeliveryTask)
class DeliveryTaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for DeliveryTask model with search and filters.
    """
    list_display = ['id', 'product_name', 'driver', 'truck', 'product_weight', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'driver', 'truck']
    search_fields = ['product_name', 'driver__name', 'truck__plate_number']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    filter_horizontal = ['destinations']
    
    fieldsets = (
        ('Task Information', {
            'fields': ('product_name', 'product_weight', 'status')
        }),
        ('Assignment', {
            'fields': ('driver', 'truck', 'destinations')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """
        Optimize queryset by selecting related objects.
        """
        return super().get_queryset(request).select_related('driver', 'truck').prefetch_related('destinations')
