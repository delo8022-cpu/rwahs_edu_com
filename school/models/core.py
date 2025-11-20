"""
Core models - existing models from original models.py
"""
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import os

# ==================== SECURITY VALIDATORS ====================
def validate_pdf_file(value):
    ext = os.path.splitext(value.name)[1].lower()
    if ext != '.pdf':
        raise ValidationError('শুধুমাত্র PDF ফাইল আপলোড করুন।')

def validate_file_extension(value):
    """শুধুমাত্র নির্দিষ্ট ফাইল এক্সটেনশন allow করুন"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.svg']
    if ext not in valid_extensions:
        raise ValidationError('শুধুমাত্র PDF, JPG, PNG, GIF, SVG ফাইল সাপোর্টেড।')

def validate_file_size(value):
    """ফাইল সাইজ limit করুন"""
    filesize = value.size
    if filesize > 5242880:  # 5MB
        raise ValidationError("ফাইলের সাইজ ৫MB এর বেশি হতে পারবে না")

# ==================== SECURITY LOG MODEL ====================
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
    
    user = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="ব্যবহারকারী")
    action = models.CharField(max_length=50, choices=ACTION_CHOICES, verbose_name="কর্ম")
    ip_address = models.GenericIPAddressField(verbose_name="আইপি ঠিকানা")
    user_agent = models.TextField(blank=True, verbose_name="ব্যবহারকারী এজেন্ট")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="সময়")
    details = models.TextField(blank=True, verbose_name="বিস্তারিত")
    
    class Meta:
        verbose_name = "সিকুরিটি লগ"
        verbose_name_plural = "সিকুরিটি লগসমূহ"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.get_action_display()}"

# ==================== BASE MODEL ====================
class BaseModel(models.Model):
    """Base model with common fields"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="তৈরির সময়")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="আপডেটের সময়")
    is_active = models.BooleanField(default=True, verbose_name="সক্রিয়?")
    
    class Meta:
        abstract = True

# ==================== EXISTING MODELS ====================
class Notice(BaseModel):
    title = models.CharField(max_length=200, verbose_name="শিরোনাম")
    content = models.TextField(verbose_name="বিস্তারিত")
    published_date = models.DateTimeField(default=timezone.now, verbose_name="প্রকাশের তারিখ")

    class Meta:
        verbose_name = "নোটিশ"
        verbose_name_plural = "নোটিশসমূহ"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

class Result(BaseModel):
    EXAM_CHOICES = [
        ('SSC', 'SSC'),
        ('HSC', 'HSC'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="শিরোনাম")
    exam_type = models.CharField(max_length=10, choices=EXAM_CHOICES, verbose_name="পরীক্ষার ধরন")
    year = models.IntegerField(verbose_name="বছর")
    pdf_file = models.FileField(
        upload_to='results/', 
        verbose_name="PDF ফাইল",
        validators=[validate_pdf_file, validate_file_size]
    )
    uploaded_at = models.DateTimeField(default=timezone.now, verbose_name="আপলোডের তারিখ")

    class Meta:
        verbose_name = "রেজাল্ট"
        verbose_name_plural = "রেজাল্টসমূহ"
        ordering = ['-year', '-uploaded_at']

    def __str__(self):
        return f"{self.exam_type} {self.year} - {self.title}"

class Slider(BaseModel):
    title = models.CharField(max_length=200, verbose_name="শিরোনাম")
    subtitle = models.CharField(max_length=300, blank=True, verbose_name="সাবটাইটেল")
    image = models.ImageField(
        upload_to='sliders/', 
        verbose_name="ছবি",
        validators=[validate_file_extension, validate_file_size]
    )
    link = models.URLField(blank=True, verbose_name="লিঙ্ক")
    order = models.PositiveIntegerField(default=0, verbose_name="ক্রম")

    class Meta:
        verbose_name = "স্লাইড"
        verbose_name_plural = "স্লাইডার"
        ordering = ['order']

    def __str__(self):
        return self.title

class Official(BaseModel):
    POSITION_CHOICES = [
        ('chairman', 'প্রধান শিক্ষক'),
        ('secretary', 'সভাপতি'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="নাম")
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, verbose_name="পদবী")
    photo = models.ImageField(
        upload_to='officials/', 
        verbose_name="ছবি",
        validators=[validate_file_extension, validate_file_size]
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ক্রম")

    class Meta:
        verbose_name = "কর্মকর্তা"
        verbose_name_plural = "কর্মকর্তাগণ"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.get_position_display()})"

class LinkCategory(BaseModel):
    name = models.CharField(max_length=100, verbose_name="ক্যাটাগরির নাম")
    order = models.PositiveIntegerField(default=0, verbose_name="ক্রম")

    class Meta:
        verbose_name = "লিঙ্ক ক্যাটাগরি"
        verbose_name_plural = "লিঙ্ক ক্যাটাগরিসমূহ"
        ordering = ['order']

    def __str__(self):
        return self.name

class SidebarLink(BaseModel):
    category = models.ForeignKey(LinkCategory, on_delete=models.CASCADE, verbose_name="ক্যাটাগরি")
    title = models.CharField(max_length=200, verbose_name="লিঙ্ক শিরোনাম")
    url = models.URLField(verbose_name="URL")
    icon = models.ImageField(
        upload_to='sidebar_icons/', 
        blank=True, 
        verbose_name="আইকন (ঐচ্ছিক)",
        validators=[validate_file_extension, validate_file_size]
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ক্রম")

    class Meta:
        verbose_name = "সাইডবার লিঙ্ক"
        verbose_name_plural = "সাইডবার লিঙ্কসমূহ"
        ordering = ['category', 'order']

    def __str__(self):
        return self.title

class HomePageSection(BaseModel):
    SECTION_COLORS = [
        ('success', 'সবুজ (Success)'),
        ('warning', 'হলুদ (Warning)'),
        ('info', 'নীল (Info)'),
        ('primary', 'গাঢ় নীল (Primary)'),
        ('danger', 'লাল (Danger)'),
        ('secondary', 'ধূসর (Secondary)'),
    ]
    
    title = models.CharField(max_length=100, verbose_name="শিরোনাম")
    description = models.CharField(max_length=200, blank=True, verbose_name="বিস্তারিত")
    link_url = models.URLField(blank=True, verbose_name="লিঙ্ক URL")
    link_text = models.CharField(max_length=50, default="দেখুন", verbose_name="লিঙ্ক টেক্সট")
    color = models.CharField(max_length=20, choices=SECTION_COLORS, default='success', verbose_name="বাটন রং")
    order = models.PositiveIntegerField(default=0, verbose_name="ক্রম")
    icon_class = models.CharField(max_length=50, blank=True, verbose_name="আইকন ক্লাস")
    icon_image = models.ImageField(
        upload_to='section_icons/', 
        blank=True, 
        verbose_name="আইকন ইমেজ (ঐচ্ছিক)",
        validators=[validate_file_extension, validate_file_size]
    )

    class Meta:
        verbose_name = "হোমপেজ সেকশন"
        verbose_name_plural = "হোমপেজ সেকশনসমূহ"
        ordering = ['order']

    def __str__(self):
        return self.title

class SiteSettings(BaseModel):
    site_title = models.CharField(max_length=200, default="রূপসা ওয়াহেদ আলী উচ্চ বিদ্যালয়", verbose_name="সাইট শিরোনাম")
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
    contact_email = models.EmailField(default="contact@rwahs.edu", verbose_name="যোগাযোগ ইমেইল")
    phone = models.CharField(max_length=15, blank=True, verbose_name="ফোন নম্বর")
    address = models.TextField(blank=True, verbose_name="ঠিকানা")
    
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

class BreakingNews(BaseModel):
    title = models.CharField(max_length=200, verbose_name="খবর")
    link = models.URLField(blank=True, verbose_name="লিঙ্ক")
    pdf_file = models.FileField(
        upload_to='breaking_news/', 
        blank=True, 
        verbose_name="PDF ফাইল",
        validators=[validate_pdf_file, validate_file_size]
    )
    order = models.PositiveIntegerField(default=0, verbose_name="ক্রম")

    class Meta:
        verbose_name = "চলমান নোটিশ"
        verbose_name_plural = "চলমান নোটিশসমূহ"
        ordering = ['order']

    def __str__(self):
        return self.title