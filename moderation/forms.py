from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Please provide details about why you are reporting this user...'
            }),
        }