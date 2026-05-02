# 🛹 Bot de Telegram para Pedidos Skateshop

## 📋 ¿Qué hace este proyecto?

Bot automatizado que envía notificaciones de nuevos pedidos de Shopify a un grupo privado de Telegram.
Cuando un cliente hace un pedido en la tienda, el bot envía automáticamente todos los detalles al grupo donde está el bodeguero.

**Tienda:** legit-skateshop.myshopify.com

---

## ✅ Estado actual (Abril 2026)

- ✅ Bot corriendo 24/7 en Render.com (gratis)
- ✅ Conectado a Shopify via webhooks
- ✅ Enviando mensajes al grupo privado de Telegram
- ✅ Mensajes en español con precios en CLP sin decimales
- ✅ Incluye: cliente, RUT, email, teléfono, productos, SKU, dirección, total

---

## 🔑 Credenciales y dónde encontrarlas

> ⚠️ NUNCA subas estas credenciales a GitHub. Siempre van en Render → Environment.

| Variable | Dónde obtenerla |
|----------|----------------|
| `TELEGRAM_TOKEN` | Telegram → @BotFather → /mybots → tu bot → API Token |
| `TELEGRAM_CHAT_ID` | Abrir grupo en web.telegram.org/k/ → número en la URL después del # |
| `SHOPIFY_WEBHOOK_SECRET` | Shopify Admin → Configuración → Webhooks → abajo de la lista de webhooks |
| `SHOPIFY_API_TOKEN` | Shopify Admin → Configuración → Apps → Desarrollar apps (opcional) |

**Valores actuales configurados en Render:**
- `TELEGRAM_CHAT_ID`: `-4996651405` (grupo privado)
- `SHOPIFY_WEBHOOK_SECRET`: se ve en Shopify Admin → Webhooks

---

## 📂 Archivos del proyecto

```
skateshop-telegram-bot/
├── bot.py              → Código principal del bot
├── requirements.txt    → Dependencias Python
├── render.yaml         → Configuración de Render
├── .env.example        → Plantilla de variables de entorno
├── CONFIGURACION.md    → Esta guía
└── README.md           → Documentación general
```

---

## 🖥️ Cómo configurar en un PC nuevo (paso a paso)

### Requisitos previos
- Tener Python instalado (https://python.org)
- Tener Git instalado (https://git-scm.com)
- Tener una cuenta en GitHub (github.com/sebacastro1)
- Tener una cuenta en Render (render.com)

---

### Paso 1: Clonar el proyecto desde GitHub

Abre una terminal (CMD o PowerShell) y ejecuta:

```bash
git clone https://github.com/sebacastro1/skateshop-telegram-bot.git
cd skateshop-telegram-bot
```

---

### Paso 2: Instalar dependencias (solo para probar localmente)

```bash
pip install -r requirements.txt
```

---

### Paso 3: Configurar variables de entorno localmente (para pruebas)

1. Copia el archivo `.env.example` y renómbralo a `.env`
2. Abre el archivo `.env` con el Bloc de notas
3. Rellena cada variable con sus valores reales

```
TELEGRAM_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=-4996651405
SHOPIFY_WEBHOOK_SECRET=tu_secret_aqui
```

> ⚠️ El archivo `.env` NUNCA se sube a GitHub (está en .gitignore)

---

### Paso 4: El bot ya está en Render (no necesitas redeplegar)

El bot ya corre 24/7 en:
- **Dashboard:** https://dashboard.render.com/web/srv-d793v714tr6s73clg3sg
- **URL del bot:** https://skateshop-telegram-bot.onrender.com

Solo necesitas entrar al dashboard de Render para:
- Ver logs
- Actualizar variables de entorno
- Forzar un redespliegue

---

### Paso 5: Si necesitas redesplegar desde cero en Render

1. Ve a render.com → New → Web Service
2. Conecta con GitHub → selecciona `skateshop-telegram-bot`
3. Configura:
   - **Name:** skateshop-telegram-bot
   - **Environment:** Python
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn bot:app`
4. Agrega las variables de entorno (ver tabla arriba)
5. Click **Create Web Service**
6. Espera 2-3 minutos a que despliegue
7. Copia la nueva URL y actualiza el webhook en Shopify

---

### Paso 6: Actualizar webhook en Shopify (si cambia la URL de Render)

1. Shopify Admin → Configuración → Webhooks
2. Editar el webhook "Creación de pedido"
3. Cambiar URL a: `https://[nueva-url-render].onrender.com/webhook`
4. Guardar

---

## 🔄 Cómo actualizar el código

1. Edita `bot.py` en tu PC
2. Ve a GitHub → `bot.py` → lápiz ✏️ → pega el nuevo código → Commit
3. Render detecta el cambio y redespliega automáticamente (~2 min)

---

## 📝 Formato del mensaje actual

```
🛹 NUEVO PEDIDO #XXXX

👤 Cliente: Juan García
🆔 RUT: 12.345.678-9
📧 juan@email.com
📞 +56912345678

⚠️ OJO: Hay productos con múltiples unidades  ← solo si qty > 1

📦 PRODUCTOS:
  • Tabla de Skate Roja (SKU: TSR-001) x2 - $45.990

  • Grip Tape Negro (SKU: GTN-002) x1 - $8.990

📍 DIRECCION DE ENVIO:
Calle Principal 123
Santiago, RM 8320000
Chile

💰 TOTAL: $54.980
```

---

## 🐛 Solución de problemas comunes

| Problema | Causa probable | Solución |
|----------|---------------|----------|
| No llegan mensajes | Bot dormido (free tier) | Espera 50 seg, el bot se despierta solo |
| "Chat not found" | TELEGRAM_CHAT_ID incorrecto | Abre grupo en web.telegram.org, copia el número de la URL |
| Llegan 3 mensajes | Race condition | Ya solucionado con threading.Lock() |
| "Event loop closed" | Conflicto de asyncio | Ya solucionado con Bot() por instancia |
| Webhook no llega | URL incorrecta en Shopify | Verificar que termine en /webhook |

---

## 🔗 URLs importantes

| Servicio | URL |
|----------|-----|
| Render Dashboard | https://dashboard.render.com/web/srv-d793v714tr6s73clg3sg |
| GitHub Repo | https://github.com/sebacastro1/skateshop-telegram-bot |
| Shopify Admin | https://legit-skateshop.myshopify.com/admin |
| Bot Webhook URL | https://skateshop-telegram-bot.onrender.com/webhook |
| Bot Health Check | https://skateshop-telegram-bot.onrender.com/health |

---

## 💡 Mejoras futuras posibles

- Imágenes de productos en el mensaje (requiere SHOPIFY_API_TOKEN)
- Persistir órdenes procesadas en archivo/base de datos (por si se reinicia Render)
- Confirmación de despacho desde Telegram
- Dashboard web para ver historial de pedidos

---

**Última actualización:** Abril 2026
**Estado:** ✅ Funcionando en producción
