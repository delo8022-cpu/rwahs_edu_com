from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='ইমেইল ঠিকানা')
    first_name = forms.CharField(max_length=30, required=True, label='প্রথম নাম')
    last_name = forms.CharField(max_length=30, required=True, label='শেষ নাম')
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = True
        user.is_superuser = True
        
        if commit:
            user.save()
        return user