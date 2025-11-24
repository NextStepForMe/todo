# Production Setup Guide for Todo Application with CORS

This guide provides instructions for deploying the Todo application to production with CORS enabled for access from any domain.

## Prerequisites

- Python 3.8+
- pip
- Virtual environment (recommended)
- Database (PostgreSQL recommended for production)
- Web server (Nginx/Apache)
- WSGI server (Gunicorn)

## Development and Production Setup

### 1. CORS Configuration for Development and Production

The application is already configured for both development and production with CORS support. The CORS settings are included in both `core/settings.py` (development) and `core/settings_prod.py` (production) to allow access from any origin. The CORS settings are configured as follows in both settings files:


```python
# Application definition - adding CORS headers to installed apps
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'todo.apps.TodoConfig',
    'rest_framework',
    'channels',
    'corsheaders',  # Add CORS headers app
]

# Middleware - adding CORS middleware at the top
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # Add CORS middleware at the top
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# CORS settings for development/production
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins - change this to specific domains for better security in production

# Additional CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

## Production Setup

### 2. Environment Configuration

The application is already configured for production with CORS support. The production settings are in `core/settings_prod.py` which inherits the CORS configuration from the main settings file and includes additional production-specific settings. The CORS settings are configured to allow access from any origin for flexibility in production environments, but can be restricted to specific domains for enhanced security if needed.


### 3. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install production dependencies (includes django-cors-headers)
pip install -r requirements.txt
pip install gunicorn psycopg2-binary  # For PostgreSQL
```

### 4. Environment Variables

Create a `.env` file for environment variables in production (example values only - use secure values in production):

```bash
TODO_SECRET_KEY=your-very-secure-production-secret-key-here
TODO_DB_NAME=todo_db
TODO_DB_USER=todo_user
TODO_DB_PASSWORD=your-very-secure-password
TODO_DB_HOST=localhost
TODO_DB_PORT=5432
REDIS_HOST=localhost
DEBUG=False
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
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

#### Production with Gunicorn (Recommended for production):
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn using production settings
gunicorn core.wsgi:application --bind 0.0.0.0:8000 --env DJANGO_SETTINGS_MODULE=core.settings_prod
```

#### With Channels support (for real-time features) using Daphne:
```bash
# Install additional dependencies
pip install redis hiredis

# Run the ASGI server with production settings
daphne -b 0.0 -p 8000 core.asgi:application -e ssl:8443:privateKey=server.key:certKey=server.crt
```

### 6. Nginx Configuration

Create an Nginx configuration file to serve the application with proper headers for CORS support (if needed at the proxy level):

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # CORS headers (optional, since Django handles this)
    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
    
    # Handle preflight requests
    if ($request_method = 'OPTIONS') {
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, PATCH, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With";
        add_header Content-Length 0;
        add_header Content-Type text/plain;
        return 200;
    }
    
    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/project;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /path/to/your/project;
        expires 30d;
        add_header Cache-Control "public";
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

### 7. Systemd Service (Linux)

Create a systemd service file for auto-starting the application with production settings:

`/etc/systemd/system/todo.service`:
```ini
[Unit]
Description=Todo application with CORS support
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
EnvironmentFile=/path/to/your/project/.env
ExecStart=/path/to/your/venv/bin/gunicorn --workers 3 --bind unix:todo.sock -m 007 core.wsgi:application --env DJANGO_SETTINGS_MODULE=core.settings_prod
Restart=always
RestartSec=10

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

For HTTPS, use Let's Encrypt (required for production with modern browsers):

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 9. Backup Strategy

Create a backup script for regular backups of your data and media files:

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

# Log backup completion
echo "$(date): Backup completed" >> /path/to/backup.log
```

### 10. Monitoring and Logging

The production settings include comprehensive logging configuration for production monitoring. Log files will be created at the location specified in the production settings file. Monitor these logs for any issues with the application or CORS requests from different origins.


## CORS Configuration Details

The application is configured to allow cross-origin requests from any domain using django-cors-headers. This is important for API access from different domains. The key settings are in `core/settings_prod.py` and include CORS_ALLOW_ALL_ORIGINS = True which allows requests from any origin. For enhanced security in production, consider replacing this with specific allowed origins after deployment if you know the domains that will be accessing your API.


## Security Best Practices

1. **Never commit secrets to version control** - Use environment variables for sensitive data
2. **Use HTTPS in production** - Essential for security and required for modern browsers
3. **Set proper file permissions** - Ensure files have appropriate read/write permissions
4. **Regular security updates** - Keep Django and all packages updated
5. **Input validation and sanitization** - Already implemented in the application
6. **Rate limiting for APIs** - Consider implementing if needed for your use case
7. **Regular security audits** - Periodically review your security configuration
8. **CORS security** - Currently configured to allow all origins; consider restricting to specific domains for better security after deployment if appropriate

## Performance Optimization

1. **Database indexing** - Properly indexed database tables for faster queries
2. **Caching with Redis** - Implemented for session storage and real-time features
3. **CDN for static files** - Consider using a CDN for faster static file delivery
4. **Database connection pooling** - Configured in production settings
5. **Optimized queries** - Using select_related and prefetch_related where appropriate
6. **Image optimization** - Images are optimized for web delivery

## Troubleshooting

Common issues and solutions for production deployment with CORS support:

- **CORS errors**: Check that `django-cors-headers` is properly installed and configured in settings
- **Static files not loading**: Check `STATIC_ROOT` and run `collectstatic` command
- **Database connection errors**: Verify database credentials and network access in environment variables
- **Permission errors**: Check file permissions and user access rights for the web server user
- **Memory issues**: Adjust worker processes based on server resources in the Gunicorn configuration
- **API access errors**: Verify CORS settings in `core/settings_prod.py` and check that the application is running with production settings

## Scaling

For high-traffic applications with CORS requirements across multiple domains or services:

1. **Load balancing**: Use multiple application servers behind a load balancer
2. **Database read replicas**: Separate read/write operations for better performance
3. **Caching layer**: Implement Redis for frequently accessed data and session storage
4. **CDN**: Serve static assets from edge locations for faster access
5. **Database sharding**: For very large datasets when single database performance is insufficient