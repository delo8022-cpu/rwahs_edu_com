"""
School App URL Configuration
রূপসা ওয়াহেদ আলী উচ্চ বিদ্যালয় - URL কনফিগারেশন
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.defaults import page_not_found, server_error
from django.shortcuts import redirect
from django.http import HttpResponse

# Custom Admin Site Import
from school.admin import custom_admin_site

# Security: Custom error handlers
handler404 = 'school.views.custom_404_view'
handler500 = 'school.views.custom_500_view'
handler403 = 'school.views.custom_403_view'
handler400 = 'school.views.custom_400_view'

urlpatterns = [
    # Custom Admin Panel - Primary admin interface
    path('admin/', custom_admin_site.urls, name='admin'),
    
    # Default Admin Panel (ব্যাকআপ হিসেবে - Security redundancy)
    path('old-admin/', admin.site.urls, name='old_admin'),
    
    # Main App URLs
    path('', include('school.urls')),
    
    # Security: Remove default Django admin docs if not needed
    # path('admin/doc/', include('django.contrib.admindocs.urls')),
]

# Security: Health check endpoint for monitoring
urlpatterns += [
    path('health/', lambda request: HttpResponse('OK'), name='health_check'),
]

# Static and Media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Debug toolbar (development only) - OPTIONAL
    # try:
    #     import debug_toolbar
    #     urlpatterns += [
    #         path('__debug__/', include(debug_toolbar.urls)),
    #     ]
    # except ImportError:
    #     pass
else:
    # Production: Security - No static files served by Django
    # Use web server (nginx/apache) to serve static files
    pass

# Security: Global URL patterns for error handling
def custom_404_redirect(request, exception=None):
    """Custom 404 handler that logs the attempt"""
    from django.http import HttpResponseNotFound
    from django.template import loader
    
    # Log 404 attempts for security monitoring
    if exception:
        print(f"404 Error: {request.path} - {exception}")
    
    template = loader.get_template('errors/404.html')
    return HttpResponseNotFound(template.render({}, request))

def custom_500_redirect(request):
    """Custom 500 handler"""
    from django.http import HttpResponseServerError
    from django.template import loader
    
    template = loader.get_template('errors/500.html')
    return HttpResponseServerError(template.render({}, request))