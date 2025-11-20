from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.views.defaults import page_not_found, server_error
from django.utils.decorators import method_decorator
from django.views import View
import logging

from .models import Notice, Result, Slider, Official, HomePageSection, BreakingNews
from .utils import log_security_event

# Security: Setup logger
logger = logging.getLogger('school')

# Security: Custom error handlers
def custom_404_view(request, exception=None):
    """Custom 404 page with logging"""
    log_security_event(request, 'security_event', f'404 Not Found: {request.path}')
    logger.warning(f'404 Not Found: {request.path} - IP: {get_client_ip(request)}')
    
    context = {
        'request_path': request.path,
        'error_code': 404,
        'error_message': 'পৃষ্ঠাটি পাওয়া যায়নি'
    }
    return render(request, 'errors/404.html', context, status=404)

def custom_500_view(request):
    """Custom 500 page with logging"""
    log_security_event(request, 'security_event', '500 Server Error')
    logger.error(f'500 Server Error - IP: {get_client_ip(request)}')
    
    context = {
        'error_code': 500,
        'error_message': 'সার্ভারে সমস্যা হয়েছে'
    }
    return render(request, 'errors/500.html', context, status=500)

def custom_403_view(request, exception=None):
    """Custom 403 page with logging"""
    log_security_event(request, 'security_event', f'403 Forbidden: {request.path}')
    logger.warning(f'403 Forbidden: {request.path} - IP: {get_client_ip(request)}')
    
    context = {
        'error_code': 403,
        'error_message': 'আপনার এই পৃষ্ঠা দেখার অনুমতি নেই'
    }
    return render(request, 'errors/403.html', context, status=403)

def custom_400_view(request, exception=None):
    """Custom 400 page with logging"""
    log_security_event(request, 'security_event', f'400 Bad Request: {request.path}')
    logger.warning(f'400 Bad Request: {request.path} - IP: {get_client_ip(request)}')
    
    context = {
        'error_code': 400,
        'error_message': 'অনুরোধটি সঠিক নয়'
    }
    return render(request, 'errors/400.html', context, status=400)

# Security: Utility function to get client IP
def get_client_ip(request):
    """Get client IP address with security headers consideration"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# Security: Input validation decorator
def validate_integer_param(view_func):
    """Decorator to validate integer parameters in URL"""
    def wrapper(request, *args, **kwargs):
        try:
            # Check if any parameter is expected to be integer
            for key, value in kwargs.items():
                if key in ['pk', 'id']:
                    int(value)  # Will raise ValueError if not integer
        except (ValueError, TypeError):
            log_security_event(request, 'security_attempt', f'Invalid parameter: {kwargs}')
            return custom_400_view(request)
        return view_func(request, *args, **kwargs)
    return wrapper

# Security: Rate limiting simulation (for basic protection)
def check_rate_limit(request, limit=100):
    """Basic rate limiting check"""
    # In production, use django-ratelimit package
    session_key = f'rate_limit_{get_client_ip(request)}'
    request_count = request.session.get(session_key, 0)
    
    if request_count > limit:
        log_security_event(request, 'rate_limit_exceeded', f'Rate limit exceeded: {request_count}')
        return True
    return False

# Main Views with Security Enhancements
@require_http_methods(["GET"])
@csrf_protect
def home(request):
    """Home page view with security measures"""
    
    # Basic rate limiting check
    if check_rate_limit(request):
        return custom_403_view(request)
    
    try:
        # Security: Only fetch active and limited records
        sliders = Slider.objects.filter(is_active=True).order_by('order')[:10]  # Limit to 10
        officials = Official.objects.all()[:6]  # Limit officials
        sections = HomePageSection.objects.filter(is_active=True).order_by('order')
        latest_notices = Notice.objects.filter(is_active=True).order_by('-published_date')[:5]
        breaking_news = BreakingNews.objects.filter(is_active=True).order_by('order')[:5]  # Limit breaking news
        
        # Security logging
        log_security_event(request, 'page_view', 'Home page accessed')
        logger.info(f'Home page accessed - IP: {get_client_ip(request)}')
        
        context = {
            'sliders': sliders,
            'officials': officials,
            'sections': sections,
            'latest_notices': latest_notices,
            'breaking_news': breaking_news,
        }
        
        return render(request, 'home.html', context)
        
    except Exception as e:
        # Security: Don't expose internal errors to users
        logger.error(f'Home page error: {str(e)} - IP: {get_client_ip(request)}')
        log_security_event(request, 'system_error', f'Home page error: {str(e)}')
        return custom_500_view(request)

@require_http_methods(["GET"])
@csrf_protect
def notice_list(request):
    """Notice list view with security"""
    
    if check_rate_limit(request):
        return custom_403_view(request)
    
    try:
        notices = Notice.objects.filter(is_active=True).order_by('-published_date')
        
        log_security_event(request, 'page_view', 'Notice list accessed')
        logger.info(f'Notice list accessed - IP: {get_client_ip(request)}')
        
        return render(request, 'notice_list.html', {'notices': notices})
        
    except Exception as e:
        logger.error(f'Notice list error: {str(e)} - IP: {get_client_ip(request)}')
        return custom_500_view(request)

@require_http_methods(["GET"])
@csrf_protect
@validate_integer_param
def notice_detail(request, pk):
    """Notice detail view with parameter validation"""
    
    if check_rate_limit(request):
        return custom_403_view(request)
    
    try:
        notice = get_object_or_404(Notice, pk=pk, is_active=True)
        
        log_security_event(request, 'page_view', f'Notice detail accessed: {notice.title}')
        logger.info(f'Notice detail accessed - ID: {pk} - IP: {get_client_ip(request)}')
        
        return render(request, 'notice_detail.html', {'notice': notice})
        
    except Notice.DoesNotExist:
        logger.warning(f'Notice not found - ID: {pk} - IP: {get_client_ip(request)}')
        return custom_404_view(request)
    except Exception as e:
        logger.error(f'Notice detail error: {str(e)} - IP: {get_client_ip(request)}')
        return custom_500_view(request)

@require_http_methods(["GET"])
@csrf_protect
def result_archive(request):
    """Result archive view with security"""
    
    if check_rate_limit(request):
        return custom_403_view(request)
    
    try:
        ssc_results = Result.objects.filter(exam_type='SSC', is_active=True).order_by('-year')
        hsc_results = Result.objects.filter(exam_type='HSC', is_active=True).order_by('-year')
        
        log_security_event(request, 'page_view', 'Result archive accessed')
        logger.info(f'Result archive accessed - IP: {get_client_ip(request)}')
        
        context = {
            'ssc_results': ssc_results,
            'hsc_results': hsc_results
        }
        
        return render(request, 'result_archive.html', context)
        
    except Exception as e:
        logger.error(f'Result archive error: {str(e)} - IP: {get_client_ip(request)}')
        return custom_500_view(request)

# Security: Additional secure views
@require_http_methods(["GET"])
@csrf_protect
def result_download(request, pk):
    """Secure result download view"""
    
    if check_rate_limit(request, limit=10):  # Lower limit for downloads
        return custom_403_view(request)
    
    try:
        result = get_object_or_404(Result, pk=pk, is_active=True)
        
        # Security: Check if file exists and is safe
        if not result.pdf_file:
            logger.warning(f'Result file missing - ID: {pk}')
            return custom_404_view(request)
        
        # Security: Log download attempts
        log_security_event(request, 'file_download', f'Result downloaded: {result.title}')
        logger.info(f'Result downloaded - ID: {pk} - IP: {get_client_ip(request)}')
        
        # Serve file (Django will handle security headers)
        response = HttpResponse(result.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{result.title}.pdf"'
        response['X-Content-Type-Options'] = 'nosniff'
        
        return response
        
    except Result.DoesNotExist:
        logger.warning(f'Result not found for download - ID: {pk}')
        return custom_404_view(request)
    except Exception as e:
        logger.error(f'Result download error: {str(e)} - IP: {get_client_ip(request)}')
        return custom_500_view(request)

# Security: Health check endpoint (for monitoring)
@require_http_methods(["GET"])
def health_check(request):
    """Simple health check endpoint"""
    return HttpResponse("OK", status=200, content_type="text/plain")

# Security: Class Based Views with additional protection
class SecureViewMixin:
    """Mixin for additional security in class-based views"""
    
    @method_decorator(csrf_protect)
    @method_decorator(validate_integer_param)
    def dispatch(self, request, *args, **kwargs):
        """Override dispatch for security checks"""
        if check_rate_limit(request):
            return custom_403_view(request)
        return super().dispatch(request, *args, **kwargs)

# Example of secure class-based view (for future use)
"""
class NoticeAPIView(SecureViewMixin, View):
    def get(self, request, *args, **kwargs):
        # API implementation with security
        pass
"""