"""
School Models Package
All models are imported here for easy access
"""

# Import core models (existing models)
try:
    from .core import (
        Notice, 
        Result, 
        Slider, 
        Official, 
        LinkCategory, 
        SidebarLink, 
        HomePageSection, 
        SiteSettings, 
        BreakingNews, 
        SecurityLog,
        ValidationError
    )
    
    # ✅ FIXED: Import validation functions from core
    from .core import (
        validate_pdf_file,
        validate_file_extension,
        validate_file_size
    )
except ImportError as e:
    print(f"Warning: Could not import core models: {e}")
    # Define empty classes as fallback
    class Notice: pass
    class Result: pass
    class Slider: pass
    class Official: pass
    class LinkCategory: pass
    class SidebarLink: pass
    class HomePageSection: pass
    class SiteSettings: pass
    class BreakingNews: pass
    class SecurityLog: pass
    class ValidationError: pass
    
    # Fallback validation functions
    def validate_pdf_file(value): pass
    def validate_file_extension(value): pass  
    def validate_file_size(value): pass

# Import academic models
try:
    from .academic import (
        Class,
        Subject
    )
except ImportError as e:
    print(f"Warning: Could not import academic models: {e}")
    class Class: pass
    class Subject: pass

# Import student models  
try:
    from .student import (
        Student
    )
except ImportError as e:
    print(f"Warning: Could not import student models: {e}")
    class Student: pass

# ==================== ALL MODELS LIST ====================
__all__ = [
    # Core models
    'Notice',
    'Result', 
    'Slider',
    'Official',
    'LinkCategory',
    'SidebarLink', 
    'HomePageSection',
    'SiteSettings',
    'BreakingNews',
    'SecurityLog',
    
    # Academic models
    'Class',
    'Subject',
    
    # Student models
    'Student',
    
    # Validation functions
    'validate_pdf_file',
    'validate_file_extension', 
    'validate_file_size',
]

print("✅ School models package loaded successfully!")

def validate_safe_text(value):
    """Validate text fields for potential XSS attacks"""
    if value and any(tag in value.lower() for tag in ['<script>', 'javascript:', 'onload=', 'onerror=']):
        raise ValidationError('টেক্সটে অবৈধ কন্টেন্ট রয়েছে।')
    return value