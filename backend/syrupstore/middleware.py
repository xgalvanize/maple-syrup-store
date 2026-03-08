"""
Custom middleware for additional security headers
"""


class SecurityHeadersMiddleware:
    """
    Adds additional security headers to all responses.
    
    Headers added:
    - Permissions-Policy: Controls browser feature access
    - Referrer-Policy: Controls referrer information
    - X-Content-Type-Options: Prevents MIME sniffing
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Permissions Policy - restrict access to sensitive features
        response["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=(), "
            "magnetometer=(), "
            "gyroscope=(), "
            "accelerometer=()"
        )
        
        # Referrer Policy - protect user privacy
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Additional protection headers
        response["X-Content-Type-Options"] = "nosniff"
        
        return response
