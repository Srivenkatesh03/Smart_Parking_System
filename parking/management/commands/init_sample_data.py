from django.core.management.base import BaseCommand
from parking.models import ParkingSpace, ReferenceImage, SystemLog, ParkingStatistics
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Initialize sample data for the Smart Parking System'

    def handle(self, *args, **options):
        self.stdout.write('Initializing sample data...')

        # Create reference images
        ref_images = [
            {'name': 'carParkImg.png', 'width': 1280, 'height': 720, 'video': 'carPark.mp4'},
            {'name': 'videoImg.png', 'width': 1280, 'height': 720, 'video': 'Video.mp4'},
            {'name': 'saming1.png', 'width': 1280, 'height': 720, 'video': 'sample5.mp4'},
        ]

        for img_data in ref_images:
            ReferenceImage.objects.get_or_create(
                name=img_data['name'],
                defaults={
                    'image_path': f'config/{img_data["name"]}',
                    'width': img_data['width'],
                    'height': img_data['height'],
                    'video_source': img_data['video']
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(ref_images)} reference images'))

        # Create sample parking spaces
        if ParkingSpace.objects.count() == 0:
            ref_image = 'carParkImg.png'
            
            # Create 20 sample parking spaces in a grid pattern
            space_width = 107
            space_height = 48
            start_x = 50
            start_y = 100
            spacing_x = 120
            spacing_y = 60
            
            spaces_per_row = 5
            total_spaces = 20
            
            for i in range(total_spaces):
                row = i // spaces_per_row
                col = i % spaces_per_row
                
                x = start_x + (col * spacing_x)
                y = start_y + (row * spacing_y)
                
                # Determine section based on position
                section = "A" if x < 640 else "B"
                section += "1" if y < 360 else "2"
                
                # Randomly set some spaces as occupied
                is_occupied = random.choice([True, False])
                
                ParkingSpace.objects.create(
                    space_id=f"S{i+1}-{section}",
                    x=x, y=y,
                    width=space_width,
                    height=space_height,
                    section=section,
                    reference_image=ref_image,
                    is_occupied=is_occupied,
                    distance_to_entrance=x + y
                )
            
            self.stdout.write(self.style.SUCCESS(f'Created {total_spaces} parking spaces'))

        # Create sample system logs
        log_messages = [
            ('INFO', 'System initialized successfully', 'system'),
            ('INFO', 'Parking spaces loaded from configuration', 'parking'),
            ('INFO', 'Video detection started', 'detection'),
            ('WARNING', 'High occupancy rate detected', 'parking'),
            ('INFO', 'Statistics recorded', 'statistics'),
            ('INFO', 'User accessed dashboard', 'system'),
            ('INFO', 'Parking space configuration saved', 'parking'),
            ('DEBUG', 'Frame processing completed', 'detection'),
        ]

        for level, message, category in log_messages:
            SystemLog.objects.create(
                level=level,
                message=message,
                category=category
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(log_messages)} log entries'))

        # Create sample statistics (last 24 hours, hourly)
        now = timezone.now()
        total_spaces = ParkingSpace.objects.count()
        
        for hour in range(24):
            timestamp = now - timedelta(hours=23-hour)
            occupied = random.randint(5, total_spaces - 2)
            free = total_spaces - occupied
            vehicle_count = random.randint(0, 15)
            
            ParkingStatistics.objects.create(
                timestamp=timestamp,
                total_spaces=total_spaces,
                free_spaces=free,
                occupied_spaces=occupied,
                vehicle_count=vehicle_count
            )

        self.stdout.write(self.style.SUCCESS('Created 24 hours of statistics data'))

        # Summary
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(self.style.SUCCESS('Sample data initialization complete!'))
        self.stdout.write(f'Total Parking Spaces: {ParkingSpace.objects.count()}')
        self.stdout.write(f'Reference Images: {ReferenceImage.objects.count()}')
        self.stdout.write(f'System Logs: {SystemLog.objects.count()}')
        self.stdout.write(f'Statistics Records: {ParkingStatistics.objects.count()}')
