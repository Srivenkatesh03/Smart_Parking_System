"""
Flask Web Application for Smart Parking Management System
Provides RESTful API and web interface for parking monitoring
"""

import os
import cv2
import json
import threading
import time
from datetime import datetime
from flask import Flask, render_template, Response, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import numpy as np
from PIL import Image as PILImage
from models.parking_manager import ParkingManager
from models.database import db, ReferenceImage, ParkingSpaceGroup, init_db
from utils.resource_manager import ensure_directories_exist, load_parking_positions
from utils.media_paths import list_available_videos

# Optional ML detector import
try:
    from models.vehicle_detector import VehicleDetector
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML detector not available. Using basic detection only.")

app = Flask(__name__)
app.config['SECRET_KEY'] = 'smart-parking-secret-key-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize database
init_db(app)

# Initialize parking manager
config_dir = "config"
log_dir = "logs"
media_dir = "media"
references_dir = os.path.join(media_dir, "references")
ensure_directories_exist([config_dir, log_dir, media_dir, references_dir])
parking_manager = ParkingManager(config_dir=config_dir, log_dir=log_dir)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

# Global state
current_frame = None
frame_lock = threading.Lock()
detection_running = False
video_capture = None
current_video_source = None
stats_history = []
MAX_HISTORY = 100

# Detection parameters
parking_threshold = 500
use_ml_detection = False
ml_detector = None


def initialize_parking_data():
    """Initialize parking positions and data"""
    try:
        # Load parking positions from default reference
        reference_image = "carParkImg.png"
        positions = load_parking_positions(config_dir, reference_image)
        parking_manager.posList = positions
        parking_manager.total_spaces = len(positions)
        parking_manager.free_spaces = 0
        parking_manager.occupied_spaces = parking_manager.total_spaces
        
        # Initialize parking data structure
        parking_manager.parking_data = {}
        for i, (x, y, w, h) in enumerate(positions):
            space_id = f"S{i + 1}"
            section = "A" if x < 640 else "B"
            parking_manager.parking_data[f"{space_id}-{section}"] = {
                'position': (x, y, w, h),
                'occupied': True,
                'vehicle_id': None,
                'last_state_change': datetime.now().isoformat(),
                'section': section
            }
        
        print(f"Initialized {len(positions)} parking spaces")
        return True
    except Exception as e:
        print(f"Error initializing parking data: {e}")
        return False


def check_parking_space(img_processed, x, y, w, h):
    """Check if a parking space is occupied"""
    try:
        img_crop = img_processed[y:y + h, x:x + w]
        count = cv2.countNonZero(img_crop)
        return count < parking_threshold
    except Exception as e:
        print(f"Error checking parking space: {e}")
        return False


def detect_parking_spaces(frame):
    """Detect parking space occupancy in a frame"""
    global current_frame
    
    try:
        # Convert to grayscale and apply processing
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 1)
        img_threshold = cv2.adaptiveThreshold(
            img_blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 25, 16
        )
        img_median = cv2.medianBlur(img_threshold, 5)
        kernel = np.ones((3, 3), np.uint8)
        img_dilate = cv2.dilate(img_median, kernel, iterations=1)
        
        free_count = 0
        occupied_count = 0
        
        # Check each parking space
        for i, (x, y, w, h) in enumerate(parking_manager.posList):
            is_free = check_parking_space(img_dilate, x, y, w, h)
            
            # Draw rectangles on the frame
            color = (0, 255, 0) if is_free else (0, 0, 255)
            thickness = 2
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
            
            # Add space number
            cv2.putText(frame, f"{i+1}", (x + 5, y + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            if is_free:
                free_count += 1
            else:
                occupied_count += 1
            
            # Update parking data
            space_id = f"S{i + 1}"
            section = "A" if x < 640 else "B"
            full_id = f"{space_id}-{section}"
            if full_id in parking_manager.parking_data:
                parking_manager.parking_data[full_id]['occupied'] = not is_free
        
        # Update global counters
        parking_manager.free_spaces = free_count
        parking_manager.occupied_spaces = occupied_count
        
        # Add status text
        cv2.rectangle(frame, (0, 0), (250, 80), (0, 0, 0), -1)
        cv2.putText(frame, f"Total: {parking_manager.total_spaces}", (10, 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Free: {free_count}", (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Occupied: {occupied_count}", (10, 75),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        with frame_lock:
            current_frame = frame.copy()
        
        # Record stats periodically
        record_stats()
        
        return frame
        
    except Exception as e:
        print(f"Error in detect_parking_spaces: {e}")
        return frame


def record_stats():
    """Record current statistics to history"""
    global stats_history
    
    if len(stats_history) >= MAX_HISTORY:
        stats_history.pop(0)
    
    stats_history.append({
        'timestamp': datetime.now().isoformat(),
        'total': parking_manager.total_spaces,
        'free': parking_manager.free_spaces,
        'occupied': parking_manager.occupied_spaces,
        'occupancy_rate': (parking_manager.occupied_spaces / parking_manager.total_spaces * 100) 
                         if parking_manager.total_spaces > 0 else 0
    })


def detection_loop():
    """Main detection loop for video processing"""
    global video_capture, detection_running, current_video_source
    
    while detection_running:
        try:
            if video_capture is None or not video_capture.isOpened():
                time.sleep(1)
                continue
            
            success, frame = video_capture.read()
            
            if not success:
                # Loop video
                video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            
            # Resize frame if needed
            frame = cv2.resize(frame, (1280, 720))
            
            # Detect parking spaces
            frame = detect_parking_spaces(frame)
            
            # Emit update via SocketIO
            socketio.emit('parking_update', {
                'total': parking_manager.total_spaces,
                'free': parking_manager.free_spaces,
                'occupied': parking_manager.occupied_spaces,
                'timestamp': datetime.now().isoformat()
            })
            
            time.sleep(0.1)  # Control frame rate
            
        except Exception as e:
            print(f"Error in detection loop: {e}")
            time.sleep(1)


def generate_frames():
    """Generate video frames for streaming"""
    global current_frame
    
    while True:
        try:
            with frame_lock:
                if current_frame is None:
                    time.sleep(0.1)
                    continue
                
                frame = current_frame.copy()
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            
            # Yield frame in multipart format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        except Exception as e:
            print(f"Error generating frame: {e}")
            time.sleep(0.1)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Web Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/parking/status')
def get_parking_status():
    """Get current parking status"""
    try:
        spaces = []
        for space_id, data in parking_manager.parking_data.items():
            spaces.append({
                'id': space_id,
                'section': data['section'],
                'occupied': data['occupied'],
                'position': data['position']
            })
        
        return jsonify({
            'success': True,
            'total_spaces': parking_manager.total_spaces,
            'free_spaces': parking_manager.free_spaces,
            'occupied_spaces': parking_manager.occupied_spaces,
            'occupancy_rate': (parking_manager.occupied_spaces / parking_manager.total_spaces * 100)
                             if parking_manager.total_spaces > 0 else 0,
            'spaces': spaces,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/parking/stats')
def get_parking_stats():
    """Get parking statistics"""
    try:
        return jsonify({
            'success': True,
            'current': {
                'total': parking_manager.total_spaces,
                'free': parking_manager.free_spaces,
                'occupied': parking_manager.occupied_spaces,
                'occupancy_rate': (parking_manager.occupied_spaces / parking_manager.total_spaces * 100)
                                 if parking_manager.total_spaces > 0 else 0
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/parking/history')
def get_parking_history():
    """Get historical parking data"""
    try:
        return jsonify({
            'success': True,
            'history': stats_history,
            'count': len(stats_history)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/video/feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                   mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/video/sources')
def get_video_sources():
    """Get available video sources"""
    try:
        sources = list_available_videos()
        return jsonify({
            'success': True,
            'sources': sources
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/detection/start', methods=['POST'])
def start_detection():
    """Start parking detection"""
    global detection_running, video_capture, current_video_source
    
    try:
        data = request.json or {}
        video_source = data.get('video_source', 'media/carPark.mp4')
        
        if detection_running:
            return jsonify({
                'success': False,
                'error': 'Detection already running'
            }), 400
        
        # Initialize video capture
        if os.path.exists(video_source):
            video_capture = cv2.VideoCapture(video_source)
        else:
            video_capture = cv2.VideoCapture(0)  # Webcam fallback
        
        if not video_capture.isOpened():
            return jsonify({
                'success': False,
                'error': 'Failed to open video source'
            }), 500
        
        current_video_source = video_source
        detection_running = True
        
        # Start detection thread
        detection_thread = threading.Thread(target=detection_loop, daemon=True)
        detection_thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Detection started',
            'video_source': video_source
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/detection/stop', methods=['POST'])
def stop_detection():
    """Stop parking detection"""
    global detection_running, video_capture
    
    try:
        detection_running = False
        
        if video_capture is not None:
            video_capture.release()
            video_capture = None
        
        return jsonify({
            'success': True,
            'message': 'Detection stopped'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Reference Management Routes
@app.route('/references')
def references_view():
    """Reference images management page"""
    references = ReferenceImage.query.all()
    return render_template('references.html', references=references)


@app.route('/api/references/add', methods=['POST'])
def add_reference():
    """Add a new reference image"""
    try:
        name = request.form.get('name')
        width = request.form.get('width')
        height = request.form.get('height')
        video_source = request.form.get('video_source', '')
        
        if not name:
            return jsonify({'success': False, 'message': 'Name is required'}), 400
        
        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'message': 'Invalid file type. Allowed: jpg, jpeg, png, bmp'}), 400
        
        # Check if name already exists
        existing = ReferenceImage.query.filter_by(name=name).first()
        if existing:
            return jsonify({'success': False, 'message': 'Reference with this name already exists'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(references_dir, filename)
        file.save(filepath)
        
        # Get image dimensions if not provided
        if not width or not height:
            img = PILImage.open(filepath)
            width, height = img.size
        
        # Create database entry
        ref = ReferenceImage(
            name=name,
            filename=filename,
            width=int(width),
            height=int(height),
            video_source=video_source
        )
        db.session.add(ref)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Reference image "{name}" added successfully',
            'reference': ref.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/references/<int:ref_id>/delete', methods=['DELETE'])
def delete_reference(ref_id):
    """Delete a reference image"""
    try:
        ref = ReferenceImage.query.get_or_404(ref_id)
        
        # Delete file from disk
        filepath = os.path.join(references_dir, ref.filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        # Delete from database
        db.session.delete(ref)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Reference image deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/media/references/<filename>')
def serve_reference_image(filename):
    """Serve reference images"""
    return send_from_directory(references_dir, filename)


# Setup Page Routes
@app.route('/setup')
def setup_view():
    """Parking space setup page"""
    references = ReferenceImage.query.all()
    return render_template('setup.html', references=references)


@app.route('/api/groups/create', methods=['POST'])
def create_group():
    """Create a parking space group"""
    try:
        name = request.form.get('name')
        member_spaces_str = request.form.get('member_spaces')
        
        if not name:
            return jsonify({'success': False, 'message': 'Group name is required'}), 400
        
        if not member_spaces_str:
            return jsonify({'success': False, 'message': 'No spaces provided'}), 400
        
        member_spaces = json.loads(member_spaces_str)
        
        if len(member_spaces) < 2:
            return jsonify({'success': False, 'message': 'At least 2 spaces required for a group'}), 400
        
        # Generate unique group ID
        group_count = ParkingSpaceGroup.query.count()
        group_id = f"GROUP_{group_count + 1:03d}"
        
        # Create group
        group = ParkingSpaceGroup(
            group_id=group_id,
            name=name,
            member_spaces=json.dumps(member_spaces)
        )
        db.session.add(group)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Group "{name}" created with {len(member_spaces)} spaces',
            'group': group.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/setup/save', methods=['POST'])
def save_setup():
    """Save parking space layout"""
    try:
        spaces_str = request.form.get('spaces')
        reference_id = request.form.get('reference_id')
        
        if not spaces_str:
            return jsonify({'success': False, 'message': 'No spaces data provided'}), 400
        
        spaces = json.loads(spaces_str)
        
        # Save to config directory
        config_file = os.path.join(config_dir, 'parking_layout.json')
        with open(config_file, 'w') as f:
            json.dump({
                'spaces': spaces,
                'reference_id': reference_id,
                'updated_at': datetime.now().isoformat()
            }, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Saved {len(spaces)} parking spaces'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/setup/load', methods=['GET'])
def load_setup():
    """Load saved parking space layout"""
    try:
        config_file = os.path.join(config_dir, 'parking_layout.json')
        
        if not os.path.exists(config_file):
            return jsonify({'success': True, 'spaces': []})
        
        with open(config_file, 'r') as f:
            data = json.load(f)
        
        return jsonify({
            'success': True,
            'spaces': data.get('spaces', []),
            'reference_id': data.get('reference_id')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# SocketIO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('request_update')
def handle_update_request():
    """Handle update request from client"""
    emit('parking_update', {
        'total': parking_manager.total_spaces,
        'free': parking_manager.free_spaces,
        'occupied': parking_manager.occupied_spaces,
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    # Initialize parking data
    initialize_parking_data()
    
    print("=" * 50)
    print("Smart Parking Management System - Web Application")
    print("=" * 50)
    print(f"Server starting on http://localhost:5000")
    print(f"Parking spaces loaded: {parking_manager.total_spaces}")
    print("=" * 50)
    
    # Run the Flask app with SocketIO
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
