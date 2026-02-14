# Quick Start Guide - Django Smart Parking System

## Installation and Setup

### 1. Install Dependencies
```bash
pip install -r requirements_django.txt
```

### 2. Run Database Migrations
```bash
python manage.py migrate
```

### 3. Initialize Sample Data (Optional but Recommended)
```bash
python manage.py init_sample_data
```

This will create:
- 20 parking spaces
- 3 reference images
- Sample system logs
- 24 hours of statistics data

### 4. Create Admin User (Optional)
```bash
python manage.py createsuperuser
```

### 5. Start the Development Server
```bash
python manage.py runserver
```

The application will be available at: http://localhost:8000

## Quick Tour

### Dashboard (http://localhost:8000/)
- View real-time parking statistics
- See free and occupied spaces
- Monitor recent system activity
- Access live detection controls

### Setup (http://localhost:8000/setup/)
- Draw parking spaces on reference images
- Left-click and drag to create spaces
- Right-click to delete spaces
- Save and load configurations

### Logs (http://localhost:8000/logs/)
- View all system events
- Filter by log level
- Auto-refreshes every 10 seconds

### Statistics (http://localhost:8000/statistics/)
- View occupancy charts over time
- Analyze historical data
- Track occupancy rates

### Allocation (http://localhost:8000/allocation/)
- View all parking spaces
- See real-time occupancy status
- Visual representation with color coding

### Admin Panel (http://localhost:8000/admin/)
- Manage all data models
- Configure system settings
- View and edit database records

## Features Migrated from Tkinter

✅ Dashboard with live statistics
✅ Interactive parking space setup
✅ System event logging
✅ Statistics and analytics
✅ Parking allocation management
✅ Reference image management
✅ OpenCV-based detection logic
✅ Database persistence
✅ Responsive web UI

## Key Differences from Tkinter Version

| Feature | Tkinter Version | Django Version |
|---------|----------------|----------------|
| Interface | Desktop GUI | Web-based |
| Access | Local only | Network accessible |
| Data Storage | Pickle files | SQLite database |
| Multi-user | No | Yes (via web) |
| Mobile Support | No | Yes (responsive) |
| Real-time Updates | Direct | API-based |

## Next Steps

1. Configure your parking spaces using the Setup page
2. Upload reference images to the `media/` directory
3. Customize the detection parameters in `parking/services.py`
4. Deploy to production using Gunicorn + Nginx

## Troubleshooting

**Problem**: Static files not loading
```bash
python manage.py collectstatic
```

**Problem**: Database errors
```bash
python manage.py migrate --run-syncdb
```

**Problem**: Port 8000 in use
```bash
python manage.py runserver 8080
```

## Support

For issues and questions, refer to:
- README_DJANGO.md - Full documentation
- Django documentation: https://docs.djangoproject.com/
- Project repository: https://github.com/Srivenkatesh03/Smart_Parking_System
