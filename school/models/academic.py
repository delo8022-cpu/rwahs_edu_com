from django.db import models
from django.utils import timezone

class AcademicBaseModel(models.Model):
    """Academic module base model"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

class Class(AcademicBaseModel):
    """Class management (ক্লাস ব্যবস্থাপনা)"""
    CLASS_CHOICES = [
        ('6', 'ষষ্ঠ শ্রেণী'),
        ('7', 'সপ্তম শ্রেণী'),
        ('8', 'অষ্টম শ্রেণী'),
        ('9', 'নবম শ্রেণী'),
        ('10', 'দশম শ্রেণী'),
    ]
    
    name = models.CharField(max_length=10, choices=CLASS_CHOICES)
    section = models.CharField(max_length=10, default='A')  # A, B, C section
    capacity = models.IntegerField(default=40)
    # class_teacher = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        unique_together = ['name', 'section']
    
    def __str__(self):
        return f"{self.get_name_display()} - {self.section}"

class Subject(AcademicBaseModel):
    """Subject management (বিষয় ব্যবস্থাপনা)"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    class_level = models.ForeignKey(Class, on_delete=models.CASCADE)
    # teacher = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
    
    def __str__(self):
        return f"{self.name} - {self.class_level}"