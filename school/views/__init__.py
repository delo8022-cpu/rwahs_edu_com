"""
School Views Package
All views are imported here for easy access
"""

# Import core views (existing views)
try:
    from .core_views import (
        home,
        notice_list,
        notice_detail, 
        result_archive,
        result_download,
        custom_404_view,
        custom_500_view,
        custom_403_view,
        custom_400_view,
        health_check
    )
except ImportError as e:
    print(f"Warning: Could not import core views: {e}")
    # Define empty functions as fallback
    def home(request): pass
    def notice_list(request): pass
    def notice_detail(request, pk): pass
    def result_archive(request): pass
    def result_download(request, pk): pass
    def custom_404_view(request, exception=None): pass
    def custom_500_view(request): pass
    def custom_403_view(request, exception=None): pass
    def custom_400_view(request, exception=None): pass
    def health_check(request): pass

# Future views - commented out until they exist
# from .academic_views import (
#     # Academic views will be added here
# )

# from .student_views import (
#     # Student views will be added here
# )

# from .staff_views import (
#     # Staff views will be added here
# )

# from .attendance_views import (
#     # Attendance views will be added here
# )

# from .examination_views import (
#     # Examination views will be added here  
# )

# from .finance_views import (
#     # Finance views will be added here
# )

# ==================== ALL VIEWS LIST ====================
__all__ = [
    # Core views
    'home',
    'notice_list',
    'notice_detail',
    'result_archive', 
    'result_download',
    'custom_404_view',
    'custom_500_view',
    'custom_403_view',
    'custom_400_view',
    'health_check',
]

print("✅ School views package loaded successfully!")