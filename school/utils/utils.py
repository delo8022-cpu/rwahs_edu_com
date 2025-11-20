"""
Security utility functions for RWAHS project
Enhanced with comprehensive security features
"""

import logging
import time
import hashlib
import re
from django.core.cache import cache
from django.core.exceptions import SuspiciousOperation
from django.utils import timezone
from django.conf import settings
from django.db.models import Count 

from .models import SecurityLog

# Security: Setup logger
logger = logging.getLogger('school.security')

# ==================== ENHANCED SECURITY UTILITIES ====================

def get_client_ip(request):
    """
    Get the real client IP address with security validation
    """
    try:
        # Check multiple headers for IP (behind proxy/load balancer)
        ip_headers = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_CLIENT_IP',
            'REMOTE_ADDR'
        ]
        
        ip = None
        for header in ip_headers:
            if header in request.META:
                ip_candidate = request.META[header]
                if ip_candidate:
                    # Handle multiple IPs in X-Forwarded-For
                    if ',' in ip_candidate:
                        ip_candidate = ip_candidate.split(',')[0].strip()
                    
                    # Validate IP format
                    if is_valid_ip(ip_candidate):
                        ip = ip_candidate
                        break
        
        if not ip:
            ip = '0.0.0.0'  # Fallback
            
        return ip
        
    except Exception as e:
        logger.error(f"Error getting client IP: {str(e)}")
        return '0.0.0.0'

def is_valid_ip(ip):
    """
    Validate IP address format
    """
    ipv4_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
    ipv6_pattern = r'^[0-9a-fA-F:]+$'  # Simplified IPv6 pattern
    
    if re.match(ipv4_pattern, ip):
        # Validate IPv4 octets
        octets = ip.split('.')
        if len(octets) != 4:
            return False
        for octet in octets:
            if not octet.isdigit() or not (0 <= int(octet) <= 255):
                return False
        return True
    elif re.match(ipv6_pattern, ip):
        # Basic IPv6 validation
        return True
    else:
        return False

def log_security_event(request, action, details="", user_agent=None):
    """
    Enhanced security event logging with comprehensive tracking
    """
    try:
        user = request.user if request.user.is_authenticated else None
        ip_address = get_client_ip(request)
        
        if not user_agent:
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
        
        # Security: Sanitize details to prevent log injection
        sanitized_details = sanitize_log_entry(str(details))
        
        # Create security log entry
        SecurityLog.objects.create(
            user=user,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            details=sanitized_details
        )
        
        # Additional console logging for important events
        if action in ['login_failed', 'security_attempt', 'rate_limit_exceeded']:
            logger.warning(f"Security event: {action} - IP: {ip_address} - Details: {sanitized_details}")
        else:
            logger.info(f"Security event: {action} - IP: {ip_address} - User: {user}")
            
    except Exception as e:
        logger.error(f"Security log error: {str(e)}")
        # Fallback to console if database is unavailable
        print(f"SECURITY_LOG_ERROR: {str(e)}")

def sanitize_log_entry(entry):
    """
    Sanitize log entries to prevent log injection attacks
    """
    if not entry:
        return ""
    
    # Remove or escape potentially dangerous characters
    sanitized = re.sub(r'[\r\n\t]', ' ', entry)  # Remove newlines and tabs
    sanitized = re.sub(r'[<>]', '', sanitized)  # Remove HTML tags
    sanitized = sanitized.strip()
    sanitized = sanitized[:1000]  # Limit length
    
    return sanitized

def check_rate_limit(request, key_prefix, max_attempts=5, timeout=1800):
    """
    Enhanced rate limiting with IP-based and user-based tracking
    """
    try:
        ip = get_client_ip(request)
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        
        # Create separate keys for IP and user
        ip_key = f'rate_limit_{key_prefix}_ip_{ip}'
        user_key = f'rate_limit_{key_prefix}_user_{user_id}'
        
        ip_attempts = cache.get(ip_key, 0)
        user_attempts = cache.get(user_key, 0)
        
        # Check if either limit is exceeded
        if ip_attempts >= max_attempts or user_attempts >= max_attempts:
            # Log rate limit violation
            log_security_event(
                request, 
                'rate_limit_exceeded', 
                f'Rate limit exceeded for {key_prefix}. IP: {ip_attempts}, User: {user_attempts}'
            )
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Rate limit check error: {str(e)}")
        return False  # Fail open for availability

def increment_rate_limit(request, key_prefix, timeout=1800):
    """
    Increment rate limit counters for both IP and user
    """
    try:
        ip = get_client_ip(request)
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        
        ip_key = f'rate_limit_{key_prefix}_ip_{ip}'
        user_key = f'rate_limit_{key_prefix}_user_{user_id}'
        
        # Increment IP-based counter
        ip_attempts = cache.get(ip_key, 0)
        cache.set(ip_key, ip_attempts + 1, timeout)
        
        # Increment user-based counter (if authenticated)
        if request.user.is_authenticated:
            user_attempts = cache.get(user_key, 0)
            cache.set(user_key, user_attempts + 1, timeout)
            
    except Exception as e:
        logger.error(f"Rate limit increment error: {str(e)}")

def clear_rate_limit(request, key_prefix):
    """
    Clear rate limit counters (useful for testing or manual reset)
    """
    try:
        ip = get_client_ip(request)
        user_id = request.user.id if request.user.is_authenticated else 'anonymous'
        
        ip_key = f'rate_limit_{key_prefix}_ip_{ip}'
        user_key = f'rate_limit_{key_prefix}_user_{user_id}'
        
        cache.delete(ip_key)
        cache.delete(user_key)
        
    except Exception as e:
        logger.error(f"Rate limit clear error: {str(e)}")

# ==================== INPUT VALIDATION UTILITIES ====================

def validate_file_upload(file, allowed_extensions=None, max_size=5242880):
    """
    Comprehensive file upload validation
    """
    if allowed_extensions is None:
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg']
    
    errors = []
    
    # Check file size
    if file.size > max_size:
        errors.append(f'ফাইলের সাইজ {max_size//1024//1024}MB এর বেশি হতে পারবে না')
    
    # Check file extension
    file_extension = '.' + file.name.split('.')[-1].lower() if '.' in file.name else ''
    if file_extension not in allowed_extensions:
        errors.append(f'ফাইল এক্সটেনশন {file_extension} অনুমোদিত নয়')
    
    # Check for potential malicious filenames
    if any(char in file.name for char in ['/', '\\', '..', ';', '|', '&', '`', '$']):
        errors.append('ফাইলের নামে অবৈধ ক্যারেক্টার রয়েছে')
    
    # Check for empty file
    if file.size == 0:
        errors.append('ফাইলটি খালি')
    
    return errors

def sanitize_filename(filename):
    """
    Sanitize filename to prevent path traversal attacks
    """
    if not filename:
        return "file"
    
    # Remove path components
    filename = filename.split('/')[-1].split('\\')[-1]
    
    # Remove dangerous characters
    filename = re.sub(r'[^\w\s\.\-]', '', filename)
    
    # Limit length
    filename = filename[:100]
    
    return filename

def validate_integer_input(value, min_value=None, max_value=None):
    """
    Safe integer input validation
    """
    try:
        int_value = int(value)
        
        if min_value is not None and int_value < min_value:
            return False, f'মান {min_value} এর কম হতে পারবে না'
        
        if max_value is not None and int_value > max_value:
            return False, f'মান {max_value} এর বেশি হতে পারবে না'
        
        return True, int_value
        
    except (ValueError, TypeError):
        return False, 'অবৈধ সংখ্যা'

def validate_text_input(text, max_length=1000, allow_html=False):
    """
    Safe text input validation
    """
    if not text:
        return True, ""
    
    # Check length
    if len(text) > max_length:
        return False, f'টেক্সট {max_length} ক্যারেক্টারের বেশি হতে পারবে না'
    
    # Check for potential XSS attacks
    if not allow_html:
        xss_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'onload=',
            r'onerror=',
            r'onclick=',
            r'vbscript:',
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, 'টেক্সটে অবৈধ কন্টেন্ট রয়েছে'
    
    return True, text.strip()

# ==================== SECURITY MONITORING UTILITIES ====================

def get_security_stats(hours=24):
    """
    Get security statistics for the given time period
    """
    try:
        since = timezone.now() - timezone.timedelta(hours=hours)
        
        stats = {
            'total_events': SecurityLog.objects.filter(timestamp__gte=since).count(),
            'failed_logins': SecurityLog.objects.filter(
                action='login_failed', 
                timestamp__gte=since
            ).count(),
            'security_attempts': SecurityLog.objects.filter(
                action='security_attempt', 
                timestamp__gte=since
            ).count(),
            'suspicious_ips': list(SecurityLog.objects.filter(
                timestamp__gte=since
            ).values('ip_address').annotate(count=Count('ip_address')).order_by('-count')[:10]),
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Security stats error: {str(e)}")
        return {}

def is_suspicious_request(request):
    """
    Basic suspicious request detection
    """
    try:
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip = get_client_ip(request)
        
        # Check for common malicious user agents
        malicious_agents = [
            'sqlmap', 'nikto', 'metasploit', 'nmap', 
            'acunetix', 'nessus', 'w3af', 'zap'
        ]
        
        for agent in malicious_agents:
            if agent.lower() in user_agent.lower():
                log_security_event(request, 'security_attempt', f'Suspicious user agent: {user_agent}')
                return True
        
        # Check for suspicious URL patterns
        suspicious_paths = [
            '/admin/', '/phpmyadmin/', '/wp-admin/', '/.env',
            '/config.json', '/backup/', '/sql/', '/database/'
        ]
        
        for path in suspicious_paths:
            if path in request.path.lower():
                log_security_event(request, 'security_attempt', f'Suspicious path access: {request.path}')
                return True
        
        return False
        
    except Exception as e:
        logger.error(f"Suspicious request check error: {str(e)}")
        return False

# ==================== PASSWORD SECURITY UTILITIES ====================

def password_strength_check(password):
    """
    Check password strength
    """
    if not password:
        return False, "পাসওয়ার্ড প্রয়োজন"
    
    errors = []
    
    # Minimum length
    if len(password) < 8:
        errors.append("পাসওয়ার্ড অন্তত ৮ ক্যারেক্টার দীর্ঘ হতে হবে")
    
    # Check for common patterns
    common_passwords = ['password', '123456', 'admin', 'qwerty']
    if password.lower() in common_passwords:
        errors.append("পাসওয়ার্ডটি খুবই সাধারণ")
    
    # Complexity requirements
    if not re.search(r'[A-Z]', password):
        errors.append("পাসওয়ার্ডে অন্তত একটি বড় হাতের অক্ষর থাকতে হবে")
    if not re.search(r'[a-z]', password):
        errors.append("পাসওয়ার্ডে অন্তত একটি ছোট হাতের অক্ষর থাকতে হবে")
    if not re.search(r'[0-9]', password):
        errors.append("পাসওয়ার্ডে অন্তত একটি সংখ্যা থাকতে হবে")
    if not re.search(r'[^A-Za-z0-9]', password):
        errors.append("পাসওয়ার্ডে অন্তত একটি বিশেষ ক্যারেক্টার থাকতে হবে")
    
    if errors:
        return False, ", ".join(errors)
    
    return True, "পাসওয়ার্ড শক্তিশালী"

# ==================== SECURITY HEADERS UTILITIES ====================

def add_security_headers(response):
    """
    Add security headers to HTTP response
    """
    security_headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Referrer-Policy': 'strict-origin-when-cross-origin',
    }
    
    # Add CSP if not in debug mode
    if not settings.DEBUG:
        security_headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https:;"
        )
    
    for header, value in security_headers.items():
        response[header] = value
    
    return response