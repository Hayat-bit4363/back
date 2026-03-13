import random
from django.core.mail import send_mail
from django.conf import settings

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(user, code):
    subject = 'Verify your email'
    message = f'Your verification code is: {code}'
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user.email]
    
    # For now, we print to console if no email backend is configured or just rely on Django's console backend
    print(f"Sending email to {user.email}: {message}")
    
    send_mail(subject, message, email_from, recipient_list)
