from flask import Flask, request, jsonify, redirect, url_for
import importlib
import smtplib
from email.message import EmailMessage
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity, get_jwt
from requests_oauthlib import OAuth2Session
import requests
import stripe

from config import config

app = Flask(__name__)

# Stripe API Key
stripe.api_key = config.STRIPE_SECRET_KEY

# In-memory storage for paid users (replace with a database in production)
paid_users = set()

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = config.JWT_REFRESH_TOKEN_EXPIRES
jwt = JWTManager(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

@app.route('/webhook', methods=['POST'])
@limiter.limit("10 per minute")
def webhook():
    """
    Ingests a webhook, transforms its payload, and sends it to a new destination.
    """
    data = request.get_json()

    # Get the source and format from the query parameters
    source = request.args.get('source', 'default')
    output_format = request.args.get('format', 'default')

    ALLOWED_SOURCES = ['default', 'github', 'stripe', 'shopify', 'wix', 'cloudflare', 'webflow']
    ALLOWED_FORMATS = ['default', 'slack', 'discord', 'msteams', 'email']

    if source not in ALLOWED_SOURCES or output_format not in ALLOWED_FORMATS:
        return jsonify({'error': 'Invalid source or format'}), 400

    # Dynamically load the parser and formatter
    parser_module = importlib.import_module(f"transformers.parsers.{source}")
    formatter_module = importlib.import_module(f"transformers.formatters.{output_format}")

    # Parse the incoming webhook
    parsed_data = parser_module.parse_payload(data)

    # Format the outgoing payload
    formatted_data = formatter_module.format_payload(parsed_data)

    # Send the transformed payload to the new destination
    send_payload(formatted_data, output_format)

    return jsonify({'status': 'success'}), 200

def send_payload(data, output_format):
    """
    Sends the payload to the new destination.
    """
    if output_format == 'email':
        sender_email = config.EMAIL_SENDER
        sender_password = config.EMAIL_PASSWORD
        receiver_email = config.EMAIL_RECEIVER
        smtp_host = config.SMTP_HOST
        smtp_port = config.SMTP_PORT

        if not all([sender_email, sender_password, receiver_email, smtp_host]):
            print("Email configuration missing. Please set EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, and SMTP_HOST environment variables.")
            return

        msg = EmailMessage()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = data.get('subject', 'Webhook Notification')
        msg.set_content(data.get('body', str(data)))

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as smtp:
                smtp.starttls() # Use starttls for port 587
                smtp.login(sender_email, sender_password)
                smtp.send_message(msg)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")
    else:
        # For now, we'll just print it to the console.
        print(f"Sending payload: {data}")


# Discord OAuth2 settings
DISCORD_API_BASE_URL = config.DISCORD_API_BASE_URL
DISCORD_AUTHORIZATION_BASE_URL = config.DISCORD_AUTHORIZATION_BASE_URL
DISCORD_TOKEN_URL = config.DISCORD_TOKEN_URL
DISCORD_REVOKE_URL = config.DISCORD_REVOKE_URL
DISCORD_USER_URL = config.DISCORD_USER_URL
DISCORD_GUILDS_URL = config.DISCORD_GUILDS_URL

# Scopes for Discord OAuth2
# 'identify' for user information
# 'guilds.join' for adding user to a guild
DISCORD_SCOPE = config.DISCORD_SCOPE

@app.route('/login')
def login():
    client_id = config.DISCORD_CLIENT_ID
    redirect_uri = config.DISCORD_REDIRECT_URI
    if not client_id or not redirect_uri:
        return jsonify({"error": "Discord client ID or redirect URI not configured"}), 500

    discord = OAuth2Session(client_id, scope=DISCORD_SCOPE, redirect_uri=redirect_uri)
    authorization_url, state = discord.authorization_url(DISCORD_AUTHORIZATION_BASE_URL)
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    client_id = config.DISCORD_CLIENT_ID
    client_secret = config.DISCORD_CLIENT_SECRET
    redirect_uri = config.DISCORD_REDIRECT_URI

    if not client_id or not client_secret or not redirect_uri:
        return jsonify({"error": "Discord OAuth2 credentials not configured"}), 500

    discord = OAuth2Session(client_id, redirect_uri=redirect_uri)
    try:
        token = discord.fetch_token(
            config.DISCORD_TOKEN_URL,
            client_secret=client_secret,
            authorization_response=request.url
        )
    except Exception as e:
        return jsonify({"error": f"Failed to fetch Discord token: {e}"}), 400

    # Fetch user information
    user_info = discord.get(config.DISCORD_USER_URL).json()
    user_id = user_info['id']
    username = user_info['username']

    # Add user to Discord guild (placeholder)
    add_user_to_discord_guild(user_id, token['access_token'])

    # Create JWTs
    access_token = create_access_token(identity=user_id, expires_delta=app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    refresh_token = create_access_token(identity=user_id, expires_delta=app.config["JWT_REFRESH_TOKEN_EXPIRES"], fresh=False)

    return jsonify(access_token=access_token, refresh_token=refresh_token)

@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity, expires_delta=app.config["JWT_ACCESS_TOKEN_EXPIRES"])
    return jsonify(access_token=access_token)

@app.route('/create-checkout-session', methods=['POST'])
@jwt_required()
def create_checkout_session():
    current_user_id = get_jwt_identity()
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Premium Access',
                        },
                        'unit_amount': 500,  # $5.00
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=request.url_root + 'success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.url_root + 'cancel',
            client_reference_id=current_user_id,
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('stripe-signature')
    webhook_secret = config.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        return 'Invalid payload', 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return 'Invalid signature', 400

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session.get('client_reference_id')
        if user_id:
            paid_users.add(user_id)
            print(f"User {user_id} has successfully paid and gained premium access.")
            # In a real application, you would update your database here
        else:
            print("No user ID found in checkout session.")

    return 'OK', 200

@app.route('/success')
def success():
    return jsonify(message="Payment successful!")

@app.route('/cancel')
def cancel():
    return jsonify(message="Payment cancelled.")

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    if current_user not in paid_users:
        return jsonify(message="Access denied. Please subscribe."), 403
    return jsonify(logged_in_as=current_user, message="Welcome, premium user!"), 200

def add_user_to_discord_guild(user_id, access_token):
    guild_id = config.DISCORD_GUILD_ID
    bot_token = config.DISCORD_BOT_TOKEN

    if not guild_id or not bot_token:
        print("Discord guild ID or bot token not configured. Skipping adding user to guild.")
        return

    # This is a placeholder. Actual implementation requires a Discord bot with 'Manage Guild' permissions
    # and the 'guilds.join' OAuth2 scope.
    # The bot needs to be in the guild.
    # The user needs to grant the 'guilds.join' scope during OAuth2.
    # The bot token should be used for authorization, not the user's access_token for this specific API call.
    # The user's access_token is used to identify the user to be added.

    headers = {
        "Authorization": f"Bot {bot_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "access_token": access_token
    }
    url = f"{config.DISCORD_API_BASE_URL}/guilds/{guild_id}/members/{user_id}"

    try:
        response = requests.put(url, headers=headers, json=payload)
        response.raise_for_status()
        if response.status_code == 201:
            print(f"User {user_id} successfully added to Discord guild {guild_id}")
        elif response.status_code == 204:
            print(f"User {user_id} is already a member of Discord guild {guild_id}")
    except requests.exceptions.HTTPError as e:
        print(f"Error adding user to Discord guild: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred while adding user to Discord guild: {e}")

if __name__ == '__main__':
    app.run(debug=config.TESTING)