# Smart Parking Management System

A comprehensive intelligent parking management system using Computer Vision (YOLO), Object Tracking (DeepSORT), and Machine Learning (XGBoost) for real-time parking space detection, monitoring, and optimization.

## 🚗 Features

### Core Functionality
- **Real-time Vehicle Detection**: Uses YOLOv8 for accurate vehicle detection
- **Object Tracking**: DeepSORT integration for vehicle tracking across frames
- **Parking Space Monitoring**: Automatic detection of parking slot occupancy
- **Predictive Analytics**: XGBoost-based prediction for parking availability
- **Space Allocation**: Intelligent parking space recommendation system

### Web Application
- **Modern Web Interface**: Responsive dashboard accessible via browser
- **Live Video Streaming**: Real-time parking lot video feed
- **Interactive Visualization**: Dynamic parking lot map with color-coded spaces
- **Real-time Updates**: Live parking status updates via WebSocket
- **Analytics Dashboard**: Charts and graphs for occupancy trends
- **Data Export**: Export parking statistics to CSV format
- **Dark/Light Theme**: Toggle between themes for better visibility
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices

### RESTful API
- Complete REST API for integration with other systems
- Real-time parking status endpoints
- Historical data access
- Video streaming capabilities

## 📋 Requirements

### System Requirements
- Python 3.8 or higher
- Webcam or video files for parking lot monitoring
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Python Dependencies
See `requirements.txt` for complete list. Main dependencies include:
- Flask (Web Framework)
- OpenCV (Computer Vision)
- PyTorch (Deep Learning)
- YOLOv8 (Object Detection)
- DeepSORT (Object Tracking)
- XGBoost (Predictive Analytics)
- Flask-SocketIO (Real-time Communication)

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Srivenkatesh03/Smart_Parking_System.git
cd Smart_Parking_System
```

### 2. Create Virtual Environment (Recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Download YOLO Weights (if not included)
The YOLOv8 weights (`yolov8n.pt`) should be in the root directory. If not, they will be downloaded automatically on first run.

## 🌐 Running the Web Application

### Start the Web Server
```bash
python web_app.py
```

The server will start on `http://localhost:5000`

### Access the Dashboard
Open your web browser and navigate to:
```
http://localhost:5000
```

### Using the Web Interface

1. **Start Detection**: Click the "Start Detection" button to begin monitoring
2. **View Live Feed**: Watch real-time video feed with parking space overlays
3. **Monitor Statistics**: View total, available, and occupied spaces in real-time
4. **Check Trends**: Analyze occupancy trends with interactive charts
5. **Export Data**: Download parking statistics as CSV reports
6. **Toggle Theme**: Switch between light and dark modes

## 🖥️ Running the Desktop Application

For the original Tkinter desktop interface:
```bash
python main.py
```

## 📡 API Documentation

### Endpoints

#### Get Parking Status
```http
GET /api/parking/status
```

Response:
```json
{
  "success": true,
  "total_spaces": 20,
  "free_spaces": 5,
  "occupied_spaces": 15,
  "occupancy_rate": 75.0,
  "spaces": [
    {
      "id": "S1-A",
      "section": "A",
      "occupied": true,
      "position": [60, 88, 115, 55]
    }
  ],
  "timestamp": "2024-02-14T10:30:00"
}
```

#### Get Statistics
```http
GET /api/parking/stats
```

#### Get Historical Data
```http
GET /api/parking/history
```

#### Start Detection
```http
POST /api/detection/start
Content-Type: application/json

{
  "video_source": "media/videos/carPark.mp4"
}
```

#### Stop Detection
```http
POST /api/detection/stop
```

#### Video Stream
```http
GET /api/video/feed
```

Returns MJPEG video stream.

#### Get Video Sources
```http
GET /api/video/sources
```

## 📁 Project Structure

```
Smart_Parking_System/
├── web_app.py              # Flask web application
├── main.py                 # Desktop application entry point
├── requirements.txt        # Python dependencies
├── config/                 # Configuration files
│   └── CarParkPos_*       # Parking position configurations
├── logs/                   # Application logs
├── media/
│   ├── videos/            # Video files for testing
│   └── references/        # Reference images
├── models/
│   ├── parking_manager.py # Core parking logic
│   ├── vehicle_detector.py # YOLO vehicle detection
│   ├── vehicle_tracker.py  # DeepSORT tracking
│   ├── allocation_engine.py # Space allocation
│   └── parking_visualizer.py # Visualization utilities
├── static/
│   ├── css/
│   │   └── style.css      # Web application styles
│   └── js/
│       └── app.js         # Frontend JavaScript
├── templates/
│   └── index.html         # Main web page
├── ui/                    # Desktop UI components
│   ├── app.py
│   ├── detection_tab.py
│   ├── setup_tab.py
│   └── ...
└── utils/                 # Utility functions
    ├── resource_manager.py
    ├── video_utils.py
    └── ...
```

## 🎯 Usage Examples

### Python API Integration
```python
import requests

# Get parking status
response = requests.get('http://localhost:5000/api/parking/status')
data = response.json()

print(f"Available spaces: {data['free_spaces']}")
print(f"Occupancy rate: {data['occupancy_rate']}%")

# Start detection
requests.post('http://localhost:5000/api/detection/start', 
              json={'video_source': 'media/videos/carPark.mp4'})
```

### JavaScript Integration
```javascript
// Fetch parking status
fetch('/api/parking/status')
  .then(response => response.json())
  .then(data => {
    console.log('Free spaces:', data.free_spaces);
    console.log('Occupancy:', data.occupancy_rate + '%');
  });

// WebSocket for real-time updates
const socket = io();
socket.on('parking_update', (data) => {
  console.log('Live update:', data);
});
```

## 🛠️ Configuration

### Parking Positions
Parking space positions are stored in `config/CarParkPos_*` files. Use the Setup tab in the desktop application to configure parking spaces for different video sources.

### Detection Parameters
Modify these parameters in `web_app.py`:
- `parking_threshold`: Pixel count threshold for occupancy detection
- `use_ml_detection`: Enable/disable ML-based detection
- `MAX_HISTORY`: Maximum history records to keep

## 🔧 Troubleshooting

### Port Already in Use
If port 5000 is already in use, modify the port in `web_app.py`:
```python
socketio.run(app, debug=True, host='0.0.0.0', port=5001)
```

### Video Not Loading
- Ensure video files are in `media/videos/` directory
- Check video file format (MP4 recommended)
- Verify file permissions

### Detection Not Working
- Ensure parking positions are configured (use desktop app Setup tab)
- Check that video resolution matches reference image
- Verify YOLO weights file (`yolov8n.pt`) exists

## 📊 Performance

- **Detection Speed**: ~10-30 FPS depending on hardware
- **Accuracy**: >95% for well-lit parking areas
- **Latency**: <100ms for real-time updates
- **Concurrent Users**: Supports multiple simultaneous web clients

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the MIT License.

## 👥 Authors

- Srivenkatesh03

## 🙏 Acknowledgments

- YOLOv8 by Ultralytics
- DeepSORT algorithm
- Flask web framework
- Bootstrap UI framework
- Chart.js for data visualization

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Note**: This system is designed for educational and research purposes. For production deployment, additional security measures and optimizations are recommended.