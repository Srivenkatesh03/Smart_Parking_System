"""
Parking Service - Business logic for parking management
Adapts the existing ParkingManager for Django web application
"""
import os
import pickle
import cv2
import numpy as np
from datetime import datetime
from django.conf import settings
from .models import ParkingSpace, ParkingGroup, Vehicle, SystemLog, ParkingStatistics


class ParkingService:
    """Service layer for parking operations"""
    
    DEFAULT_THRESHOLD = 500
    MIN_CONTOUR_SIZE = 40
    
    def __init__(self):
        self.config_dir = os.path.join(settings.BASE_DIR, 'config')
        self.parking_threshold = self.DEFAULT_THRESHOLD
        self._ensure_directories_exist()
    
    def _ensure_directories_exist(self):
        """Ensure necessary directories exist"""
        os.makedirs(self.config_dir, exist_ok=True)
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
    
    def load_parking_positions(self, reference_image):
        """Load parking positions from file"""
        try:
            base_name = os.path.splitext(os.path.basename(reference_image))[0]
            pos_file = os.path.join(self.config_dir, f'CarParkPos_{base_name}')
            
            if os.path.exists(pos_file):
                with open(pos_file, 'rb') as f:
                    positions = pickle.load(f)
                
                # Validate positions
                valid_positions = []
                for pos in positions:
                    if isinstance(pos, tuple) and len(pos) == 4:
                        x, y, w, h = pos
                        if x >= 0 and y >= 0 and w > 0 and h > 0:
                            valid_positions.append(pos)
                
                return valid_positions
            return []
        except Exception as e:
            self.log_event('ERROR', f'Error loading parking positions: {str(e)}')
            return []
    
    def save_parking_positions(self, reference_image, positions):
        """Save parking positions to file"""
        try:
            base_name = os.path.splitext(os.path.basename(reference_image))[0]
            pos_file = os.path.join(self.config_dir, f'CarParkPos_{base_name}')
            
            # Remove existing file
            if os.path.exists(pos_file):
                os.remove(pos_file)
            
            # Save new positions
            with open(pos_file, 'wb') as f:
                pickle.dump(positions, f)
            
            return True
        except Exception as e:
            self.log_event('ERROR', f'Error saving parking positions: {str(e)}')
            return False
    
    def sync_positions_to_database(self, reference_image, positions):
        """Sync parking positions to database"""
        try:
            # Clear existing spaces for this reference
            ParkingSpace.objects.filter(reference_image=reference_image).delete()
            
            # Create new spaces
            for i, pos in enumerate(positions):
                if isinstance(pos, tuple) and len(pos) == 4:
                    x, y, w, h = pos
                    section = "A" if x < 640 else "B"
                    section += "1" if y < 360 else "2"
                    
                    ParkingSpace.objects.create(
                        space_id=f"S{i+1}-{section}",
                        x=x, y=y, width=w, height=h,
                        section=section,
                        reference_image=reference_image,
                        distance_to_entrance=x + y
                    )
            
            self.log_event('INFO', f'Synced {len(positions)} parking spaces to database')
            return True
        except Exception as e:
            self.log_event('ERROR', f'Error syncing positions to database: {str(e)}')
            return False
    
    def check_parking_spaces(self, frame, positions):
        """
        Process frame to check parking space occupancy
        Returns: (processed_frame, free_count, occupied_count)
        """
        try:
            # Preprocess frame
            imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
            imgThreshold = cv2.adaptiveThreshold(
                imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 25, 16
            )
            imgProcessed = cv2.medianBlur(imgThreshold, 5)
            kernel = np.ones((3, 3), np.uint8)
            imgProcessed = cv2.dilate(imgProcessed, kernel, iterations=1)
            
            # Check each parking space
            free_count = 0
            occupied_count = 0
            result_frame = frame.copy()
            
            for i, pos in enumerate(positions):
                if not isinstance(pos, tuple) or len(pos) != 4:
                    continue
                
                x, y, w, h = pos
                
                # Ensure within bounds
                if (y >= 0 and y + h < imgProcessed.shape[0] and
                    x >= 0 and x + w < imgProcessed.shape[1]):
                    
                    # Get crop and count pixels
                    img_crop = imgProcessed[y:y+h, x:x+w]
                    count = cv2.countNonZero(img_crop)
                    
                    # Determine if occupied
                    is_free = count < self.parking_threshold
                    if is_free:
                        color = (0, 255, 0)  # Green
                        free_count += 1
                    else:
                        color = (0, 0, 255)  # Red
                        occupied_count += 1
                    
                    # Draw rectangle
                    cv2.rectangle(result_frame, (x, y), (x+w, y+h), color, 2)
                    
                    # Add space number
                    cv2.putText(
                        result_frame, f"S{i+1}", (x+5, y+20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
                    )
            
            # Add summary text
            total = free_count + occupied_count
            cv2.putText(
                result_frame, f"Free: {free_count}/{total}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2
            )
            
            return result_frame, free_count, occupied_count
            
        except Exception as e:
            self.log_event('ERROR', f'Error checking parking spaces: {str(e)}')
            return frame, 0, 0
    
    def detect_vehicles(self, current_frame, prev_frame, line_height=400):
        """
        Detect and count vehicles crossing a line
        Returns: (processed_frame, vehicle_count)
        """
        try:
            # Get difference between frames
            d = cv2.absdiff(prev_frame, current_frame)
            grey = cv2.cvtColor(d, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(grey, (5, 5), 0)
            _, th = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
            dilated = cv2.dilate(th, np.ones((3, 3)))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
            closing = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)
            
            # Find contours
            contours, _ = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            
            result_frame = current_frame.copy()
            
            # Draw detection line
            if line_height >= result_frame.shape[0]:
                line_height = result_frame.shape[0] - 50
            cv2.line(result_frame, (0, line_height), 
                    (result_frame.shape[1], line_height), (0, 255, 0), 2)
            
            vehicle_count = 0
            for c in contours:
                (x, y, w, h) = cv2.boundingRect(c)
                if w >= self.MIN_CONTOUR_SIZE and h >= self.MIN_CONTOUR_SIZE:
                    cv2.rectangle(result_frame, (x-10, y-10), 
                                (x+w+10, y+h+10), (255, 0, 0), 2)
                    
                    # Check if crossing line
                    if abs(y - line_height) < 20:
                        vehicle_count += 1
            
            return result_frame, vehicle_count
            
        except Exception as e:
            self.log_event('ERROR', f'Error detecting vehicles: {str(e)}')
            return current_frame, 0
    
    def log_event(self, level, message, category='general'):
        """Log an event to the database"""
        try:
            SystemLog.objects.create(
                level=level,
                message=message,
                category=category
            )
        except Exception as e:
            print(f"Error logging event: {str(e)}")
    
    def record_statistics(self, total_spaces, free_spaces, occupied_spaces, vehicle_count):
        """Record parking statistics"""
        try:
            ParkingStatistics.objects.create(
                total_spaces=total_spaces,
                free_spaces=free_spaces,
                occupied_spaces=occupied_spaces,
                vehicle_count=vehicle_count
            )
        except Exception as e:
            self.log_event('ERROR', f'Error recording statistics: {str(e)}')
    
    def get_recent_logs(self, count=50):
        """Get recent system logs"""
        return SystemLog.objects.all()[:count]
    
    def get_statistics(self, limit=100):
        """Get recent statistics"""
        return ParkingStatistics.objects.all()[:limit]
    
    def update_space_occupancy(self, reference_image, positions, frame):
        """Update database with current occupancy status"""
        try:
            _, free_count, occupied_count = self.check_parking_spaces(frame, positions)
            
            # Update database
            spaces = ParkingSpace.objects.filter(reference_image=reference_image)
            for i, space in enumerate(spaces):
                if i < len(positions):
                    # Determine if this specific space is occupied
                    # This is simplified - in production, you'd track individual spaces
                    space.is_occupied = (i >= free_count)
                    space.save()
            
            return free_count, occupied_count
        except Exception as e:
            self.log_event('ERROR', f'Error updating space occupancy: {str(e)}')
            return 0, 0
