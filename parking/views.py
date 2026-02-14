from django.shortcuts import render, redirect
from django.http import JsonResponse, StreamingHttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json
import cv2
import base64
import numpy as np
from .models import ParkingSpace, ParkingGroup, Vehicle, SystemLog, ParkingStatistics
from .services import ParkingService


def index(request):
    """Main dashboard view"""
    # Get current parking status
    spaces = ParkingSpace.objects.all()
    total_spaces = spaces.count()
    occupied_spaces = spaces.filter(is_occupied=True).count()
    free_spaces = total_spaces - occupied_spaces
    
    # Get recent logs
    recent_logs = SystemLog.objects.all()[:10]
    
    # Get latest statistics
    latest_stats = ParkingStatistics.objects.first()
    
    context = {
        'total_spaces': total_spaces,
        'free_spaces': free_spaces,
        'occupied_spaces': occupied_spaces,
        'recent_logs': recent_logs,
        'latest_stats': latest_stats,
    }
    return render(request, 'parking/dashboard.html', context)


def setup_view(request):
    """Parking space setup view"""
    service = ParkingService()
    
    # Get available reference images
    reference_images = []
    config_dir = service.config_dir
    for filename in ['carParkImg.png', 'videoImg.png', 'saming1.png']:
        img_path = f'config/{filename}'
        if True:  # Simplified - would check if file exists
            reference_images.append(filename)
    
    context = {
        'reference_images': reference_images,
    }
    return render(request, 'parking/setup.html', context)


def logs_view(request):
    """System logs view"""
    logs = SystemLog.objects.all()[:100]
    context = {
        'logs': logs,
    }
    return render(request, 'parking/logs.html', context)


def statistics_view(request):
    """Statistics view"""
    stats = ParkingStatistics.objects.all()[:50]
    
    # Prepare data for charts
    chart_data = {
        'labels': [str(s.timestamp.strftime('%H:%M')) for s in reversed(stats)],
        'free_spaces': [s.free_spaces for s in reversed(stats)],
        'occupied_spaces': [s.occupied_spaces for s in reversed(stats)],
    }
    
    context = {
        'stats': stats,
        'chart_data': json.dumps(chart_data),
    }
    return render(request, 'parking/statistics.html', context)


def allocation_view(request):
    """Parking allocation view"""
    spaces = ParkingSpace.objects.all()
    groups = ParkingGroup.objects.all()
    
    context = {
        'spaces': spaces,
        'groups': groups,
    }
    return render(request, 'parking/allocation.html', context)


def references_view(request):
    """Reference images management view"""
    from .models import ReferenceImage
    references = ReferenceImage.objects.all()
    
    context = {
        'references': references,
    }
    return render(request, 'parking/references.html', context)


# API Views

@method_decorator(csrf_exempt, name='dispatch')
class SaveParkingSpacesView(View):
    """API endpoint to save parking spaces"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            reference_image = data.get('reference_image')
            positions = data.get('positions', [])
            
            service = ParkingService()
            
            # Convert positions to tuples
            pos_tuples = []
            for pos in positions:
                if isinstance(pos, dict):
                    pos_tuples.append((pos['x'], pos['y'], pos['w'], pos['h']))
                elif isinstance(pos, list):
                    pos_tuples.append(tuple(pos))
            
            # Save to file
            success = service.save_parking_positions(reference_image, pos_tuples)
            
            if success:
                # Sync to database
                service.sync_positions_to_database(reference_image, pos_tuples)
                return JsonResponse({'status': 'success', 'message': 'Parking spaces saved'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Failed to save'}, status=500)
                
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class LoadParkingSpacesView(View):
    """API endpoint to load parking spaces"""
    
    def get(self, request):
        try:
            reference_image = request.GET.get('reference_image', 'carParkImg.png')
            service = ParkingService()
            positions = service.load_parking_positions(reference_image)
            
            # Convert to list of dicts
            pos_list = []
            for x, y, w, h in positions:
                pos_list.append({'x': x, 'y': y, 'w': w, 'h': h})
            
            return JsonResponse({'status': 'success', 'positions': pos_list})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class ParkingStatusAPI(View):
    """API to get current parking status"""
    
    def get(self, request):
        spaces = ParkingSpace.objects.all()
        total = spaces.count()
        occupied = spaces.filter(is_occupied=True).count()
        free = total - occupied
        
        return JsonResponse({
            'total_spaces': total,
            'free_spaces': free,
            'occupied_spaces': occupied,
            'occupancy_rate': (occupied / total * 100) if total > 0 else 0
        })

