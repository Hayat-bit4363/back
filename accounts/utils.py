import random
import logging
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(user, code):
    subject = 'Verify your email'
    message = f'Your verification code is: {code}'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    print(f"DEBUG: Attempting to send email to {user.email} using {settings.EMAIL_HOST}")
    
    try:
        # Using fail_silently=False so we catch the actual error in our try/except block
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        print("DEBUG: Email sent successfully!")
        return True
    except Exception as e:
        # This will catch the 'Network is unreachable' error
        print(f"CRITICAL: Failed to send email to {user.email}: {str(e)}")
        logger.error(f"SMTP Error: {str(e)}")
        return False
