
"""
Signals for the accounts app
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from apps.accounts.models import User


@receiver(post_save, sender=User)
def assign_user_to_group(sender, instance, created, **kwargs):
    """
    Automatically assign user to appropriate group based on role
    """
    if created:
        # Remove from all groups first
        instance.groups.clear()
        
        # Assign to role-based group
        try:
            group = Group.objects.get(name=instance.get_role_display())
            instance.groups.add(group)
        except Group.DoesNotExist:
            pass
