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
    
    print(f"\n--------------------------------------")
    print(f"  OTP CODE FOR {user.email}: {code}")
    print(f"--------------------------------------\n")
    
    try:
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        print(f"DEBUG: Email sent successfully to {user.email}")
        return True
    except Exception as e:
        print(f"SMTP ERROR: Network issue sending email to {user.email}: {str(e)}")
        print(f"NOTE: Proceeding anyway for testing. Use the code logged above.")
        return False
