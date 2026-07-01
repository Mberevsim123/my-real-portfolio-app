from django import forms
from django.contrib.auth.forms import (
    UserCreationForm, UserChangeForm, 
    AuthenticationForm, PasswordResetForm, 
    SetPasswordForm, PasswordChangeForm
)
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError
from .models import UserProfile
import re

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form with email required"""
    
    email = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    username = forms.CharField(
        label=_('Username'),
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password'
        })
    )
    password2 = forms.CharField(
        label=_('Confirm Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('A user with this email already exists.'))
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_('A user with this username already exists.'))
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError(_('Enter a valid username. This value may contain only letters, numbers, and @/./+/-/_ characters.'))
        return username


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form"""
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'bio', 
                 'avatar', 'website', 'github', 'linkedin', 'twitter',
                 'job_title', 'company')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'github': forms.URLInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control'}),
            'twitter': forms.URLInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'company': forms.TextInput(attrs={'class': 'form-control'}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    """Custom authentication form with Bootstrap styling"""
    
    username = forms.EmailField(
        label=_('Email'),
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email'
        })
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    
    error_messages = {
        'invalid_login': _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }


class CustomPasswordResetForm(PasswordResetForm):
    """Custom password reset form"""
    
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError(_('No user found with this email address.'))
        return email


class CustomSetPasswordForm(SetPasswordForm):
    """Custom set password form"""
    
    new_password1 = forms.CharField(
        label=_('New password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        label=_('Confirm new password'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile"""
    
    class Meta:
        model = UserProfile
        fields = ('phone_number', 'address', 'city', 'country', 'postal_code',
                 'newsletter_subscribed', 'email_notifications', 'instagram',
                 'youtube', 'medium', 'devto')
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'newsletter_subscribed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_notifications': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'instagram': forms.URLInput(attrs={'class': 'form-control'}),
            'youtube': forms.URLInput(attrs={'class': 'form-control'}),
            'medium': forms.URLInput(attrs={'class': 'form-control'}),
            'devto': forms.URLInput(attrs={'class': 'form-control'}),
        }


class EmailChangeForm(forms.Form):
    """Form for changing email address"""
    
    new_email = forms.EmailField(
        label=_('New email address'),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    confirm_email = forms.EmailField(
        label=_('Confirm email address'),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_email = cleaned_data.get('new_email')
        confirm_email = cleaned_data.get('confirm_email')
        
        if new_email and confirm_email and new_email != confirm_email:
            raise ValidationError(_('Email addresses do not match.'))
        
        if new_email and User.objects.filter(email=new_email).exists():
            raise ValidationError(_('A user with this email already exists.'))
        
        return cleaned_data