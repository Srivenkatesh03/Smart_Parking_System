# Smart Parking Management System - Django Web Application

This is a Django-based web application for managing and monitoring parking spaces using computer vision and machine learning.

## Features

- **Dashboard**: Real-time parking space monitoring and statistics
- **Parking Setup**: Interactive tool to draw and configure parking spaces on reference images
- **Detection**: Video-based parking space detection and vehicle counting
- **Logs**: System event logging and monitoring
- **Statistics**: Historical data and analytics with charts
- **Allocation**: Parking space allocation management
- **References**: Manage reference images for different parking areas

## Technology Stack

- **Backend**: Django 6.0.2, Python 3.12
- **Frontend**: Bootstrap 5, jQuery, Chart.js
- **Computer Vision**: OpenCV, YOLO (YOLOv8)
- **Database**: SQLite (default), can be configured for PostgreSQL/MySQL

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup Instructions

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/Srivenkatesh03/Smart_Parking_System.git
   cd Smart_Parking_System
   ```

2. **Install required packages**:
   ```bash
   pip install -r requirements_django.txt
   ```

   Or install manually:
   ```bash
   pip install Django djangorestframework Pillow opencv-python-headless numpy
   ```

3. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Create a superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin account.

5. **Collect static files** (for production):
   ```bash
   python manage.py collectstatic
   ```

## Running the Application

### Development Server

Start the Django development server:

```bash
python manage.py runserver
```

The application will be available at: `http://localhost:8000`

To run on a different port:
```bash
python manage.py runserver 8080
```

To allow external access:
```bash
python manage.py runserver 0.0.0.0:8000
```

### Accessing the Application

- **Main Dashboard**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Setup Page**: http://localhost:8000/setup/
- **Logs**: http://localhost:8000/logs/
- **Statistics**: http://localhost:8000/statistics/
- **Allocation**: http://localhost:8000/allocation/
- **References**: http://localhost:8000/references/

## Usage Guide

### 1. Configure Parking Spaces

1. Navigate to the **Setup** page
2. Select a reference image from the dropdown
3. Use your mouse to draw rectangles over parking spaces:
   - **Left-click and drag** to draw a new parking space
   - **Right-click** on a space to delete it
4. Click **Save Spaces** to persist your configuration

### 2. Monitor Parking Status

1. Go to the **Dashboard**
2. View real-time statistics:
   - Total parking spaces
   - Free spaces (green)
   - Occupied spaces (red)
3. Recent activity logs appear on the right side

### 3. View Statistics

1. Navigate to the **Statistics** page
2. View historical data with interactive charts
3. Analyze occupancy rates over time

### 4. Manage Allocation

1. Go to the **Allocation** page
2. View all parking spaces and their current status
3. See grouped parking spaces for larger vehicles

### 5. Check System Logs

1. Navigate to the **Logs** page
2. View all system events with timestamps
3. Filter by log level (INFO, WARNING, ERROR)

## Project Structure

```
Smart_Parking_System/
├── manage.py                 # Django management script
├── smart_parking_web/       # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── parking/                 # Main parking app
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # URL routing
│   ├── services.py         # Business logic
│   └── admin.py            # Admin configuration
├── templates/              # HTML templates
│   ├── base.html
│   └── parking/
│       ├── dashboard.html
│       ├── setup.html
│       ├── logs.html
│       ├── statistics.html
│       ├── allocation.html
│       └── references.html
├── static/                 # Static files
│   ├── css/
│   │   └── style.css
│   └── js/
├── media/                  # User uploaded files
├── config/                 # Parking configurations
├── models/                 # ML models (YOLO, etc.)
└── utils/                  # Utility functions
```

## Configuration

### Settings

Edit `smart_parking_web/settings.py` to customize:

- Database configuration
- Static/Media file paths
- Allowed hosts
- Debug mode

### Environment Variables

For production, set these environment variables:
```bash
export DJANGO_SECRET_KEY='your-secret-key'
export DJANGO_DEBUG=False
export DJANGO_ALLOWED_HOSTS='your-domain.com,www.your-domain.com'
```

## API Endpoints

The application provides REST API endpoints:

- `GET /api/status/` - Get current parking status
- `POST /api/save-spaces/` - Save parking space configuration
- `GET /api/load-spaces/` - Load parking space configuration

## Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   python manage.py runserver 8080
   ```

2. **Static files not loading**:
   ```bash
   python manage.py collectstatic --clear
   ```

3. **Database errors**:
   ```bash
   python manage.py migrate --run-syncdb
   ```

4. **Permission errors**:
   - Ensure the `media/` and `config/` directories are writable
   - Check file permissions: `chmod -R 755 media config`

## Migrating from Tkinter Version

The original Tkinter application has been fully migrated to this Django web application:

- All features have been preserved
- Hardware integration has been removed (software-only)
- The UI has been modernized with a responsive web interface
- Data persistence uses Django ORM and database

Original Tkinter files are still available in:
- `ui/` - Original UI components
- `main.py` - Original Tkinter entry point

## Development

### Running Tests

```bash
python manage.py test
```

### Creating New Apps

```bash
python manage.py startapp app_name
```

### Database Shell

```bash
python manage.py dbshell
```

### Python Shell with Django

```bash
python manage.py shell
```

## Production Deployment

For production deployment, consider:

1. Use a production-grade web server (Gunicorn, uWSGI)
2. Set up a reverse proxy (Nginx, Apache)
3. Use a production database (PostgreSQL, MySQL)
4. Enable HTTPS
5. Set DEBUG=False
6. Configure proper static file serving
7. Set up proper logging
8. Use environment variables for secrets

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn smart_parking_web.wsgi:application --bind 0.0.0.0:8000
```

## Contributing

This project is migrated from a Tkinter desktop application to a Django web application. Contributions are welcome!

## License

[Add your license here]

## Support

For issues, questions, or contributions, please visit:
https://github.com/Srivenkatesh03/Smart_Parking_System

---

**Note**: This is a software-only implementation. Hardware integration features from the original Tkinter version have been intentionally excluded.
