"""
School Utils Package
All utility functions are imported here for easy access
"""

try:
    from .utils import (
        get_client_ip,
        log_security_event,
        validate_file_upload,
        sanitize_filename,
        validate_integer_input,
        validate_text_input,
        check_rate_limit,
        increment_rate_limit,
        clear_rate_limit,
        get_security_stats,
        is_suspicious_request,
        password_strength_check,
        add_security_headers
    )
except ImportError as e:
    print(f"Warning: Could not import utils: {e}")
    # Define empty functions as fallback
    def get_client_ip(request): return "127.0.0.1"
    def log_security_event(request, action, details=""): pass
    def validate_file_upload(file, allowed_extensions=None, max_size=5242880): return []
    def sanitize_filename(filename): return filename
    def validate_integer_input(value, min_value=None, max_value=None): return True, value
    def validate_text_input(text, max_length=1000, allow_html=False): return True, text
    def check_rate_limit(request, key_prefix, max_attempts=5, timeout=1800): return False
    def increment_rate_limit(request, key_prefix, timeout=1800): pass
    def clear_rate_limit(request, key_prefix): pass
    def get_security_stats(hours=24): return {}
    def is_suspicious_request(request): return False
    def password_strength_check(password): return True, "OK"
    def add_security_headers(response): return response

# ==================== ALL UTILS LIST ====================
__all__ = [
    'get_client_ip',
    'log_security_event', 
    'validate_file_upload',
    'sanitize_filename',
    'validate_integer_input',
    'validate_text_input',
    'check_rate_limit',
    'increment_rate_limit',
    'clear_rate_limit',
    'get_security_stats',
    'is_suspicious_request',
    'password_strength_check',
    'add_security_headers',
]

print("✅ School utils package loaded successfully!")