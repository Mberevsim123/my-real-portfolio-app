from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.cache import cache
from django.conf import settings
from .models import Project, BlogPost, Skill


def is_dummy_cache():
    """Check if we're using DummyCache"""
    return cache.__class__.__name__ == 'DummyCache'


def safe_cache_delete_pattern(pattern):
    """Safely delete cache by pattern with fallback"""
    if is_dummy_cache():
        return
    
    try:
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
    except AttributeError:
        pass


def safe_cache_delete(key):
    """Safely delete a cache key"""
    try:
        cache.delete(key)
    except AttributeError:
        pass


@receiver(post_save, sender=Project)
def clear_project_cache(sender, instance, **kwargs):
    """Clear cache when project is saved"""
    safe_cache_delete('homepage_data')
    safe_cache_delete_pattern('project_*')


@receiver(post_save, sender=BlogPost)
def clear_blog_cache(sender, instance, **kwargs):
    """Clear cache when blog post is saved"""
    safe_cache_delete('homepage_data')
    safe_cache_delete_pattern('blog_*')


@receiver(post_save, sender=Skill)
def clear_skills_cache(sender, instance, **kwargs):
    """Clear skills cache when skills are updated"""
    safe_cache_delete_pattern('about_page_data')