"""
School App URL Configuration
রূপসা ওয়াহেদ আলী উচ্চ বিদ্যালয় - URL কনফিগারেশন
"""

from django.urls import path
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    # Home page
    path('', views.home, name='home'),
    
    # Notices URLs with security validation
    path('notices/', views.notice_list, name='notice_list'),
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),
    
    # Results URLs
    path('results/', views.result_archive, name='result_archive'),
    path('results/download/<int:pk>/', views.result_download, name='result_download'),
    
    # Security: Public facing pages with content security
    path('about/', TemplateView.as_view(template_name='school/about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='school/contact.html'), name='contact'),
    path('privacy-policy/', TemplateView.as_view(template_name='school/privacy_policy.html'), name='privacy_policy'),
    
    # Security: Error pages for custom error handling
    path('error/404/', views.custom_404_view, name='custom_404'),
    path('error/500/', views.custom_500_view, name='custom_500'),
    path('error/403/', views.custom_403_view, name='custom_403'),
    path('error/400/', views.custom_400_view, name='custom_400'),
]

# Security: API endpoints (if needed in future)
api_patterns = [
    # path('api/notices/', views.NoticeAPIView.as_view(), name='api_notices'),
]

urlpatterns += api_patterns

# Security: Rate limiting decorators (install django-ratelimit if needed)
# @ratelimit(key='ip', rate='10/m', block=True)