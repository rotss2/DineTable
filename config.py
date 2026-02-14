import os

class Config:
    # Brevo email configuration
    BREVO_API_KEY = os.getenv("BREVO_API_KEY", "your_brevo_api_key_here")  # Replace this with your actual API keyimport os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') # Secret key for Flask sessions
    DATABASE_URL = os.environ.get('DATABASE_URL') # PostgreSQL URL
    BREVO_API_KEY = os.environ.get('BREVO_API_KEY') # Brevo API Key
    BREVO_SENDER_EMAIL = os.environ.get('BREVO_SENDER_EMAIL') # Brevo Sender Email
    WEBSITE_URL = os.environ.get('WEBSITE_URL') # Website URL (optional)
