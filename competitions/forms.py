from django import forms
from .models import Competition, Problem, Submission

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['title', 'description', 'start_date', 'end_date', 'status', 'max_score']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ProblemForm(forms.ModelForm):
    class Meta:
        model = Problem
        fields = ['title', 'description', 'points', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['solution']
        widgets = {
            'solution': forms.Textarea(attrs={
                'rows': 15,
                'placeholder': 'Paste your code or solution here...'
            }),
        }
        labels = {
            'solution': 'Your Solution',
        }

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['score', 'feedback']
        widgets = {
            'feedback': forms.Textarea(attrs={'rows': 3}),
        }