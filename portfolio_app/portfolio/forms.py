from django import forms
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .models import ContactMessage, NewsletterSubscriber, Comment
from django.utils.text import slugify
import re


class ContactForm(forms.ModelForm):
    """Contact form for website visitors"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name',
            'required': True
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': True
        })
    )
    subject = forms.ChoiceField(
        choices=ContactMessage.SUBJECT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    custom_subject = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Custom subject (if other)'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Your message here...',
            'required': True
        })
    )
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'custom_subject', 'message']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            raise forms.ValidationError('Please enter a valid email address.')
        return email
    
    def clean_custom_subject(self):
        subject = self.cleaned_data.get('subject')
        custom_subject = self.cleaned_data.get('custom_subject')
        
        if subject == 'other' and not custom_subject:
            raise forms.ValidationError('Please provide a custom subject.')
        
        return custom_subject
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError('Message must be at least 10 characters long.')
        if len(message) > 5000:
            raise forms.ValidationError('Message must be less than 5000 characters.')
        return message


class NewsletterForm(forms.ModelForm):
    """Newsletter subscription form"""
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': True
        })
    )
    name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name (optional)'
        })
    )
    
    class Meta:
        model = NewsletterSubscriber
        fields = ['email', 'name']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if NewsletterSubscriber.objects.filter(email=email, is_active=True).exists():
            raise forms.ValidationError('This email is already subscribed.')
        return email


class CommentForm(forms.ModelForm):
    """Comment form for blog posts"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email (will not be published)'
        })
    )
    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your website (optional)'
        })
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Write your comment here...'
        })
    )
    
    class Meta:
        model = Comment
        fields = ['name', 'email', 'website', 'content']
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        # Basic spam protection
        spam_keywords = ['casino', 'viagra', 'porn', 'xxx']
        content_lower = content.lower()
        for keyword in spam_keywords:
            if keyword in content_lower:
                raise forms.ValidationError('Your comment appears to contain spam.')
        return content


class SearchForm(forms.Form):
    """Global search form"""
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search projects, blog posts...',
            'autocomplete': 'off'
        })
    )
    category = forms.ModelChoiceField(
        required=False,
        queryset=None,  # Will be set in __init__
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].widget.attrs['class'] = 'form-select'


class ResumeUploadForm(forms.Form):
    """Resume upload form for admin"""
    resume = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx'
        })
    )
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Check file size (max 5MB)
            if resume.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be under 5MB.')
            
            # Check file extension
            ext = resume.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise forms.ValidationError('Only PDF and Word documents are allowed.')
        
        return resume