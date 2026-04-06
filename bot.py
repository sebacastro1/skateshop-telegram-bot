"""
Telegram Bot para Notificaciones de Pedidos de Shopify
Envia detalles del pedido a Telegram cuando se crea un nuevo pedido
"""

import os
import json
import hmac
import hashlib
import asyncio
import requests
import threading
from flask import Flask, request
from telegram import Bot
from telegram.error import TelegramError
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variables de entorno
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SHOPIFY_WEBHOOK_SECRET = os.getenv('SHOPIFY_WEBHOOK_SECRET')
SHOPIFY_API_TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOPIFY_STORE = 'legit-skateshop.myshopify.com'

# Validar variables requeridas
if not TELEGRAM_TOKEN:
    logger.warning("TELEGRAM_TOKEN no configurado")
if not TELEGRAM_CHAT_ID:
    logger.warning("TELEGRAM_CHAT_ID no configurado")
if not SHOPIFY_WEBHOOK_SECRET:
    logger.warning("SHOPIFY_WEBHOOK_SECRET no configurado")
if not SHOPIFY_API_TOKEN:
    logger.warning("SHOPIFY_API_TOKEN no configurado - las imagenes no estaran disponibles")

# Inicializar bot de Telegram
telegram_bot = Bot(token=TELEGRAM_TOKEN) if TELEGRAM_TOKEN else None


def verify_shopify_webhook(request_data, signature):
    """
    Verificar que el webhook viene de Shopify
    """
    if not SHOPIFY_WEBHOOK_SECRET:
        logger.warning("Sin webhook secret, saltando verificacion")
        return True

    hash_object = hmac.new(
        SHOPIFY_WEBHOOK_SECRET.encode('utf-8'),
        msg=request_data,
        digestmod=hashlib.sha256
    )
    expected_signature = hash_object.digest()
    expected_signature_b64 = __import__('base64').b64encode(expected_signature).decode()

    return hmac.compare_digest(expected_signature_b64, signature)


def get_product_image(product_id):
    """
    Obtener la imagen del producto desde la API de Shopify
    """
    if not SHOPIFY_API_TOKEN or not product_id:
        return None

    try:
        url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/products/{product_id}.json"
        headers = {
            'X-Shopify-Access-Token': SHOPIFY_API_TOKEN,
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers, timeout=5)

        if response.status_code == 200:
            product = response.json().get('product', {})
            images = product.get('images', [])
            if images:
                return images[0].get('src')
    except Exception as e:
        logger.error(f"Error obteniendo imagen del producto: {e}")

    return None


def format_order_message(order_data):
    """
    Formatear los datos del pedido en un mensaje legible en español
    """
    order_number = order_data.get('order_number', 'N/A')

    # Informacion del cliente
    customer = order_data.get('customer', {})
    customer_name = customer.get('first_name', '') + ' ' + customer.get('last_name', '')
    customer_email = customer.get('email', 'N/A')
    customer_phone = customer.get('phone', 'N/A')
    customer_rut = customer.get('default_address', {}).get('company', 'N/A') if customer.get('default_address') else 'N/A'

    # Productos
    line_items = order_data.get('line_items', [])
    products_text = ""
    has_multiple_units = False

    for item in line_items:
        title = item.get('title', 'Producto desconocido')
        quantity = item.get('quantity', 0)
        price = float(item.get('price', 0))
        sku = item.get('sku', 'N/A')
        products_text += f"  • {title} (SKU: {sku}) x{quantity} - ${int(price):,}\n\n"

        # Verificar si hay múltiples unidades
        if quantity > 1:
            has_multiple_units = True

    # Agregar alerta si hay múltiples unidades
    alert_text = "⚠️ OJO: Hay productos con múltiples unidades\n\n" if has_multiple_units else ""

    # Direccion de envio
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

    # Total del pedido
    total_price = float(order_data.get('total_price', 0))

    # Construir el mensaje en espanol
    message = f"""🛹 NUEVO PEDIDO #{order_number}

👤 Cliente: {customer_name.strip()}
🆔 RUT: {customer_rut}
📧 {customer_email}
📞 {customer_phone if customer_phone != 'None' else 'N/A'}

{alert_text}📦 PRODUCTOS:
{products_text}
📍 DIRECCION DE ENVIO:
{address_text}

💰 TOTAL: ${int(total_price):,}"""

    return message


def send_telegram_message(message, image_url=None):
    """
    Enviar mensaje a Telegram en background (no bloquea el webhook)
    """
    try:
        if telegram_bot and TELEGRAM_CHAT_ID:
            if image_url:
                asyncio.run(telegram_bot.send_photo(
                    chat_id=TELEGRAM_CHAT_ID,
                    photo=image_url,
                    caption=message
                ))
            else:
                asyncio.run(telegram_bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=message
                ))
            logger.info("Mensaje enviado a Telegram exitosamente")
        else:
            logger.error("Bot de Telegram no configurado correctamente")
    except Exception as e:
        logger.error(f"Error enviando mensaje a Telegram: {e}")


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """
    Recibir webhook de Shopify para nuevos pedidos
    Responde inmediatamente a Shopify y envía el mensaje en background
    """
    try:
        # Obtener datos y firma del request
        request_data = request.get_data()
        signature = request.headers.get('X-Shopify-Hmac-SHA256', '')

        # Verificar la firma del webhook
        if not verify_shopify_webhook(request_data, signature):
            logger.warning("Firma del webhook invalida")
            return {'status': 'error', 'message': 'Firma invalida'}, 401

        # Parsear los datos JSON
        order_data = json.loads(request_data)
        order_number = order_data.get('order_number', 'N/A')

        # Formatear el mensaje
        message = format_order_message(order_data)

        # Obtener imagen del primer producto
        line_items = order_data.get('line_items', [])
        image_url = None
        if line_items:
            product_id = line_items[0].get('product_id')
            image_url = get_product_image(product_id)

        # Enviar a Telegram en un thread separado (no bloquea la respuesta)
        thread = threading.Thread(
            target=send_telegram_message,
            args=(message, image_url)
        )
        thread.daemon = True
        thread.start()

        logger.info(f"Pedido #{order_number} recibido y en cola para procesar")
        # Responder INMEDIATAMENTE a Shopify (sin esperar a Telegram)
        return {'status': 'success', 'message': 'Pedido recibido'}, 200

    except json.JSONDecodeError:
        logger.error("JSON invalido en el webhook")
        return {'status': 'error', 'message': 'JSON invalido'}, 400
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'saludable'}, 200


@app.route('/', methods=['GET'])
def home():
    return {
        'nombre': 'Bot de Pedidos Skateshop',
        'estado': 'funcionando',
        'version': '2.0'
    }, 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
