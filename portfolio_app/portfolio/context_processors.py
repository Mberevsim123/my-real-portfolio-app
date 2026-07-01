"""
Context processors for global template variables
"""

from .models import Category, SocialLink, SiteSetting
from django.conf import settings


def global_settings(request):
    """Add global settings to all templates"""
    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Backend Portfolio'),
        'SITE_URL': getattr(settings, 'SITE_URL', ''),
        'GOOGLE_ANALYTICS_ID': getattr(settings, 'GOOGLE_ANALYTICS_ID', ''),
        'DEBUG': settings.DEBUG,
    }


def categories(request):
    """Add categories to all templates"""
    return {
        'categories': Category.objects.all(),
    }


def social_links(request):
    """Add social links to all templates"""
    return {
        'social_links': SocialLink.objects.filter(is_active=True),
    }


def site_settings(request):
    """Add public site settings to all templates"""
    public_settings = SiteSetting.objects.filter(is_public=True)
    settings_dict = {setting.key: setting.value for setting in public_settings}
    return {
        'site_settings': settings_dict,
    }