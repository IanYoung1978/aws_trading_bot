import logging
from notifier import send_email

# Configure logging
logging.basicConfig(filename='trade_bot.log', 
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_trade(action, price, currency="USD", amount=None):
    message = f"{action.upper()} - Price: {price} {currency}, Amount: {amount}"
    logging.info(message)
    send_email("Trade Notification", message)
