from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import CustomUser, UserProfile, LoginHistory
from .forms import CustomUserCreationForm, CustomUserChangeForm


class UserProfileInline(admin.StackedInline):
    """Inline admin for user profile with modern styling"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = '👤 Profile Details'
    fieldsets = (
        ('📞 Contact Information', {
            'fields': ('phone_number', 'address', 'city', 'country', 'postal_code')
        }),
        ('⚙️ Preferences', {
            'fields': ('newsletter_subscribed', 'email_notifications')
        }),
        ('🔗 Social Links', {
            'fields': ('instagram', 'youtube', 'medium', 'devto'),
            'classes': ('collapse',)
        }),
    )
    classes = ('wide',)


class LoginHistoryInline(admin.TabularInline):
    """Inline admin for login history"""
    model = LoginHistory
    can_delete = False
    max_num = 10
    fields = ('ip_address', 'user_agent', 'login_time', 'is_successful')
    readonly_fields = fields
    classes = ('collapse',)
    verbose_name_plural = '🔐 Login History'


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Custom admin interface for User model with modern design"""
    
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    list_display = ('avatar_display', 'email', 'username', 'get_full_name', 
                   'status_badge', 'verified_badge', 'date_joined', 'actions_display')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'email_verified', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    list_per_page = 25
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('👤 Personal Information'), {
            'fields': ('first_name', 'last_name', 'bio', 'avatar', 
                      'job_title', 'company', 'years_experience')
        }),
        (_('🔗 Social Links'), {
            'fields': ('website', 'github', 'linkedin', 'twitter'),
            'classes': ('collapse',)
        }),
        (_('🔐 Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 
                      'groups', 'user_permissions'),
        }),
        (_('📅 Important Dates'), {
            'fields': ('last_login', 'date_joined', 'email_verified', 'last_seen'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )
    
    inlines = [UserProfileInline, LoginHistoryInline]
    readonly_fields = ('last_login', 'date_joined', 'last_seen')
    
    actions = ['activate_users', 'deactivate_users', 'send_verification_email']
    
    def avatar_display(self, obj):
        """Display avatar with status indicator"""
        if obj.avatar:
            html = f'''
            <div style="position: relative; display: inline-block;">
                <img src="{obj.avatar.url}" width="40" height="40" style="border-radius: 50%; object-fit: cover; border: 2px solid #e2e8f0;" />
                <span style="position: absolute; bottom: -2px; right: -2px; width: 14px; height: 14px; background: {'#10b981' if obj.is_active else '#ef4444'}; border-radius: 50%; border: 2px solid white;"></span>
            </div>
            '''
        else:
            html = f'''
            <div style="position: relative; display: inline-block;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #6366f1, #8b5cf6); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 1rem; border: 2px solid #e2e8f0;">
                    {obj.email[:1].upper()}
                </div>
                <span style="position: absolute; bottom: -2px; right: -2px; width: 14px; height: 14px; background: {'#10b981' if obj.is_active else '#ef4444'}; border-radius: 50%; border: 2px solid white;"></span>
            </div>
            '''
        return mark_safe(html)
    avatar_display.short_description = _('Avatar')
    
    def status_badge(self, obj):
        """Display status badge"""
        color = '#10b981' if obj.is_active else '#ef4444'
        text = 'Active' if obj.is_active else 'Inactive'
        return mark_safe(f'<span style="background: {color}; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">{text}</span>')
    status_badge.short_description = _('Status')
    
    def verified_badge(self, obj):
        """Display verified badge"""
        if obj.email_verified:
            return mark_safe('<span style="background: #10b981; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">✓ Verified</span>')
        return mark_safe('<span style="background: #f59e0b; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">⏳ Pending</span>')
    verified_badge.short_description = _('Email')
    
    def actions_display(self, obj):
        """Display action buttons"""
        url = reverse('admin:accounts_customuser_change', args=[obj.pk])
        return mark_safe(f'''
        <a href="{url}" style="display: inline-block; padding: 4px 12px; background: #3b82f6; color: white; border-radius: 6px; text-decoration: none; font-size: 0.75rem; font-weight: 500;">✏️ Edit</a>
        ''')
    actions_display.short_description = _('Actions')
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = _('Full Name')
    get_full_name.admin_order_field = 'first_name'
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'✅ {updated} users were successfully activated.')
    activate_users.short_description = _('🔓 Activate selected users')
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'🔒 {updated} users were successfully deactivated.')
    deactivate_users.short_description = _('🔒 Deactivate selected users')
    
    def send_verification_email(self, request, queryset):
        from .services import AccountService
        for user in queryset:
            if not user.email_verified:
                AccountService.send_verification_email(request, user)
        self.message_user(request, f'📧 Verification emails sent to {queryset.count()} users.')
    send_verification_email.short_description = _('📧 Send verification email')


@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    """Admin for login history with modern design"""
    
    list_display = ('user_link', 'ip_address', 'login_time', 'status_badge')
    list_filter = ('is_successful', 'login_time')
    search_fields = ('user__email', 'ip_address', 'user_agent')
    readonly_fields = ('user', 'ip_address', 'user_agent', 'location', 'login_time', 'is_successful')
    date_hierarchy = 'login_time'
    list_per_page = 25
    
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
        return mark_safe(f'<a href="{url}" style="color: #3b82f6; text-decoration: none; font-weight: 500;">{obj.user.email}</a>')
    user_link.short_description = _('User')
    
    def status_badge(self, obj):
        if obj.is_successful:
            return mark_safe('<span style="background: #10b981; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">✅ Success</span>')
        return mark_safe('<span style="background: #ef4444; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">❌ Failed</span>')
    status_badge.short_description = _('Status')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for user profiles with modern design"""
    
    list_display = ('user_link', 'phone_number', 'city', 'country', 'subscription_badge')
    list_filter = ('newsletter_subscribed', 'email_notifications', 'country')
    search_fields = ('user__email', 'user__username', 'phone_number', 'city')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    fieldsets = (
        ('👤 User Information', {
            'fields': ('user',)
        }),
        ('📞 Contact Information', {
            'fields': ('phone_number', 'address', 'city', 'country', 'postal_code')
        }),
        ('⚙️ Preferences', {
            'fields': ('newsletter_subscribed', 'email_notifications')
        }),
        ('🔗 Social Links', {
            'fields': ('instagram', 'youtube', 'medium', 'devto'),
            'classes': ('collapse',)
        }),
        ('📅 Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        url = reverse('admin:accounts_customuser_change', args=[obj.user.pk])
        return mark_safe(f'<a href="{url}" style="color: #3b82f6; text-decoration: none; font-weight: 500;">{obj.user.email}</a>')
    user_link.short_description = _('User')
    
    def subscription_badge(self, obj):
        if obj.newsletter_subscribed:
            return mark_safe('<span style="background: #10b981; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">✅ Subscribed</span>')
        return mark_safe('<span style="background: #94a3b8; color: white; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 500;">Not Subscribed</span>')
    subscription_badge.short_description = _('Newsletter')


# Admin Site Customization
admin.site.site_header = '🚀 Portfolio Admin'
admin.site.site_title = 'Portfolio Admin Panel'
admin.site.index_title = '✨ Welcome to Portfolio Management System'