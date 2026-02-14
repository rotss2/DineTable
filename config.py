import os

class Config:
    # Brevo email configuration
    BREVO_API_KEY = os.getenv("BREVO_API_KEY", "your_brevo_api_key_here")  # Replace this with your actual API key