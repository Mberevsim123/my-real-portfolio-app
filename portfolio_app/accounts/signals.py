from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new user is created"""
    if created:
        try:
            UserProfile.objects.create(user=instance)
            logger.info(f"UserProfile created for user: {instance.email}")
        except Exception as e:
            logger.error(f"Error creating UserProfile for {instance.email}: {str(e)}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when user is saved"""
    try:
        if hasattr(instance, 'profile'):
            instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)
        logger.info(f"UserProfile created for user: {instance.email}")