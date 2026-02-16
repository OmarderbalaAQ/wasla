# Gunicorn Configuration for Production

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = 4  # 2 * CPU cores
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeouts
timeout = 30
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = "/var/log/wasla/access.log"
errorlog = "/var/log/wasla/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "wasla"

# Server mechanics
daemon = False
pidfile = "/var/run/wasla.pid"
user = "www-data"
group = "www-data"
tmp_upload_dir = None

# SSL (if terminating SSL at Gunicorn level instead of Nginx)
# keyfile = "/path/to/private.key"
# certfile = "/path/to/certificate.crt"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190