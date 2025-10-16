from django.contrib import admin
from .models import Company, CompanyAdmin as CompanyAdminModel, Driver, Truck, Destination, DeliveryTask, DriverUser
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']


@admin.register(CompanyAdminModel)
class CompanyAdminLink(admin.ModelAdmin):
    list_display = ['user', 'company']
    search_fields = ['user__username', 'company__name']
    ordering = ['company__name']



@admin.register(Driver)
class DriverAdmin(admin.ModelAdmin):
    """
    Admin configuration for Driver model with search and filters.
    """
    list_display = ['name', 'company', 'license_number', 'phone', 'experience_years', 'status', 'created_at']
    list_filter = ['company', 'status', 'experience_years', 'created_at']
    search_fields = ['name', 'license_number', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('company', 'name', 'phone', 'license_number')
        }),
        ('Professional Information', {
            'fields': ('experience_years', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'company_admin'):
            return qs.filter(company=request.user.company_admin.company)
        if hasattr(request.user, 'driver_user'):
            return qs.filter(pk=request.user.driver_user.driver_id)
        return qs.none()


@admin.register(Truck)
class TruckAdmin(admin.ModelAdmin):
    """
    Admin configuration for Truck model with search and filters.
    """
    list_display = ['plate_number', 'company', 'model', 'capacity_kg', 'fuel_type', 'current_status', 'created_at']
    list_filter = ['company', 'current_status', 'fuel_type', 'capacity_kg', 'created_at']
    search_fields = ['plate_number', 'model']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['plate_number']
    
    fieldsets = (
        ('Vehicle Information', {
            'fields': ('company', 'plate_number', 'model', 'capacity_kg', 'fuel_type')
        }),
        ('Status', {
            'fields': ('current_status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'company_admin'):
            return qs.filter(company=request.user.company_admin.company)
        if hasattr(request.user, 'driver_user'):
            return qs.filter(delivery_tasks__driver=request.user.driver_user.driver).distinct()
        return qs.none()


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    """
    Admin configuration for Destination model with search and filters.
    """
    list_display = ['name', 'company', 'address', 'latitude', 'longitude', 'created_at']
    list_filter = ['company', 'created_at']
    search_fields = ['name', 'address']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Location Information', {
            'fields': ('company', 'name', 'address')
        }),
        ('Coordinates', {
            'fields': ('latitude', 'longitude')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'company_admin'):
            return qs.filter(company=request.user.company_admin.company)
        if hasattr(request.user, 'driver_user'):
            return qs.filter(delivery_tasks__driver=request.user.driver_user.driver).distinct()
        return qs.none()


@admin.register(DeliveryTask)
class DeliveryTaskAdmin(admin.ModelAdmin):
    """
    Admin configuration for DeliveryTask model with search and filters.
    """
    list_display = ['id', 'company', 'product_name', 'driver', 'truck', 'product_weight', 'status', 'created_at']
    list_filter = ['company', 'status', 'created_at', 'driver', 'truck']
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
        qs = super().get_queryset(request).select_related('driver', 'truck').prefetch_related('destinations')
        if request.user.is_superuser:
            return qs
        if hasattr(request.user, 'company_admin'):
            return qs.filter(company=request.user.company_admin.company)
        if hasattr(request.user, 'driver_user'):
            return qs.filter(driver=request.user.driver_user.driver)
        return qs


@admin.register(DriverUser)
class DriverUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'driver']
    search_fields = ['user__username', 'driver__name']
    ordering = ['driver__name']
