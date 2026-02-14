from django.contrib import admin
from .models import ParkingSpace, ParkingGroup, Vehicle, ReferenceImage, SystemLog, ParkingStatistics


@admin.register(ParkingSpace)
class ParkingSpaceAdmin(admin.ModelAdmin):
    list_display = ['space_id', 'section', 'is_occupied', 'reference_image', 'last_state_change']
    list_filter = ['is_occupied', 'section', 'reference_image']
    search_fields = ['space_id', 'vehicle_id']


@admin.register(ParkingGroup)
class ParkingGroupAdmin(admin.ModelAdmin):
    list_display = ['group_id', 'name', 'is_occupied', 'section', 'created_at']
    list_filter = ['is_occupied', 'section']
    search_fields = ['group_id', 'name']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_id', 'vehicle_type', 'entry_time', 'exit_time', 'is_active']
    list_filter = ['vehicle_type', 'is_active']
    search_fields = ['vehicle_id']


@admin.register(ReferenceImage)
class ReferenceImageAdmin(admin.ModelAdmin):
    list_display = ['name', 'width', 'height', 'video_source', 'created_at']
    search_fields = ['name', 'video_source']


@admin.register(SystemLog)
class SystemLogAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'level', 'category', 'message']
    list_filter = ['level', 'category']
    search_fields = ['message']
    readonly_fields = ['timestamp']


@admin.register(ParkingStatistics)
class ParkingStatisticsAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'total_spaces', 'free_spaces', 'occupied_spaces', 'occupancy_rate']
    readonly_fields = ['timestamp', 'occupancy_rate']

