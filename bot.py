"""
Telegram Bot for Shopify Order Notifications
Sends order details to Telegram when new orders are created on Shopify
"""

import os
import json
import hmac
import hashlib
from flask import Flask, request
from telegram import Bot
from telegram.error import TelegramError
import logging
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load environment variables
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SHOPIFY_WEBHOOK_SECRET = os.getenv('SHOPIFY_WEBHOOK_SECRET')

# Validate required environment variables
if not TELEGRAM_TOKEN:
    logger.warning("TELEGRAM_TOKEN not set")
if not TELEGRAM_CHAT_ID:
    logger.warning("TELEGRAM_CHAT_ID not set")
if not SHOPIFY_WEBHOOK_SECRET:
    logger.warning("SHOPIFY_WEBHOOK_SECRET not set")

# Initialize Telegram bot
telegram_bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None


def verify_shopify_webhook(request_data, signature):
    """
    Verify that the webhook came from Shopify
    Uses HMAC-SHA256 signature verification
    """
    if not SHOPIFY_WEBHOOK_SECRET:
        logger.warning("No webhook secret configured, skipping verification")
        return True

    hash_object = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode('utf-8'),
        msg=request_data,
        digestmod=hashlib.sha256
    )
    expected_signature = hash_object.digest()
    expected_signature_b64 = __import__('base64').b64encode(expected_signature).decode()

    return hmac.compare_digest(expected_signature_b64, signature)


def format_order_message(order_data):
    """
    Format Shopify order data into a readable Telegram message
    """
    order_number = order_data.get('order_number', 'N/A')

    # Customer information
    customer = order_data.get('customer', {})
    customer_name = customer.get('first_name', '') + ' ' + customer.get('last_name', '')
    customer_email = customer.get('email', 'N/A')
    customer_phone = customer.get('phone', 'N/A')

    # Products
    line_items = order_data.get('line_items', [])
    products_text = ""
    for item in line_items:
        title = item.get('title', 'Unknown Product')
        quantity = item.get('quantity', 0)
        price = float(item.get('price', 0))
        products_text += f"  • {title} x{quantity} - ${price:.2f}\n"

    # Shipping address
    shipping_address = order_data.get('shipping_address', {})
    address_line1 = shipping_address.get('address1', '')
    address_line2 = shipping_address.get('address2', '')
    city = shipping_address.get('city', '')
    province = shipping_address.get('province', '')
    zip_code = shipping_address.get('zip', '')
    country = shipping_address.get('country', '')

    address_text = f"{address_line1}"
    if address_line2:
        address_text += f" {address_line2}"
    address_text += f"\n{city}, {province} {zip_code}\n{country}"

    # Order total
    total_price = float(order_data.get('total_price', 0))

    # Build the message
    message = f"""🛹 NEW ORDER #{order_number}

👤 Customer: {customer_name.strip()}
📧 {customer_email}
📞 {customer_phone if customer_phone != 'None' else 'N/A'}

📦 PRODUCTS:
{products_text}
📍 SHIPPING TO:
{address_text}

💰 TOTAL: ${total_price:.2f}"""

    return message


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Receive Shopify webhook for new orders
    """
    try:
        # Get the request data and signature
        request_data = request.get_data()
        signature = request.headers.get('X-Shopify-Hmac-SHA256', '')

        # Verify the webhook signature
        if not verify_shopify_webhook(request_data, signature):
            logger.warning("Invalid webhook signature")
            return {'status': 'error', 'message': 'Invalid signature'}, 401

        # Parse the JSON data
        order_data = json.loads(request_data)

        # Format the message
        message = format_order_message(order_data)

        # Send to Telegram
        if telegram_bot and TELEGRAM_CHAT_ID:
            try:
                asyncio.run(telegram_bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=message,
                    parse_mode='HTML'
                    )
                )
                logger.info(f"Order notification sent for order #{order_data.get('order_number')}")
                return {'status': 'success', 'message': 'Notification sent'}, 200
            except TelegramError as e:
                logger.error(f"Telegram error: {e}")
                return {'status': 'error', 'message': f'Telegram error: {e}'}, 500
        else:
            logger.error("Telegram bot not properly configured")
            return {'status': 'error', 'message': 'Bot not configured'}, 500

    except json.JSONDecodeError:
        logger.error("Invalid JSON in webhook")
        return {'status': 'error', 'message': 'Invalid JSON'}, 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for Render to verify the bot is running
    """
    return {'status': 'healthy'}, 200


@app.route('/', methods=['GET'])
def home():
    """
    Simple home page
    """
    return {
        'name': 'Skateshop Order Bot',
        'status': 'running',
        'version': '1.0'
    }, 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
