import random
from django.core.mail import send_mail
from django.conf import settings
from .models import OneTimePassword


def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_via_email(user):
    otp_code = generate_otp()
    OneTimePassword.objects.update_or_create(
        user=user,
        defaults={'code': otp_code, 'attempts': 0, 'is_blocked': False}
    )
    subject = "Verify your account"
    message = f"Hi {user.username},\n\nYour verification code is: {otp_code}\n\nPlease enter this to verify your account."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    send_mail(subject, message, email_from, recipient_list)


def send_password_reset_otp(user):
    otp_code = generate_otp()

    OneTimePassword.objects.update_or_create(
        user=user,
        defaults={'code': otp_code, 'attempts': 0, 'is_blocked': False}
    )
    subject = "Reset Your Password"
    message = f"Hi {user.username},\n\nUse this code to reset your password: {otp_code}\n\nIf you did not request this, ignore this email."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    send_mail(subject, message, email_from, recipient_list)

def send_password_success_email(user):
    subject = "Password Reset Successfully"
    message = f"Hi {user.username},\n\nYour password has been successfully reset. You can now login with your new password."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    
    send_mail(subject, message, email_from, recipient_list)
