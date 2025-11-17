import os
from twilio.rest import Client
from fastapi import HTTPException

# Twilio configuration (replace with your credentials)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "your_account_sid")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "your_auth_token")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "your_twilio_phone_number")
ADMIN_PHONE_NUMBER = os.getenv("ADMIN_PHONE_NUMBER", "admin_phone_number")

def send_notification(subject: str, message: str, additional_info: dict = None):
    """
    Send a notification to the admin via SMS using Twilio.
    """
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        full_message = f"{subject}\n{message}"
        if additional_info:
            full_message += f"\nDetails: {additional_info}"
        
        client.messages.create(
            body=full_message,
            from_=TWILIO_PHONE_NUMBER,
            to=ADMIN_PHONE_NUMBER
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")
