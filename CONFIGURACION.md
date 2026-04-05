# 🛹 Bot de Telegram para Pedidos Skateshop - Guía de Configuración

## 📋 Resumen del Proyecto

Bot automatizado que envía notificaciones de nuevos pedidos de Shopify a Telegram. Cuando se crea una orden en tu tienda, el bot automáticamente envía un mensaje con todos los detalles (cliente, RUT, productos, dirección, total).

---

## ✅ Qué está configurado

- ✅ Bot deployado en **Render.com** (gratis)
- ✅ Conectado a tu tienda Shopify: `legit-skateshop.myshopify.com`
- ✅ Envía mensajes a **grupo de Telegram privado**
- ✅ Mensajes en **ESPAÑOL**
- ✅ Precios sin decimales (pesos chilenos)
- ✅ Incluye SKU de productos
- ✅ Alerta si hay múltiples unidades
- ✅ Muestra RUT, email, teléfono del cliente

---

## 🔧 Variables de Entorno (en Render)

Configuradas en: **Render → skateshop-telegram-bot → Environment**

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `TELEGRAM_TOKEN` | `shpat_...` | Token del bot de Telegram (de @BotFather) |
| `TELEGRAM_CHAT_ID` | `-4996651405` | Chat ID del grupo privado |
| `SHOPIFY_WEBHOOK_SECRET` | `9d1d9a7c2c30...` | Secret del webhook de Shopify |
| `SHOPIFY_API_TOKEN` | (opcional) | Para obtener imágenes (no configurado actualmente) |

---

## 📂 Archivos Principales

**En GitHub:** `https://github.com/sebacastro1/skateshop-telegram-bot`

- **bot.py** - Código principal del bot
- **requirements.txt** - Dependencias Python (Flask, python-telegram-bot, gunicorn, requests)
- **render.yaml** - Configuración de Render

---

## 🚀 Cómo funciona

1. **Cliente hace una orden en Shopify**
2. **Shopify envía webhook a Render** (`https://skateshop-telegram-bot.onrender.com/webhook`)
3. **Bot procesa los datos del pedido**
4. **Bot envía mensaje al grupo de Telegram** con:
   - Número de orden
   - Cliente (nombre)
   - RUT (del campo "empresa")
   - Email
   - Teléfono
   - Productos (nombre, SKU, cantidad, precio)
   - Dirección de envío
   - Total

---

## 📝 Formato del Mensaje

```
🛹 NUEVO PEDIDO #1234

👤 Cliente: Juan García
🆔 RUT: 12.345.678-9
📧 juan@email.com
📞 +56912345678

⚠️ OJO: Hay productos con múltiples unidades

📦 PRODUCTOS:
  • Tabla de Skate Roja (SKU: TSR-001) x2 - $45.990

  • Grip Tape Negro (SKU: GTN-002) x1 - $8.990

📍 DIRECCION DE ENVIO:
Calle Principal 123, Apt 4B
Santiago, RM 8320000
Chile

💰 TOTAL: $54.980
```

---

## 🔗 Configuración en Shopify

**Webhook configurado:**
- **Evento:** Pedidos → Pedido creado
- **URL:** `https://skateshop-telegram-bot.onrender.com/webhook`
- **Formato:** JSON
- **Versión de API:** 2026-04

**Secret:** `9d1d9a7c2c30310f024acc3a193ef74c8e4cfc1b932be153d662197e5011e293`

---

## 💬 Configuración en Telegram

**Grupo:** "Pedidos Skateshop" (privado)
- **Chat ID:** `-4996651405`
- **Miembros:** Tú + tu papá + bot

**Bot:** `@legit_skateshop_orders_bot` (o el nombre que hayas configurado)

---

## 🛠️ Cómo actualizar el código

### Si quieres cambiar algo:

1. **Edita localmente:** `C:\Users\scrub\skateshop-telegram-bot\bot.py`
2. **Sube a GitHub:**
   - Ve a `github.com/sebacastro1/skateshop-telegram-bot`
   - Haz clic en el archivo
   - Haz clic en el lápiz ✏️ (editar)
   - Pega el contenido actualizado
   - Click "Commit changes"
3. **Render redesplegará automáticamente** en ~2 minutos
4. **Prueba con una orden de prueba en Shopify**

### Cambios comunes que podrías hacer:

- **Cambiar emoji o formato del mensaje:** Edita `format_order_message()` en bot.py
- **Agregar más campos del cliente:** Busca en `order_data` en bot.py
- **Cambiar precio a otro formato:** Busca `${int(price):,}` y modifica

---

## 🐛 Troubleshooting

**Problema:** El bot no envía mensajes
- ✓ Verifica que el bot esté agregado al grupo
- ✓ Verifica que `TELEGRAM_CHAT_ID` sea correcto (`-4996651405`)
- ✓ Revisa los logs en Render (Logs → busca errores)

**Problema:** Webhook no se dispara
- ✓ Verifica que el webhook esté activo en Shopify (Configuración → Webhooks)
- ✓ Verifica que la URL sea exacta: `https://skateshop-telegram-bot.onrender.com/webhook`
- ✓ Verifica que el secret sea correcto

**Problema:** Error "Chat not found" en Render
- ✓ El Chat ID está incorrecto
- ✓ Obtén el correcto abriendo el grupo en: `https://web.telegram.org/k/`
- ✓ El número después de `#` es tu Chat ID

---

## 📊 URLs Importantes

- **Render Dashboard:** `https://dashboard.render.com/web/srv-d793v714tr6s73clg3sg`
- **GitHub Repo:** `https://github.com/sebacastro1/skateshop-telegram-bot`
- **Shopify Admin:** `https://legit-skateshop.myshopify.com/admin`
- **Bot URL (webhook):** `https://skateshop-telegram-bot.onrender.com/webhook`

---

## 💡 Posibles mejoras futuras

- Agregar imágenes de productos en el mensaje
- Crear un dashboard web para ver pedidos
- Agregar filtros o búsqueda de pedidos
- Guardar historial de pedidos en base de datos
- Agregar más información del cliente (dirección adicional, etc.)

---

## 📞 Notas rápidas

- El bot se ejecuta 24/7 en Render (plan gratuito)
- No hay costo mensual (todo es gratis)
- Los mensajes llegan en tiempo real
- El grupo puede tener múltiples personas
- Puedes agregar más miembros al grupo cuando quieras

---

**Última actualización:** 6 de abril de 2026
**Estado:** ✅ Funcionando correctamente
