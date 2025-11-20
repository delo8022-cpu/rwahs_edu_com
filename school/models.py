from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.utils.text import Truncator
import os
import re

# ==================== ENHANCED SECURITY VALIDATORS ====================
def validate_pdf_file(value):
    """Enhanced PDF validation with security checks"""
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError('শুধুমাত্র PDF ফাইল আপলোড করুন।')
    
    # Security: Check for potential malicious filenames
    filename = value.name.lower()
    if any(char in filename for char in ['/', '\\', '..', ';', '|', '&', '`', '$']):
        raise ValidationError('ফাইলের নামে অবৈধ ক্যারেক্টার রয়েছে।')

def validate_file_extension(value):
    """শুধুমাত্র নির্দিষ্ট ফাইল এক্সটেনশন allow করুন - Enhanced security"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg']
    
    if ext not in valid_extensions:
        raise ValidationError('শুধুমাত্র PDF, JPG, PNG, GIF, SVG ফাইল সাপোর্টেড।')
    
    # Security: Additional file type verification
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg']:
        # For images, you might want to add PIL verification in production
        pass

def validate_file_size(value):
    """ফাইল সাইজ limit করুন - Enhanced security"""
    filesize = value.size
    max_size = 5242880  # 5MB
    
    if filesize > max_size:
        raise ValidationError(f"ফাইলের সাইজ ৫MB এর বেশি হতে পারবে না (বর্তমান: {filesize//1024}KB)")
    
    if filesize == 0:
        raise ValidationError("ফাইলটি খালি বা ড্যামেজড হয়েছে")

def validate_safe_text(value):
    """Validate text fields for potential XSS attacks"""
    if value and any(tag in value.lower() for tag in ['<script>', 'javascript:', 'onload=', 'onerror=']):
        raise ValidationError('টেক্সটে অবৈধ কন্টেন্ট রয়েছে।')
    return value

def validate_year(value):
    """Validate year field"""
    current_year = timezone.now().year
    if value < 1900 or value > current_year + 1:
        raise ValidationError(f'বছরটি বৈধ নয় (১৯০০ - {current_year + 1} এর মধ্যে হতে হবে)')

# ==================== ENHANCED SECURITY LOG MODEL ====================
class SecurityLog(models.Model):
    ACTION_CHOICES = [
        ('login_success', 'লগইন সফল'),
        ('login_failed', 'লগইন ব্যর্থ'),
        ('file_upload', 'ফাইল আপলোড'),
        ('admin_action', 'এডমিন একশন'),
        ('page_view', 'পৃষ্ঠা দেখা'),
        ('security_attempt', 'সিকিউরিটি প্রচেষ্টা'),
        ('system_error', 'সিস্টেম ত্রুটি'),
        ('file_download', 'ফাইল ডাউনলোড'),
        ('rate_limit_exceeded', 'রেট লিমিট превышен'),
    ]
    
    user = models.ForeignKey(
        'auth.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name="ব্যবহারকারী"
    )
    action = models.CharField(
        max_length=50, 
        choices=ACTION_CHOICES,
        verbose_name="কর্ম"
    )
    ip_address = models.GenericIPAddressField(
        verbose_name="আইপি ঠিকানা"
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name="ব্যবহারকারী এজেন্ট"
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name="সময়"
    )
    details = models.TextField(
        blank=True,
        verbose_name="বিস্তারিত"
    )
    
    class Meta:
        verbose_name = "সিকুরিটি লগ"
        verbose_name_plural = "সিকুরিটি লগসমূহ"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.get_action_display()}"

    def save(self, *args, **kwargs):
        # Security: Truncate long details to prevent DB flooding
        if self.details:
            self.details = Truncator(self.details).chars(1000)
        super().save(*args, **kwargs)

# ==================== BASE ABSTRACT MODEL FOR SECURITY ====================
class SecureBaseModel(models.Model):
    """Abstract base model with common security fields"""
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="তৈরির সময়"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="আপডেটের সময়"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="সক্রিয়?"
    )
    
    class Meta:
        abstract = True

# ========== ENHANCED MODELS WITH SECURITY FEATURES ==========
class Notice(SecureBaseModel):
    title = models.CharField(
        max_length=200, 
        verbose_name="শিরোনাম",
        validators=[validate_safe_text]
    )
    content = models.TextField(
        verbose_name="বিস্তারিত",
        validators=[validate_safe_text]
    )
    published_date = models.DateTimeField(
        default=timezone.now, 
        verbose_name="প্রকাশের তারিখ"
    )

    class Meta:
        verbose_name = "নোটিশ"
        verbose_name_plural = "নোটিশসমূহ"
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['-published_date']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return Truncator(self.title).chars(50)

    def clean(self):
        """Additional model-level validation"""
        super().clean()
        if self.published_date and self.published_date > timezone.now() + timezone.timedelta(days=365):
            raise ValidationError({
                'published_date': 'প্রকাশের তারিখ ভবিষ্যতের এক বছরের বেশি হতে পারবে না।'
            })

class Result(SecureBaseModel):
    EXAM_CHOICES = [
        ('SSC', 'SSC'),
        ('HSC', 'HSC'),
        ('JSC', 'JSC'),
        ('PSC', 'PSC'),
    ]
    
    title = models.CharField(
        max_length=200, 
        verbose_name="শিরোনাম",
        validators=[validate_safe_text]
    )
    exam_type = models.CharField(
        max_length=10, 
        choices=EXAM_CHOICES, 
        verbose_name="পরীক্ষার ধরন"
    )
    year = models.IntegerField(
        verbose_name="বছর",
        validators=[validate_year]
    )
    pdf_file = models.FileField(
        upload_to='results/%Y/%m/',  # Organized by year/month
        verbose_name="PDF ফাইল",
        validators=[validate_pdf_file, validate_file_size]
    )
    uploaded_at = models.DateTimeField(
        default=timezone.now, 
        verbose_name="আপলোডের তারিখ"
    )

    class Meta:
        verbose_name = "রেজাল্ট"
        verbose_name_plural = "রেজাল্টসমূহ"
        ordering = ['-year', '-uploaded_at']
        indexes = [
            models.Index(fields=['exam_type']),
            models.Index(fields=['year']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['exam_type', 'year', 'title'],
                name='unique_result_per_exam_year'
            )
        ]

    def __str__(self):
        return f"{self.exam_type} {self.year} - {self.title}"

    def clean(self):
        """Validate result data"""
        super().clean()
        if self.year < 1990:
            raise ValidationError({
                'year': 'বছর ১৯৯০ এর কম হতে পারবে না।'
            })

class Slider(SecureBaseModel):
    title = models.CharField(
        max_length=200, 
        verbose_name="শিরোনাম",
        validators=[validate_safe_text]
    )
    subtitle = models.CharField(
        max_length=300, 
        blank=True, 
        verbose_name="সাবটাইটেল",
        validators=[validate_safe_text]
    )
    image = models.ImageField(
        upload_to='sliders/%Y/%m/',  # Organized uploads
        verbose_name="ছবি",
        validators=[validate_file_extension, validate_file_size]
    )
    link = models.URLField(
        blank=True, 
        verbose_name="লিঙ্ক",
        max_length=500
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name="ক্রম"
    )

    class Meta:
        verbose_name = "স্লাইড"
        verbose_name_plural = "স্লাইডার"
        ordering = ['order']
        indexes = [
            models.Index(fields=['order']),
        ]

    def __str__(self):
        return self.title

# ========== ENHANCED OFFICIALS MODEL ==========
class Official(SecureBaseModel):
    POSITION_CHOICES = [
        ('headmaster', 'প্রধান শিক্ষক'),
        ('assistant_headmaster', 'সহকারী প্রধান শিক্ষক'),
        ('teacher', 'শিক্ষক'),
        ('assistant_teacher', 'সহকারী শিক্ষক'),
        ('chairman', 'সভাপতি'),
        ('secretary', 'সম্পাদক'),
    ]
    
    name = models.CharField(
        max_length=200, 
        verbose_name="নাম",
        validators=[validate_safe_text]
    )
    position = models.CharField(
        max_length=20, 
        choices=POSITION_CHOICES, 
        verbose_name="পদবী"
    )
    photo = models.ImageField(
        upload_to='officials/%Y/',  # Organized by year
        verbose_name="ছবি",
        validators=[validate_file_extension, validate_file_size]
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name="ক্রম"
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        verbose_name="ফোন নম্বর"
    )
    email = models.EmailField(
        blank=True, 
        verbose_name="ইমেইল"
    )

    class Meta:
        verbose_name = "কর্মকর্তা"
        verbose_name_plural = "কর্মকর্তাগণ"
        ordering = ['order']
        indexes = [
            models.Index(fields=['position']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_position_display()})"

# ========== ENHANCED LINK MANAGEMENT ==========
class LinkCategory(SecureBaseModel):
    name = models.CharField(
        max_length=100, 
        verbose_name="ক্যাটাগরির নাম",
        validators=[validate_safe_text]
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name="ক্রম"
    )

    class Meta:
        verbose_name = "লিঙ্ক ক্যাটাগরি"
        verbose_name_plural = "লিঙ্ক ক্যাটাগরিসমূহ"
        ordering = ['order']

    def __str__(self):
        return self.name

class SidebarLink(SecureBaseModel):
    category = models.ForeignKey(
        LinkCategory, 
        on_delete=models.CASCADE, 
        verbose_name="ক্যাটাগরি"
    )
    title = models.CharField(
        max_length=200, 
        verbose_name="লিঙ্ক শিরোনাম",
        validators=[validate_safe_text]
    )
    url = models.URLField(
        verbose_name="URL",
        max_length=500
    )
    icon = models.ImageField(
        upload_to='sidebar_icons/', 
        blank=True, 
        verbose_name="আইকন (ঐচ্ছিক)",
        validators=[validate_file_extension, validate_file_size]
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name="ক্রম"
    )

    class Meta:
        verbose_name = "সাইডবার লিঙ্ক"
        verbose_name_plural = "সাইডবার লিঙ্কসমূহ"
        ordering = ['category', 'order']

    def __str__(self):
        return self.title

# ========== ENHANCED HOMEPAGE SECTIONS ==========
class HomePageSection(SecureBaseModel):
    SECTION_COLORS = [
        ('success', 'সবুজ (Success)'),
        ('warning', 'হলুদ (Warning)'),
        ('info', 'নীল (Info)'),
        ('primary', 'গাঢ় নীল (Primary)'),
        ('danger', 'লাল (Danger)'),
        ('secondary', 'ধূসর (Secondary)'),
    ]
    
    title = models.CharField(
        max_length=100, 
        verbose_name="শিরোনাম",
        validators=[validate_safe_text]
    )
    description = models.CharField(
        max_length=200, 
        blank=True, 
        verbose_name="বিস্তারিত",
        validators=[validate_safe_text]
    )
    link_url = models.URLField(
        blank=True, 
        verbose_name="লিঙ্ক URL",
        max_length=500
    )
    link_text = models.CharField(
        max_length=50, 
        default="দেখুন", 
        verbose_name="লিঙ্ক টেক্সট"
    )
    color = models.CharField(
        max_length=20, 
        choices=SECTION_COLORS, 
        default='success', 
        verbose_name="বাটন রং"
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name="ক্রম"
    )
    icon_class = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="আইকন ক্লাস",
        help_text="Font Awesome 5 ক্লাস লিখুন (https://fontawesome.com/v5/search)"
    )
    icon_image = models.ImageField(
        upload_to='section_icons/', 
        blank=True, 
        verbose_name="আইকন ইমেজ (ঐচ্ছিক)",
        help_text="PNG/SVG ইমেজ আপলোড করুন (48x48 বা 64x64)",
        validators=[validate_file_extension, validate_file_size]
    )

    class Meta:
        verbose_name = "হোমপেজ সেকশন"
        verbose_name_plural = "হোমপেজ সেকশনসমূহ"
        ordering = ['order']

    def __str__(self):
        return self.title

# ========== ENHANCED SITE SETTINGS ==========
class SiteSettings(SecureBaseModel):
    site_title = models.CharField(
        max_length=200, 
        default="রূপসা ওয়াহেদ আলী উচ্চ বিদ্যালয়", 
        verbose_name="সাইট শিরোনাম"
    )
    logo = models.ImageField(
        upload_to='site/logo/', 
        verbose_name="লোগো",
        validators=[validate_file_extension, validate_file_size]
    )
    favicon = models.ImageField(
        upload_to='site/favicon/', 
        verbose_name="ফেভিকন",
        validators=[validate_file_extension, validate_file_size]
    )
    contact_email = models.EmailField(
        default="contact@rwahs.edu", 
        verbose_name="যোগাযোগ ইমেইল"
    )
    phone = models.CharField(
        max_length=15, 
        blank=True, 
        verbose_name="ফোন নম্বর"
    )
    address = models.TextField(
        blank=True, 
        verbose_name="ঠিকানা"
    )
    
    class Meta:
        verbose_name = "সাইট সেটিংস"
        verbose_name_plural = "সাইট সেটিংস"

    def __str__(self):
        return "সাইট কনফিগারেশন"

    def save(self, *args, **kwargs):
        # Security: Ensure only one settings instance
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

# ========== ENHANCED BREAKING NEWS ==========
class BreakingNews(SecureBaseModel):
    title = models.CharField(
        max_length=200, 
        verbose_name="খবর",
        validators=[validate_safe_text]
    )
    link = models.URLField(
        blank=True, 
        verbose_name="লিঙ্ক",
        max_length=500
    )
    pdf_file = models.FileField(
        upload_to='breaking_news/%Y/%m/', 
        blank=True, 
        verbose_name="PDF ফাইল",
        validators=[validate_pdf_file, validate_file_size]
    )
    order = models.PositiveIntegerField(
        default=0, 
        verbose_name="ক্রম"
    )

    class Meta:
        verbose_name = "চলমান নোটিশ"
        verbose_name_plural = "চলমান নোটিশসমূহ"
        ordering = ['order']

    def __str__(self):
        return self.title