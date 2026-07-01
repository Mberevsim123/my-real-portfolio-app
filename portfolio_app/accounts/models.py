from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import RegexValidator, MinLengthValidator
from django.conf import settings
import uuid


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not username:
            raise ValueError(_('The Username field must be set'))
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('email_verified', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, username, password, **extra_fields)


class CustomUser(AbstractUser):
    """Custom User model with additional fields"""
    
    # Remove email as required field from AbstractUser and set as unique
    email = models.EmailField(_('email address'), unique=True)
    
    # Additional fields
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    bio = models.TextField(_('biography'), max_length=500, blank=True)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)
    website = models.URLField(_('website'), blank=True)
    github = models.URLField(_('GitHub'), blank=True)
    linkedin = models.URLField(_('LinkedIn'), blank=True)
    twitter = models.URLField(_('Twitter'), blank=True)
    
    # Professional info
    job_title = models.CharField(_('job title'), max_length=100, blank=True)
    company = models.CharField(_('company'), max_length=100, blank=True)
    years_experience = models.PositiveIntegerField(_('years of experience'), default=0)
    
    # Verification and status
    email_verified = models.BooleanField(_('email verified'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    last_seen = models.DateTimeField(_('last seen'), default=timezone.now)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    # Override default fields
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['username']),
            models.Index(fields=['-date_joined']),
        ]
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def is_profile_complete(self):
        """Check if user profile is complete"""
        required_fields = [self.bio, self.job_title, self.avatar]
        return all(required_fields)
    
    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen = timezone.now()
        self.save(update_fields=['last_seen'])


class UserProfile(models.Model):
    """Extended user profile information"""
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Contact info
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    address = models.CharField(_('address'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=100, blank=True)
    country = models.CharField(_('country'), max_length=100, blank=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True)
    
    # Preferences
    newsletter_subscribed = models.BooleanField(_('newsletter subscribed'), default=True)
    email_notifications = models.BooleanField(_('email notifications'), default=True)
    
    # Social links
    instagram = models.URLField(_('Instagram'), blank=True)
    youtube = models.URLField(_('YouTube'), blank=True)
    medium = models.URLField(_('Medium'), blank=True)
    devto = models.URLField(_('dev.to'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"


class LoginHistory(models.Model):
    """Track user login history for security"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='login_history'
    )
    ip_address = models.GenericIPAddressField(_('IP address'))
    user_agent = models.TextField(_('user agent'))
    location = models.CharField(_('location'), max_length=255, blank=True)
    login_time = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('login history')
        verbose_name_plural = _('login histories')
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.email} - {self.login_time}"