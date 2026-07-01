"""
Business logic layer for accounts app
Separates business logic from views for better maintainability
"""

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from .models import LoginHistory  # Import at the top
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class AccountService:
    """Service class for account-related operations"""
    
    @staticmethod
    def create_user(email, username, password, **extra_fields):
        """Create a new user with transaction support"""
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=email,
                    username=username,
                    password=password,
                    **extra_fields
                )
                logger.info(f"User created successfully: {email}")
                return user
        except Exception as e:
            logger.error(f"Error creating user {email}: {str(e)}")
            raise
    
    @staticmethod
    def update_user_profile(user, data):
        """Update user profile information"""
        try:
            for field, value in data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)
            user.save()
            logger.info(f"Profile updated for user: {user.email}")
            return True
        except Exception as e:
            logger.error(f"Error updating profile for {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_verification_email(request, user):
        """Send email verification link"""
        try:
            current_site = get_current_site(request)
            mail_subject = 'Verify your email address'
            message = render_to_string('accounts/verification_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            send_mail(
                mail_subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            logger.info(f"Verification email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Error sending verification email to {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def verify_email(user):
        """Mark user email as verified"""
        if not user.email_verified:
            user.email_verified = True
            user.save()
            logger.info(f"Email verified for user: {user.email}")
            return True
        return False
    
    @staticmethod
    def record_login_attempt(user, request, success=True):
        """Record user login attempt for security"""
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            LoginHistory.objects.create(
                user=user,
                ip_address=ip,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                is_successful=success
            )
            
            if success:
                user.update_last_seen()
            
            return True
        except Exception as e:
            logger.error(f"Error recording login for {user.email}: {str(e)}")
            return False
    
    @staticmethod
    def get_user_statistics(user):
        """Get user statistics"""
        return {
            'login_count': LoginHistory.objects.filter(user=user, is_successful=True).count(),
            'last_login': user.last_login,
            'last_seen': user.last_seen,
            'profile_complete': user.is_profile_complete,
            'account_age': (timezone.now() - user.date_joined).days,
        }
    
    @staticmethod
    def change_email(user, new_email):
        """Change user email with verification"""
        if User.objects.filter(email=new_email).exclude(pk=user.pk).exists():
            return False, "Email already in use"
        
        old_email = user.email
        user.email = new_email
        user.email_verified = False
        user.save()
        
        logger.info(f"Email changed from {old_email} to {new_email} for user {user.pk}")
        return True, "Email changed successfully"
    
    @staticmethod
    def deactivate_account(user, reason=""):
        """Deactivate user account"""
        user.is_active = False
        user.save()
        
        logger.warning(f"Account deactivated for user {user.email}. Reason: {reason}")
        return True


class SecurityService:
    """Service for security-related operations"""
    
    @staticmethod
    def validate_password_strength(password):
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        if not any(char.isdigit() for char in password):
            errors.append("Password must contain at least one digit")
        if not any(char.isupper() for char in password):
            errors.append("Password must contain at least one uppercase letter")
        if not any(char.islower() for char in password):
            errors.append("Password must contain at least one lowercase letter")
        if not any(char in "!@#$%^&*()_+" for char in password):
            errors.append("Password must contain at least one special character")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def sanitize_input(data):
        """Basic input sanitization"""
        if isinstance(data, str):
            # Remove potentially dangerous characters
            dangerous_chars = ['<', '>', '&', '"', "'"]
            for char in dangerous_chars:
                data = data.replace(char, f'\\{char}')
        return data