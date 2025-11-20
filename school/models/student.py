from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

class StudentBaseModel(models.Model):
    """Student module base model"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

class Student(StudentBaseModel):
    """Student management (ছাত্র ব্যবস্থাপনা)"""
    GENDER_CHOICES = [
        ('male', 'পুরুষ'),
        ('female', 'মহিলা'),
        ('other', 'অন্যান্য'),
    ]
    
    # Personal Information
    student_id = models.CharField(max_length=20, unique=True, verbose_name="Student ID")
    name = models.CharField(max_length=100, verbose_name="Full Name")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()
    
    # Academic Information
    class_level = models.ForeignKey('Class', on_delete=models.CASCADE, verbose_name="Class")
    roll_number = models.IntegerField(verbose_name="Roll Number")
    registration_number = models.CharField(max_length=20, blank=True, verbose_name="Registration No")
    
    # Contact Information
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+8801712345678'")
    phone = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(verbose_name="Full Address")
    
    # Guardian Information
    father_name = models.CharField(max_length=100, verbose_name="Father's Name")
    mother_name = models.CharField(max_length=100, verbose_name="Mother's Name")
    guardian_phone = models.CharField(validators=[phone_regex], max_length=17, blank=True, verbose_name="Guardian Phone")
    
    # Additional Info
    photo = models.ImageField(upload_to='students/photos/', blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True)
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        unique_together = ['class_level', 'roll_number']
        ordering = ['class_level', 'roll_number']
    
    def __str__(self):
        return f"{self.name} - {self.student_id} - Class {self.class_level}"
    
    def current_age(self):
        """Calculate current age"""
        import datetime
        today = datetime.date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )