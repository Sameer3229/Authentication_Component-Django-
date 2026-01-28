from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .utils import send_otp_via_email

User = get_user_model()

@receiver(post_save, sender=User)
def send_otp_on_singup(sender, instance, created, **kwargs):
    if created:
        send_otp_via_email(instance)