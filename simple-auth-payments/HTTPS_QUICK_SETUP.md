# HTTPS Quick Setup Commands

## When You Have Your Domain and Server

### 1. Install Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx

# Install Gunicorn for production
pip install gunicorn
```

### 2. Configure Nginx
```bash
# Copy template and edit
sudo cp nginx.conf.template /etc/nginx/sites-available/wasla
sudo nano /etc/nginx/sites-available/wasla

# Replace 'yourdomain.com' with your actual domain
# Replace '/path/to/your/app' with actual path

# Enable site
sudo ln -s /etc/nginx/sites-available/wasla /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Get SSL Certificate
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

### 4. Setup FastAPI Service
```bash
# Create log directory
sudo mkdir -p /var/log/wasla
sudo chown www-data:www-data /var/log/wasla

# Copy and edit service file
sudo cp wasla.service /etc/systemd/system/
sudo nano /etc/systemd/system/wasla.service

# Update paths in the service file
# Start service
sudo systemctl daemon-reload
sudo systemctl enable wasla
sudo systemctl start wasla
```

### 5. Test Setup
```bash
# Check service status
sudo systemctl status wasla

# Test HTTPS
curl -I https://yourdomain.com

# Check SSL rating
# Visit: https://www.ssllabs.com/ssltest/
```

## Files to Update After Domain Purchase

1. **main.py** - Update CORS origins
2. **nginx.conf.template** - Replace yourdomain.com
3. **wasla.service** - Update file paths
4. **.env** - Add production environment variables

## Security Headers Added

- Strict-Transport-Security (HSTS)
- X-Content-Type-Options
- X-Frame-Options  
- X-XSS-Protection
- Referrer-Policy
- Content-Security-Policy