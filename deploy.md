# Deployment Guide for Advanced Todo Application

This guide provides instructions for deploying the Advanced Todo application to production.

## Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)
- Database (PostgreSQL recommended for production)
- Web server (Nginx/Apache)
- WSGI server (Gunicorn)

## Production Setup

### 1. Environment Configuration

Create a production settings file:

```bash
# Create production settings
cp core/settings.py core/settings_prod.py
```

Then update the production settings:

```python
# core/settings_prod.py
import os
from .settings import *

# Security settings
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com', 'localhost']

# Use environment variables for sensitive data
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration (PostgreSQL recommended)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'todo_db'),
        'USER': os.environ.get('DB_USER', 'todo_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Redis for Channels (if using real-time features)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(os.environ.get('REDIS_HOST', 'localhost'), 6379)],
        },
    },
}

# Static files (production)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (user uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### 2. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies
pip install -r requirements.txt
pip install gunicorn psycopg2-binary  # For PostgreSQL
```

### 3. Environment Variables

Create a `.env` file for environment variables:

```bash
SECRET_KEY=your-very-secure-secret-key
DB_NAME=todo_db
DB_USER=todo_user
DB_PASSWORD=your-secure-password
DB_HOST=localhost
DB_PORT=5432
REDIS_HOST=localhost
DEBUG=False
```

### 4. Database Setup

```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 5. Running the Application

#### Development Server (not for production):
```bash
python manage.py runserver
```

#### Production with Gunicorn:
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

#### With Channels support (for real-time features):
```bash
# Install additional dependencies
pip install redis hiredis

# Run the ASGI server
daphne -b 0.0.0 -p 8000 core.asgi:application
```

### 6. Nginx Configuration

Create an Nginx configuration file:

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/project;
        expires 30d;
    }
    
    location /media/ {
        root /path/to/your/project;
        expires 30d;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7. Systemd Service (Linux)

Create a systemd service file for auto-starting:

`/etc/systemd/system/todo.service`:
```ini
[Unit]
Description=Todo application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
EnvironmentFile=/path/to/your/project/.env
ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind unix:todo.sock -m 007 core.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable todo
sudo systemctl start todo
```

### 8. SSL Configuration

For HTTPS, use Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 9. Backup Strategy

Create a backup script:

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup database
pg_dump todo_db > $BACKUP_DIR/todo_db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/media_$DATE.tar.gz /path/to/media/

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 10. Monitoring and Logging

Add logging configuration to settings:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/path/to/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Security Best Practices

1. **Never commit secrets to version control**
2. **Use HTTPS in production**
3. **Set proper file permissions**
4. **Regular security updates**
5. **Input validation and sanitization**
6. **Rate limiting for APIs**
7. **Regular security audits**

## Performance Optimization

1. **Database indexing**
2. **Caching with Redis**
3. **CDN for static files**
4. **Database connection pooling**
5. **Optimized queries**
6. **Image optimization**

## Troubleshooting

Common issues and solutions:

- **Static files not loading**: Check `STATIC_ROOT` and run `collectstatic`
- **Database connection errors**: Verify database credentials and network access
- **Permission errors**: Check file permissions and user access rights
- **Memory issues**: Adjust worker processes based on server resources

## Scaling

For high-traffic applications:

1. **Load balancing**: Use multiple application servers
2. **Database read replicas**: Separate read/write operations
3. **Caching layer**: Implement Redis for frequently accessed data
4. **CDN**: Serve static assets from edge locations
5. **Database sharding**: For very large datasets