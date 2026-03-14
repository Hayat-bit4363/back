import random
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_email(user, code):
    """
    Sends verification email using Brevo's Transactional Email API via HTTPS.
    This bypasses SMTP blocks on platforms like Railway.
    """
    api_key = settings.EMAIL_HOST_PASSWORD
    sender_email = settings.DEFAULT_FROM_EMAIL
    
    url = "https://api.brevo.com/v3/smtp/email"
    
    payload = {
        "sender": {"email": sender_email, "name": "HayatChat"},
        "to": [{"email": user.email}],
        "subject": "Verify your email",
        "textContent": f"Your verification code is: {code}",
        "htmlContent": f"<html><body><h1>Verify your email</h1><p>Your verification code is: <strong>{code}</strong></p></body></html>"
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key
    }

    print(f"\n--------------------------------------")
    print(f"  OTP CODE FOR {user.email}: {code}")
    print(f"--------------------------------------\n")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 201:
            print(f"DEBUG: Email sent successfully via Brevo API to {user.email}")
            return True
        else:
            print(f"DEBUG: Brevo API Error {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"API ERROR: Network issue calling Brevo API for {user.email}: {str(e)}")
        return False
