from flask import Flask, render_template, request, redirect, url_for, flash
from brevo import brevo
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

# Setup Brevo email service
brevo_client = brevo.Client(api_key=app.config["BREVO_API_KEY"])

@app.route('/')
def home():
    return redirect(url_for('public_reserve'))

@app.route('/reserve', methods=['GET', 'POST'])
def public_reserve():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        guests = request.form.get('guests')

        # Simulate saving reservation (we're skipping DB for now)
        flash(f"Reservation for {name} (guests: {guests}) is successfully submitted!", "success")

        # Send confirmation email via Brevo
        send_confirmation_email(name, email)

        return redirect(url_for('public_status'))

    return render_template('public_reserve.html')

def send_confirmation_email(name, email):
    try:
        # Confirmation email message
        message = {
            "sender": {"email": "your_email@domain.com"},  # Replace with your own email
            "to": [{"email": email}],
            "subject": "Table Reservation Confirmation",
            "htmlContent": f"<p>Hi {name}, your reservation has been confirmed!</p>"
        }

        brevo_client.send_email(message)
    except Exception as e:
        flash(f"Error sending confirmation email: {e}", "danger")

@app.route('/status')
def public_status():
    return render_template('public_status.html')

if __name__ == '__main__':
    app.run(debug=True)