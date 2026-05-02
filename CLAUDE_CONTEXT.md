# CONTEXTO COMPLETO — PROYECTO SKATESHOP TELEGRAM BOT
# Carga este archivo a Claude para que entienda todo el proyecto

---

## QUIÉN SOY Y QUÉ HACE ESTE PROYECTO

Tengo una tienda de skate online llamada **Legit Skateshop** en Shopify:
- URL tienda: legit-skateshop.myshopify.com
- Mi papá es el bodeguero y prepara los pedidos para despacho
- Yo estoy en Australia (diferencia horaria grande con Chile)

**Problema original:** Cuando llegaba un pedido nuevo, yo tenía que tomar un screenshot de Shopify y mandarlo a mi papá por WhatsApp. Si el pedido llegaba de madrugada en Australia, mi papá no se enteraba hasta que yo me despertara, atrasando el despacho horas o incluso un día completo.

**Solución:** Un bot de Telegram que automáticamente avisa al grupo cuando llega un pedido nuevo. Mi papá solo tiene Telegram instalado y recibe los detalles completos del pedido al instante, sin que yo intervenga.

---

## ARQUITECTURA DEL SISTEMA

```
Cliente compra en Shopify
        ↓
Shopify dispara webhook (POST JSON)
        ↓
Bot corriendo en Render.com (Flask/Gunicorn)
        ↓
Bot formatea el mensaje y lo envía
        ↓
Grupo privado de Telegram (yo + mi papá)
```

---

## STACK TÉCNICO

- **Lenguaje:** Python 3.14
- **Web framework:** Flask 3.0.0 (recibe los webhooks de Shopify)
- **WSGI server:** Gunicorn 22.0.0 (mantiene Flask corriendo 24/7)
- **Bot:** python-telegram-bot 21.0 (envía mensajes a Telegram)
- **Hosting:** Render.com (free tier, 24/7, gratis)
- **Repo:** github.com/sebacastro1/skateshop-telegram-bot

---

## URLS IMPORTANTES

| Servicio | URL |
|----------|-----|
| Render Dashboard | https://dashboard.render.com/web/srv-d793v714tr6s73clg3sg |
| GitHub Repo | https://github.com/sebacastro1/skateshop-telegram-bot |
| Shopify Admin | https://legit-skateshop.myshopify.com/admin |
| Bot Webhook URL | https://skateshop-telegram-bot.onrender.com/webhook |
| Bot Health | https://skateshop-telegram-bot.onrender.com/health |

---

## VARIABLES DE ENTORNO (configuradas en Render → Environment)

| Variable | Descripción | Dónde recuperarla si se pierde |
|----------|-------------|-------------------------------|
| `TELEGRAM_TOKEN` | Token del bot de Telegram | @BotFather → /mybots → tu bot → API Token |
| `TELEGRAM_CHAT_ID` | ID del grupo privado = `-4996651405` | Abrir grupo en web.telegram.org/k/ → número en URL |
| `SHOPIFY_WEBHOOK_SECRET` | Secret para verificar webhooks | Shopify Admin → Configuración → Webhooks → abajo de la lista |
| `SHOPIFY_API_TOKEN` | Para imágenes de productos (NO configurado aún) | Shopify Admin → Apps → Desarrollar apps |

---

## CÓDIGO ACTUAL (bot.py completo)

```python
"""
Telegram Bot para Notificaciones de Pedidos de Shopify
"""

import os
import json
import hmac
import hashlib
import asyncio
import requests
import threading
import time
from flask import Flask, request
from telegram import Bot
from telegram.error import TelegramError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SHOPIFY_WEBHOOK_SECRET = os.getenv('SHOPIFY_WEBHOOK_SECRET')
SHOPIFY_API_TOKEN = os.getenv('SHOPIFY_API_TOKEN')
SHOPIFY_STORE = 'legit-skateshop.myshopify.com'

if not TELEGRAM_TOKEN:
    logger.warning("TELEGRAM_TOKEN no configurado")
if not TELEGRAM_CHAT_ID:
    logger.warning("TELEGRAM_CHAT_ID no configurado")
if not SHOPIFY_WEBHOOK_SECRET:
    logger.warning("SHOPIFY_WEBHOOK_SECRET no configurado")
if not SHOPIFY_API_TOKEN:
    logger.warning("SHOPIFY_API_TOKEN no configurado - las imagenes no estaran disponibles")

processed_orders = set()
orders_lock = threading.Lock()


def verify_shopify_webhook(request_data, signature):
    if not SHOPIFY_WEBHOOK_SECRET:
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
    if not SHOPIFY_API_TOKEN or not product_id:
        return None
    try:
        url = f"https://{SHOPIFY_STORE}/admin/api/2024-01/products/{product_id}.json"
        headers = {'X-Shopify-Access-Token': SHOPIFY_API_TOKEN}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            images = response.json().get('product', {}).get('images', [])
            if images:
                return images[0].get('src')
    except Exception as e:
        logger.error(f"Error obteniendo imagen: {e}")
    return None


def format_order_message(order_data):
    order_number = order_data.get('order_number', 'N/A')

    customer = order_data.get('customer', {})
    customer_name = customer.get('first_name', '') + ' ' + customer.get('last_name', '')
    customer_email = customer.get('email', 'N/A')
    customer_phone = (
        customer.get('phone') or
        order_data.get('shipping_address', {}).get('phone') or
        order_data.get('billing_address', {}).get('phone') or
        'N/A'
    )
    customer_rut = customer.get('default_address', {}).get('company', 'N/A') if customer.get('default_address') else 'N/A'

    line_items = order_data.get('line_items', [])
    products_text = ""
    has_multiple_units = False
    for item in line_items:
        title = item.get('title', 'Producto desconocido')
        quantity = item.get('quantity', 0)
        price = float(item.get('price', 0))
        sku = item.get('sku', 'N/A')
        products_text += f"  • {title} (SKU: {sku}) x{quantity} - ${int(price):,}\n\n"
        if quantity > 1:
            has_multiple_units = True

    alert_text = "⚠️ OJO: Hay productos con múltiples unidades\n\n" if has_multiple_units else ""

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

    total_price = float(order_data.get('total_price', 0))

    message = f"""🛹 NUEVO PEDIDO #{order_number}

👤 Cliente: {customer_name.strip()}
🆔 RUT: {customer_rut}
📧 {customer_email}
📞 {customer_phone if customer_phone and customer_phone != 'None' else 'N/A'}

{alert_text}📦 PRODUCTOS:
{products_text}
📍 DIRECCION DE ENVIO:
{address_text}

💰 TOTAL: ${int(total_price):,}"""

    return message


def send_telegram_message(message, image_url=None):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            bot = Bot(token=TELEGRAM_TOKEN)
            if image_url:
                loop.run_until_complete(bot.send_photo(
                    chat_id=TELEGRAM_CHAT_ID,
                    photo=image_url,
                    caption=message
                ))
            else:
                loop.run_until_complete(bot.send_message(
                    chat_id=TELEGRAM_CHAT_ID,
                    text=message
                ))
            logger.info("Mensaje enviado a Telegram exitosamente")
    except Exception as e:
        logger.error(f"Error enviando mensaje a Telegram: {e}")
    finally:
        loop.close()


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    try:
        request_data = request.get_data()
        signature = request.headers.get('X-Shopify-Hmac-SHA256', '')

        if not verify_shopify_webhook(request_data, signature):
            return {'status': 'error', 'message': 'Firma invalida'}, 401

        order_data = json.loads(request_data)
        order_number = order_data.get('order_number', 'N/A')

        with orders_lock:
            if order_number in processed_orders:
                logger.warning(f"Orden #{order_number} ya procesada, ignorando duplicado")
                return {'status': 'success', 'message': 'Orden ya procesada'}, 200
            processed_orders.add(order_number)

        message = format_order_message(order_data)

        line_items = order_data.get('line_items', [])
        image_url = None
        if line_items:
            product_id = line_items[0].get('product_id')
            image_url = get_product_image(product_id)

        thread = threading.Thread(target=send_telegram_message, args=(message, image_url))
        thread.daemon = True
        thread.start()

        logger.info(f"Pedido #{order_number} recibido y en cola para procesar")
        return {'status': 'success', 'message': 'Pedido recibido'}, 200

    except json.JSONDecodeError:
        return {'status': 'error', 'message': 'JSON invalido'}, 400
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return {'status': 'error', 'message': str(e)}, 500


@app.route('/health', methods=['GET'])
def health_check():
    return {'status': 'saludable'}, 200


@app.route('/', methods=['GET'])
def home():
    return {'nombre': 'Bot de Pedidos Skateshop', 'estado': 'funcionando', 'version': '2.0'}, 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
```

---

## CONFIGURACIÓN EN SHOPIFY

- **Webhook activo:** Creación de pedido → `https://skateshop-telegram-bot.onrender.com/webhook`
- **RUT del cliente:** Está en el campo "empresa" de la dirección del cliente (Shopify no tiene campo RUT nativo)
- **Versión API webhooks:** 2026-04

---

## CONFIGURACIÓN EN TELEGRAM

- **Grupo:** Privado, con el dueño y el bodeguero
- **Chat ID del grupo:** `-4996651405`
- **El bodeguero:** Solo necesita Telegram instalado, no necesita acceso a Shopify

---

## PROBLEMAS RESUELTOS Y CÓMO SE RESOLVIERON

1. **Mensajes duplicados (x3):** Shopify dispara el mismo webhook 3 veces. Resuelto con `threading.Lock()` + `set()` que bloquea atómicamente la verificación
2. **"Event loop is closed":** python-telegram-bot v21 es async. Resuelto creando un `Bot()` nuevo + `asyncio.new_event_loop()` en cada envío
3. **Shopify reintentaba por timeout:** Resuelto respondiendo `200 OK` inmediatamente y enviando el mensaje a Telegram en un thread separado (background)
4. **Teléfono no aparecía:** Shopify guarda el teléfono en `shipping_address`, no en `customer`. Resuelto buscando en `customer.phone`, `shipping_address.phone` y `billing_address.phone`

---

## CÓMO HACER CAMBIOS AL CÓDIGO

1. Edita `bot.py` localmente
2. Ve a github.com/sebacastro1/skateshop-telegram-bot
3. Haz clic en `bot.py` → lápiz ✏️ → pega el nuevo código → Commit changes
4. Render redespliegua automáticamente en ~2 minutos
5. Prueba creando una orden de prueba en Shopify

---

## MEJORAS PENDIENTES

- [ ] Imágenes de productos (requiere configurar `SHOPIFY_API_TOKEN` en Render)
- [ ] Persistir `processed_orders` en archivo para sobrevivir reinicios de Render

---

## NOTAS IMPORTANTES

- El bot corre en Render, **NO en tu PC local**. Tu PC solo tiene el código fuente
- El free tier de Render "duerme" tras 15 min sin actividad → primer webhook puede tardar ~50 seg
- Las credenciales NUNCA van en GitHub, solo en Render → Environment
- Si Render cambia la URL del bot, hay que actualizar el webhook en Shopify
