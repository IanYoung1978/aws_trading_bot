import os

# Kraken API credentials
KRAKEN_API_KEY = os.environ.get("KRAKEN_API_KEY")
KRAKEN_PRIVATE_KEY = os.environ.get("KRAKEN_PRIVATE_KEY")

# Email notification settings
EMAIL_SMTP_SERVER = os.environ.get("EMAIL_SMTP_SERVER", "smtp.gmail.com")  # Default to Gmail
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", 587))  # Default to 587
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Trade bot parameters
X_PERCENT = float(os.environ.get("X_PERCENT", 1.5))  # Default X% threshold
Y_PERCENT = float(os.environ.get("Y_PERCENT", 5.0))  # Default Y% threshold

# Validate required environment variables
REQUIRED_VARS = ["KRAKEN_API_KEY", "KRAKEN_PRIVATE_KEY", "EMAIL_ADDRESS", "EMAIL_PASSWORD"]
missing_vars = [var for var in REQUIRED_VARS if not os.environ.get(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
