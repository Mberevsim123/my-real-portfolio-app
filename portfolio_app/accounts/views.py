from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.views import LoginView, PasswordResetView
from django.views.generic import TemplateView, FormView
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model

from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm,
    CustomUserChangeForm, UserProfileForm, EmailChangeForm,
    CustomPasswordResetForm, CustomSetPasswordForm
)
from .services import AccountService, SecurityService
from .models import UserProfile, LoginHistory

import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class CustomLoginView(LoginView):
    """Custom login view with rate limiting and analytics"""
    authentication_form = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        """Handle successful login"""
        response = super().form_valid(form)
        
        AccountService.record_login_attempt(
            user=form.get_user(),
            request=self.request,
            success=True
        )
        
        messages.success(self.request, f'Welcome back, {form.get_user().get_full_name()}!')
        logger.info(f"User logged in: {form.get_user().email}")
        
        return response
    
    def form_invalid(self, form):
        """Handle failed login attempt"""
        email = form.cleaned_data.get('username')
        try:
            user = User.objects.get(email=email)
            AccountService.record_login_attempt(
                user=user,
                request=self.request,
                success=False
            )
        except User.DoesNotExist:
            pass
        
        messages.error(self.request, 'Invalid email or password. Please try again.')
        return super().form_invalid(form)


@csrf_protect
def register_view(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('portfolio:home')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                is_strong, errors = SecurityService.validate_password_strength(
                    form.cleaned_data['password1']
                )
                
                if not is_strong:
                    for error in errors:
                        messages.error(request, error)
                    return render(request, 'accounts/register.html', {'form': form})
                
                user = form.save(commit=False)
                user.email = form.cleaned_data['email']
                user.save()
                
                UserProfile.objects.create(user=user)
                AccountService.send_verification_email(request, user)
                login(request, user)
                
                messages.success(
                    request,
                    'Registration successful! Please check your email to verify your account.'
                )
                logger.info(f"New user registered: {user.email}")
                
                return redirect('portfolio:home')
            except Exception as e:
                logger.error(f"Registration error: {str(e)}")
                messages.error(request, 'An error occurred during registration. Please try again.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def profile_view(request):
    """User profile view and edit"""
    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            logger.info(f"Profile updated for user: {user.email}")
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = CustomUserChangeForm(instance=user)
        profile_form = UserProfileForm(instance=profile)
    
    stats = AccountService.get_user_statistics(user)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'stats': stats,
        'profile': profile,
    }
    
    return render(request, 'accounts/profile.html', context)


@login_required
def change_email_view(request):
    """View for changing user email"""
    if request.method == 'POST':
        form = EmailChangeForm(request.POST)
        if form.is_valid():
            new_email = form.cleaned_data['new_email']
            success, message = AccountService.change_email(request.user, new_email)
            
            if success:
                messages.success(request, message)
                logger.info(f"Email changed for user {request.user.pk}")
                return redirect('accounts:profile')
            else:
                messages.error(request, message)
    else:
        form = EmailChangeForm()
    
    return render(request, 'accounts/change_email.html', {'form': form})


@login_required
def account_security_view(request):
    """Account security settings view"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('accounts:security')
        
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('accounts:security')
        
        is_strong, errors = SecurityService.validate_password_strength(new_password)
        if not is_strong:
            for error in errors:
                messages.error(request, error)
            return redirect('accounts:security')
        
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        
        messages.success(request, 'Your password has been changed successfully!')
        logger.info(f"Password changed for user {request.user.email}")
        
        return redirect('accounts:profile')
    
    login_history = LoginHistory.objects.filter(user=request.user)[:10]
    
    return render(request, 'accounts/security.html', {'login_history': login_history})


@login_required
@require_http_methods(['POST'])
def logout_view(request):
    """Custom logout view"""
    logger.info(f"User logged out: {request.user.email}")
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('portfolio:home')


def verify_email_view(request, uidb64, token):
    """Email verification view"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user and default_token_generator.check_token(user, token):
        AccountService.verify_email(user)
        messages.success(request, 'Your email has been verified successfully!')
        logger.info(f"Email verified for user: {user.email}")
    else:
        messages.error(request, 'The verification link is invalid or has expired.')
    
    return redirect('accounts:profile')


class CustomPasswordResetView(PasswordResetView):
    """Custom password reset view"""
    form_class = CustomPasswordResetForm
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = '/accounts/password-reset/done/'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Password reset email has been sent. Please check your inbox.'
        )
        return response


@login_required
@require_http_methods(['POST'])
def delete_account_view(request):
    """Account deletion view"""
    password = request.POST.get('password')
    
    if request.user.check_password(password):
        reason = request.POST.get('reason', '')
        email = request.user.email
        
        AccountService.deactivate_account(request.user, reason)
        logout(request)
        
        messages.info(request, 'Your account has been deactivated.')
        logger.info(f"Account deactivated: {email}")
        
        return redirect('portfolio:home')
    else:
        messages.error(request, 'Incorrect password. Account not deactivated.')
        return redirect('accounts:profile')