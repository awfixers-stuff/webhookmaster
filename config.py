import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # JWT Settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-jwt-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 5)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 30)))

    # Discord OAuth2 Settings
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
    DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
    DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "http://127.0.0.1:5000/callback")
    DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    DISCORD_GUILD_ID = os.getenv("DISCORD_GUILD_ID")

    # Discord API URLs
    DISCORD_API_BASE_URL = 'https://discord.com/api'
    DISCORD_AUTHORIZATION_BASE_URL = DISCORD_API_BASE_URL + '/oauth2/authorize'
    DISCORD_TOKEN_URL = DISCORD_API_BASE_URL + '/oauth2/token'
    DISCORD_REVOKE_URL = DISCORD_API_BASE_URL + '/oauth2/token/revoke'
    DISCORD_USER_URL = DISCORD_API_BASE_URL + '/users/@me'
    DISCORD_GUILDS_URL = DISCORD_API_BASE_URL + '/users/@me/guilds'

    # Discord Scopes
    DISCORD_SCOPE = ['identify', 'guilds.join']

    # Email Settings
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
    SMTP_HOST = os.getenv("SMTP_HOST")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

    # Stripe Settings
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

    # Application Settings
    TESTING = os.getenv("TESTING", "False").lower() == "true"

config = Config()