# CORS Production Configuration

## Current Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",  # Development
        "http://127.0.0.1:8000",  # Development
        "https://wasla.example.com",  # TODO: Replace with actual domain
        "https://api.wasla.example.com",  # TODO: Replace with actual API domain
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

## When You Get Your Domain

Replace the example domains with your actual domains:

```python
allow_origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com",
    "https://api.yourdomain.com",  # If API is on subdomain
],
```

## Security Benefits

- ✅ Blocks requests from unauthorized domains
- ✅ Prevents CSRF attacks from malicious sites
- ✅ Allows only specific HTTP methods
- ✅ Maintains development functionality

## Development vs Production

**Development:** Includes localhost origins for testing
**Production:** Only your actual domain(s)