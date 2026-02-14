# Deployment Guide

This guide provides instructions for deploying the Smart Parking Management System web application in various environments.

## Quick Start

### Using the Launch Scripts

#### Linux/Mac:
```bash
./run_web.sh
```

#### Windows:
```batch
run_web.bat
```

## Development Deployment

### Local Development Server

The Flask development server is suitable for testing and development:

```bash
python web_app.py
```

Access at: `http://localhost:5000`

**Note**: The development server is not suitable for production use.

## Production Deployment

### Option 1: Gunicorn (Linux/Mac)

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Start the server:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 --worker-class eventlet -t 120 web_app:app
```

Parameters:
- `-w 4`: 4 worker processes
- `-b 0.0.0.0:5000`: Bind to all interfaces on port 5000
- `--worker-class eventlet`: Use eventlet for WebSocket support
- `-t 120`: Timeout of 120 seconds

### Option 2: Waitress (Windows)

1. Install Waitress:
```bash
pip install waitress
```

2. Create `run_production.py`:
```python
from waitress import serve
from web_app import app

serve(app, host='0.0.0.0', port=5000, threads=4)
```

3. Run:
```bash
python run_production.py
```

### Option 3: Docker Deployment

1. Create `Dockerfile`:
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn eventlet

# Copy application files
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--worker-class", "eventlet", "-t", "120", "web_app:app"]
```

2. Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  parking-system:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./media:/app/media
    restart: unless-stopped
    environment:
      - FLASK_ENV=production
```

3. Build and run:
```bash
docker-compose up -d
```

## Nginx Reverse Proxy (Recommended for Production)

1. Install Nginx

2. Create Nginx configuration (`/etc/nginx/sites-available/parking-system`):
```nginx
upstream parking_backend {
    server 127.0.0.1:5000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://parking_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    location /static {
        alias /path/to/Smart_Parking_System/static;
        expires 30d;
    }
}
```

3. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/parking-system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## SSL/HTTPS Setup (Optional but Recommended)

### Using Let's Encrypt (Certbot):

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Systemd Service (Linux)

Create `/etc/systemd/system/parking-system.service`:

```ini
[Unit]
Description=Smart Parking Management System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/Smart_Parking_System
Environment="PATH=/path/to/Smart_Parking_System/venv/bin"
ExecStart=/path/to/Smart_Parking_System/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 --worker-class eventlet -t 120 web_app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable parking-system
sudo systemctl start parking-system
```

## Environment Variables

Configure these environment variables for production:

```bash
export FLASK_ENV=production
export SECRET_KEY=your-secret-key-here
export MAX_HISTORY=1000
```

## Performance Optimization

### 1. Enable Caching
Consider using Redis for caching frequent API responses:
```bash
pip install redis flask-caching
```

### 2. Video Optimization
- Use H.264 codec for video files
- Optimize resolution (1280x720 is usually sufficient)
- Consider using RTSP streams for IP cameras

### 3. Database (Optional)
For long-term data storage:
- Use SQLite for small deployments
- Use PostgreSQL/MySQL for larger deployments

### 4. Load Balancing
For high-traffic scenarios, use multiple instances behind a load balancer.

## Security Considerations

1. **Change Secret Key**: Update `SECRET_KEY` in `web_app.py`
2. **HTTPS Only**: Use SSL/TLS certificates
3. **Firewall**: Configure firewall rules to restrict access
4. **Authentication**: Implement user authentication for production
5. **CORS**: Restrict CORS origins in production
6. **Rate Limiting**: Implement rate limiting for API endpoints

## Monitoring

### Log Files
Logs are stored in the `logs/` directory. Monitor:
- Application logs
- Error logs
- Access logs (if using Nginx)

### System Monitoring
Consider using:
- Prometheus + Grafana for metrics
- ELK Stack for log aggregation
- Uptime monitoring services

## Backup

Regular backups should include:
1. Configuration files (`config/`)
2. Parking position data
3. Historical logs (if needed)
4. Media files (reference images)

## Troubleshooting

### Port Already in Use
```bash
lsof -ti:5000 | xargs kill -9
```

### Permission Denied
```bash
sudo chown -R $USER:$USER /path/to/Smart_Parking_System
```

### Video Feed Not Working
1. Check video file permissions
2. Verify OpenCV is installed correctly
3. Check available disk space
4. Review application logs

## Scaling

For handling more traffic:

1. **Horizontal Scaling**: Deploy multiple instances with a load balancer
2. **Caching**: Use Redis/Memcached for session and data caching
3. **CDN**: Use CDN for static assets
4. **Database**: Move to a dedicated database server
5. **Queue System**: Use Celery for background tasks

## Support

For issues or questions:
- Check the main README.md
- Review application logs
- Open an issue on GitHub

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Documentation](https://docs.docker.com/)
