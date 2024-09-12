from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # If a new User is created, create a new Profile
        Profile.objects.create(user=instance)
    else:
        # If an existing User is updated, check if a Profile already exists
        if not hasattr(instance, 'profile'):
            # If a Profile does not exist, create a new one
            Profile.objects.create(user=instance)
        else:
            # If a Profile already exists, update the existing Profile
            instance.profile.save()