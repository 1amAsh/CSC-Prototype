from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User
from .models import Application

class ApplicationForm(forms.ModelForm):
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password"
    )
    
    class Meta:
        model = Application
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 
                  'age', 'school', 'programming_experience', 'why_join']
        widgets = {
            'password': forms.PasswordInput,
            'programming_experience': forms.Textarea(attrs={'rows': 4}),
            'why_join': forms.Textarea(attrs={'rows': 4}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        
        # Check if username exists in User model
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        
        # Check if username exists in pending applications
        if Application.objects.filter(username=username, status='pending').exists():
            raise ValidationError("An application with this username is already pending.")
        
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        # Check if email exists in User model
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        
        # Check if email exists in pending applications
        if Application.objects.filter(email=email, status='pending').exists():
            raise ValidationError("An application with this email is already pending.")
        
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise ValidationError("Passwords do not match.")
        
        return cleaned_data