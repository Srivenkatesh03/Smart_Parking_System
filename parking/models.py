from django.db import models
from django.utils import timezone


class ParkingSpace(models.Model):
    """Model for parking space configuration"""
    space_id = models.CharField(max_length=50, unique=True)
    x = models.IntegerField()
    y = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    section = models.CharField(max_length=10, default='A')
    reference_image = models.CharField(max_length=255)
    is_occupied = models.BooleanField(default=False)
    vehicle_id = models.CharField(max_length=100, null=True, blank=True)
    last_state_change = models.DateTimeField(auto_now=True)
    distance_to_entrance = models.IntegerField(default=0)
    in_group = models.BooleanField(default=False)
    group_id = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['space_id']

    def __str__(self):
        return f"{self.space_id} - {'Occupied' if self.is_occupied else 'Free'}"


class ParkingGroup(models.Model):
    """Model for grouped parking spaces"""
    group_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    member_spaces = models.JSONField(default=list)  # List of space indices
    is_occupied = models.BooleanField(default=False)
    section = models.CharField(max_length=10, default='G')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['group_id']

    def __str__(self):
        return f"Group {self.group_id} - {self.name}"


class Vehicle(models.Model):
    """Model for tracked vehicles"""
    vehicle_id = models.CharField(max_length=100, unique=True)
    vehicle_type = models.CharField(max_length=50, default='car')
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    parking_space = models.ForeignKey(
        ParkingSpace,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles'
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-entry_time']

    def __str__(self):
        return f"Vehicle {self.vehicle_id}"

    @property
    def duration(self):
        """Calculate parking duration"""
        if self.exit_time:
            return self.exit_time - self.entry_time
        return timezone.now() - self.entry_time


class ReferenceImage(models.Model):
    """Model for reference images and video mappings"""
    name = models.CharField(max_length=255, unique=True)
    image_path = models.CharField(max_length=500)
    width = models.IntegerField()
    height = models.IntegerField()
    video_source = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SystemLog(models.Model):
    """Model for system event logging"""
    LOG_LEVELS = [
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('DEBUG', 'Debug'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    level = models.CharField(max_length=10, choices=LOG_LEVELS, default='INFO')
    message = models.TextField()
    category = models.CharField(max_length=50, default='general')

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.timestamp}] {self.level}: {self.message[:50]}"


class ParkingStatistics(models.Model):
    """Model for parking statistics over time"""
    timestamp = models.DateTimeField(auto_now_add=True)
    total_spaces = models.IntegerField(default=0)
    free_spaces = models.IntegerField(default=0)
    occupied_spaces = models.IntegerField(default=0)
    vehicle_count = models.IntegerField(default=0)
    occupancy_rate = models.FloatField(default=0.0)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Parking Statistics'

    def __str__(self):
        return f"Stats at {self.timestamp}: {self.occupied_spaces}/{self.total_spaces}"

    def save(self, *args, **kwargs):
        """Calculate occupancy rate before saving"""
        if self.total_spaces > 0:
            self.occupancy_rate = (self.occupied_spaces / self.total_spaces) * 100
        super().save(*args, **kwargs)
