from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.shortcuts import render
from django.urls import path
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.core.exceptions import ValidationError

# ✅ FIXED: Import models properly
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin

# ✅ FIXED: Import from models package
from .models.core import Notice, Result, Slider, Official, LinkCategory, SidebarLink, HomePageSection, SiteSettings, BreakingNews, SecurityLog
from .models.academic import Class, Subject
from .models.student import Student

from .utils import log_security_event, get_client_ip
import logging

# Security: Setup logger
logger = logging.getLogger('school.admin')

# ==================== CUSTOM ADMIN LOGIN VIEW WITH SECURITY ====================
class CustomAdminLoginView(LoginView):
    template_name = 'admin/login.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # SiteSettings থেকে error handling সহ
        try:
            context['site_settings'] = SiteSettings.load()
        except Exception as e:
            # Security: Log the error but don't expose to user
            logger.warning(f"SiteSettings load failed in admin login: {str(e)}")
            context['site_settings'] = None
        return context
    
    def form_valid(self, form):
        # Security: Log successful admin login attempts
        user = form.get_user()
        log_security_event(
            self.request, 
            'login_success', 
            f'Admin login successful: {user.username}'
        )
        logger.info(f"Admin login successful: {user.username} - IP: {get_client_ip(self.request)}")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Security: Log failed admin login attempts
        username = form.data.get('username', 'unknown')
        log_security_event(
            self.request, 
            'login_failed', 
            f'Admin login failed for username: {username}'
        )
        logger.warning(f"Admin login failed: {username} - IP: {get_client_ip(self.request)}")
        return super().form_invalid(form)

# ==================== SECURITY ENHANCED ADMIN SITE ====================
class CustomAdminSite(AdminSite):
    site_header = "রূপসা ওয়াহেদ আলী উচ্চ বিদ্যালয় - এডমিন প্যানেল"
    site_title = "RWAHS Admin"
    index_title = "ড্যাশবোর্ড"
    login_view = CustomAdminLoginView
    login_template = 'admin/login.html'
    index_template = 'admin/dashboard.html'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('dashboard/', self.admin_view(self.dashboard_view), name='dashboard'),
            path('security-logs/', self.admin_view(self.security_logs_view), name='security_logs'),
            path('system-health/', self.admin_view(self.system_health_view), name='system_health'),
        ]
        return custom_urls + urls
    
    def has_permission(self, request):
        """
        Enhanced permission check with security logging
        """
        has_perm = request.user.is_active and request.user.is_staff
        
        if not has_perm and request.user.is_authenticated:
            # Security: Log unauthorized admin access attempts
            log_security_event(
                request, 
                'security_attempt', 
                f'Unauthorized admin access attempt by: {request.user.username}'
            )
            logger.warning(f"Unauthorized admin access: {request.user.username}")
        
        return has_perm
    
    def dashboard_view(self, request):
        """Enhanced dashboard with security features"""
        # Authentication check
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseRedirect('/admin/login/')
        
        # Security: Log dashboard access
        log_security_event(request, 'admin_action', 'Admin dashboard accessed')
        
        try:
            # Get statistics with error handling
            today = timezone.now().date()
            last_week = today - timezone.timedelta(days=7)
            
            stats = {
                # Basic counts
                'total_notices': Notice.objects.count(),
                'active_notices': Notice.objects.filter(is_active=True).count(),
                'total_results': Result.objects.count(),
                'active_sliders': Slider.objects.filter(is_active=True).count(),
                'total_officials': Official.objects.count(),
                'total_sections': HomePageSection.objects.filter(is_active=True).count(),
                
                # New academic counts
                'total_classes': Class.objects.count(),
                'total_students': Student.objects.count(),
                'total_subjects': Subject.objects.count(),
                
                # Recent activity
                'recent_notices': Notice.objects.order_by('-published_date')[:5],
                'recent_results': Result.objects.order_by('-uploaded_at')[:3],
                'recent_students': Student.objects.order_by('-created_at')[:5],
                
                # Security stats
                'recent_security_logs': SecurityLog.objects.order_by('-timestamp')[:10],
                'failed_logins_today': SecurityLog.objects.filter(
                    action='login_failed',
                    timestamp__date=today
                ).count(),
                
                # System info
                'total_users': User.objects.count(),
                'active_users': User.objects.filter(is_active=True).count(),
            }
            
        except Exception as e:
            # Security: Log dashboard errors
            logger.error(f"Dashboard error: {str(e)}")
            stats = {
                'total_notices': 0,
                'active_notices': 0,
                'total_results': 0,
                'active_sliders': 0,
                'total_officials': 0,
                'total_classes': 0,
                'total_students': 0,
                'recent_notices': [],
                'error': str(e)
            }
            messages.error(request, f'ড্যাশবোর্ড লোড করতে সমস্যা: {str(e)}')
        
        return render(request, 'admin/dashboard.html', stats)
    
    def security_logs_view(self, request):
        """Security logs viewing interface"""
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseRedirect('/admin/login/')
        
        # Security: Only superusers can view security logs
        if not request.user.is_superuser:
            messages.error(request, 'আপনার সিকিউরিটি লগ দেখার অনুমতি নেই।')
            return HttpResponseRedirect('/admin/')
        
        logs = SecurityLog.objects.all().order_by('-timestamp')[:100]  # Limit to 100 logs
        return render(request, 'admin/security_logs.html', {'logs': logs})
    
    def system_health_view(self, request):
        """System health monitoring"""
        if not request.user.is_authenticated or not request.user.is_staff:
            return HttpResponseRedirect('/admin/login/')
        
        health_data = {
            'database_status': 'OK',
            'media_storage': 'OK',
            'static_files': 'OK',
            'last_backup': 'N/A',
        }
        
        # Basic system checks
        try:
            Notice.objects.first()  # Test database connection
        except Exception as e:
            health_data['database_status'] = f'Error: {str(e)}'
            logger.error(f"Database health check failed: {str(e)}")
        
        return render(request, 'admin/system_health.html', {'health_data': health_data})

# কাস্টম এডমিন সাইট ইনস্ট্যান্স
custom_admin_site = CustomAdminSite(name='custom_admin')

# ==================== SECURITY ENHANCED MODEL ADMINS ====================
class SecureModelAdmin(admin.ModelAdmin):
    """Base ModelAdmin with security enhancements"""
    
    def save_model(self, request, obj, form, change):
        """Log all admin model changes"""
        action = 'updated' if change else 'created'
        model_name = obj._meta.verbose_name
        
        log_security_event(
            request, 
            'admin_action', 
            f'{model_name} {action}: {str(obj)}'
        )
        logger.info(f"Admin {action} {model_name}: {str(obj)} - User: {request.user.username}")
        
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Log all admin model deletions"""
        model_name = obj._meta.verbose_name
        
        log_security_event(
            request, 
            'admin_action', 
            f'{model_name} deleted: {str(obj)}'
        )
        logger.warning(f"Admin deleted {model_name}: {str(obj)} - User: {request.user.username}")
        
        super().delete_model(request, obj)

# ==================== OLD MODELS REGISTRATION ====================
@admin.register(Notice, site=custom_admin_site)
class NoticeAdmin(SecureModelAdmin):
    list_display = ['title', 'published_date', 'is_active', 'created_at']
    list_filter = ['is_active', 'published_date']
    search_fields = ['title', 'content']
    date_hierarchy = 'published_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('মূল তথ্য', {
            'fields': ('title', 'content', 'published_date', 'is_active')
        }),
        ('সিস্টেম তথ্য', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Result, site=custom_admin_site)
class ResultAdmin(SecureModelAdmin):
    list_display = ['title', 'exam_type', 'year', 'is_active', 'uploaded_at']
    list_filter = ['exam_type', 'year', 'is_active']
    search_fields = ['title']
    readonly_fields = ['uploaded_at', 'created_at', 'updated_at']
    
    def save_model(self, request, obj, form, change):
        """Additional validation for results"""
        if obj.year < 1990:
            messages.error(request, 'বছর ১৯৯০ এর কম হতে পারবে না।')
            return
        
        # Check for duplicate results
        existing = Result.objects.filter(
            exam_type=obj.exam_type,
            year=obj.year,
            title=obj.title
        ).exclude(pk=obj.pk)
        
        if existing.exists():
            messages.warning(request, 'একই পরীক্ষার জন্য একই শিরোনামের রেজাল্ট আগেই আছে।')
        
        super().save_model(request, obj, form, change)

@admin.register(Slider, site=custom_admin_site)
class SliderAdmin(SecureModelAdmin):
    list_display = ['title', 'order', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Official, site=custom_admin_site)
class OfficialAdmin(SecureModelAdmin):
    list_display = ['name', 'position', 'order', 'is_active']
    list_editable = ['order']
    list_filter = ['position', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['name']

@admin.register(LinkCategory, site=custom_admin_site)
class LinkCategoryAdmin(SecureModelAdmin):
    list_display = ['name', 'order', 'is_active']
    list_editable = ['order']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SidebarLink, site=custom_admin_site)
class SidebarLinkAdmin(SecureModelAdmin):
    list_display = ['title', 'category', 'url', 'is_active', 'order']
    list_filter = ['category', 'is_active']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    search_fields = ['title', 'url']

@admin.register(HomePageSection, site=custom_admin_site)
class HomePageSectionAdmin(SecureModelAdmin):
    list_display = ['title', 'color', 'order', 'is_active']
    list_editable = ['order', 'is_active']
    list_filter = ['is_active', 'color']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SiteSettings, site=custom_admin_site)
class SiteSettingsAdmin(SecureModelAdmin):
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    readonly_fields = ['created_at', 'updated_at']

@admin.register(BreakingNews, site=custom_admin_site)
class BreakingNewsAdmin(SecureModelAdmin):
    list_display = ['title', 'is_active', 'order', 'created_at']
    list_editable = ['is_active', 'order']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(SecurityLog, site=custom_admin_site)
class SecurityLogAdmin(SecureModelAdmin):
    list_display = ['timestamp', 'action', 'user', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'ip_address', 'details']
    readonly_fields = ['timestamp', 'user', 'action', 'ip_address', 'user_agent', 'details']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

# ==================== NEW MODELS REGISTRATION ====================
@admin.register(Class, site=custom_admin_site)
class ClassAdmin(SecureModelAdmin):
    list_display = ['name', 'section', 'capacity', 'is_active']  # ✅ FIXED: class_teacher removed
    list_filter = ['name', 'is_active']
    search_fields = ['name', 'section']
    list_editable = ['capacity', 'is_active']

@admin.register(Subject, site=custom_admin_site)
class SubjectAdmin(SecureModelAdmin):
    list_display = ['name', 'code', 'class_level', 'is_active']  # ✅ FIXED: teacher removed
    list_filter = ['class_level', 'is_active']
    search_fields = ['name', 'code']

@admin.register(Student, site=custom_admin_site)
class StudentAdmin(SecureModelAdmin):
    list_display = ['name', 'student_id', 'class_level', 'roll_number', 'gender', 'is_active']
    list_filter = ['class_level', 'gender', 'is_active']
    search_fields = ['name', 'student_id', 'roll_number']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('ব্যক্তিগত তথ্য', {
            'fields': ('student_id', 'name', 'gender', 'date_of_birth', 'photo', 'blood_group')
        }),
        ('একাডেমিক তথ্য', {
            'fields': ('class_level', 'roll_number', 'registration_number')
        }),
        ('যোগাযোগ তথ্য', {
            'fields': ('phone', 'email', 'address')
        }),
        ('অভিভাবক তথ্য', {
            'fields': ('father_name', 'mother_name', 'guardian_phone')
        }),
        ('সিস্টেম তথ্য', {
            'fields': ('is_active', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# ==================== ENHANCED USER ADMIN ====================
class CustomUserAdmin(UserAdmin):
    """Enhanced UserAdmin with security features"""
    
    def save_model(self, request, obj, form, change):
        """Log user modifications"""
        action = 'updated' if change else 'created'
        
        log_security_event(
            request, 
            'admin_action', 
            f'User {action}: {obj.username}'
        )
        
        super().save_model(request, obj, form, change)
    
    def delete_model(self, request, obj):
        """Log user deletions"""
        log_security_event(
            request, 
            'admin_action', 
            f'User deleted: {obj.username}'
        )
        logger.warning(f"User deleted: {obj.username} - By: {request.user.username}")
        
        super().delete_model(request, obj)

# Django এর default models রেজিস্টার করুন
custom_admin_site.register(User, CustomUserAdmin)
custom_admin_site.register(Group, GroupAdmin)

# ==================== ADMIN ACTIONS FOR SECURITY ====================
def deactivate_selected(modeladmin, request, queryset):
    """Admin action to deactivate multiple items"""
    updated = queryset.update(is_active=False)
    
    log_security_event(
        request, 
        'admin_action', 
        f'Deactivated {updated} {modeladmin.model._meta.verbose_name_plural}'
    )
    
    messages.success(request, f'{updated} টি আইটেম ডিএক্টিভেট করা হয়েছে।')

deactivate_selected.short_description = "নির্বাচিত আইটেম ডিএক্টিভেট করুন"

def activate_selected(modeladmin, request, queryset):
    """Admin action to activate multiple items"""
    updated = queryset.update(is_active=True)
    
    log_security_event(
        request, 
        'admin_action', 
        f'Activated {updated} {modeladmin.model._meta.verbose_name_plural}'
    )
    
    messages.success(request, f'{updated} টি আইটেম এক্টিভেট করা হয়েছে।')

activate_selected.short_description = "নির্বাচিত আইটেম এক্টিভেট করুন"

# Add actions to relevant admins
for admin_class in [NoticeAdmin, ResultAdmin, SliderAdmin, SidebarLinkAdmin, 
                   HomePageSectionAdmin, BreakingNewsAdmin, ClassAdmin, 
                   SubjectAdmin, StudentAdmin]:
    admin_class.actions = [deactivate_selected, activate_selected]