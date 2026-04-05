# Skateshop Telegram Order Bot

Automatically send Shopify order notifications to Telegram. When a new order arrives, your dad gets a message with all the order details (customer info, products, prices, shipping address).

## Features

✅ Instant notifications when orders arrive
✅ Complete order details (customer, products, prices, shipping)
✅ 24/7 operation (no computer needed)
✅ Completely free
✅ Simple setup (10 minutes)

## Setup Instructions

### Step 1: Create a Telegram Bot (5 minutes)

1. Open **Telegram** app or web
2. Search for **@BotFather** (official Telegram bot)
3. Send the message `/newbot`
4. Follow the prompts:
   - Name: `Skateshop Orders` (or any name you like)
   - Username: `legit_skateshop_orders_bot` (must be unique)
5. **Copy and save the API token** (looks like: `123456789:ABCdefGHIjklMNOpqrSTUVwxyz`)

### Step 2: Get Your Telegram Chat ID (2 minutes)

1. In Telegram, search for and open **@userinfobot**
2. Send it a message (any message works)
3. It will reply with your **User ID** - copy this number
4. This is your `TELEGRAM_CHAT_ID`

### Step 3: Deploy to Render (3 minutes)

1. Go to **render.com** and sign up (free account)
2. Click **New +** → **Web Service**
3. Choose **Deploy an existing Git repository**
   - If you don't have GitHub, create a quick one:
     - Go to github.com, create account
     - Create new repository named `skateshop-telegram-bot`
     - Upload the files from this folder
4. In Render:
   - Select your GitHub repository
   - Name: `skateshop-telegram-bot`
   - Environment: `Python`
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn bot:app`
5. Under **Environment**, add these variables:
   - `TELEGRAM_TOKEN` = (paste your token from BotFather)
   - `TELEGRAM_CHAT_ID` = (paste your User ID)
   - `SHOPIFY_WEBHOOK_SECRET` = (you'll get this from Shopify, see Step 4)

6. Click **Deploy** (takes ~2 minutes)
7. Once deployed, copy the URL (looks like: `https://skateshop-telegram-bot.onrender.com`)

### Step 4: Connect Shopify Webhook

1. Go to your **Shopify Admin Dashboard**
2. Settings → **Apps and integrations**
3. Click **Webhooks**
4. Click **Create webhook**
5. Fill in:
   - Event: `Orders` → `Order created`
   - URL: `https://YOUR_RENDER_URL/webhook` (paste the URL from Render Step 7)
   - Content type: `application/json`
6. Click **Save**
7. Shopify will show you the **Webhook secret** - copy it
8. Go back to **Render dashboard**
9. Add environment variable:
   - `SHOPIFY_WEBHOOK_SECRET` = (paste the secret from Shopify)

### Step 5: Test It! (1 minute)

1. In your Shopify admin, go to **Orders**
2. Click **Create** to make a test order
3. Fill in:
   - Customer: Your name
   - Product: Any product
   - Shipping address: Your address
4. Click **Create order**
5. Check Telegram - your dad should get a message! 🎉

### Step 6: Tell Your Dad (1 minute)

Tell your dad to:
1. Install Telegram app (if he doesn't have it)
2. Search for your bot name: `legit_skateshop_orders_bot` (from Step 1)
3. Click "Start"
4. From now on, he'll get a message every time an order arrives!

---

## What The Message Looks Like

```
🛹 NEW ORDER #1234567890

👤 Customer: John Doe
📧 john@email.com
📞 +1234567890

📦 PRODUCTS:
  • Red Skateboard Deck x1 - $45.99
  • Black Grip Tape x1 - $8.99
  • Wheels (Black) x4 - $32.00

📍 SHIPPING TO:
123 Main Street
Miami, FL 33101

💰 TOTAL: $86.98
```

---

## Troubleshooting

**"Bot not sending messages"**
- Check that `TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID` are correct in Render
- Make sure your dad started the bot (search for bot name, click Start)
- Check Render logs for errors

**"Webhook not working"**
- Check that the webhook URL is correct (Shopify Settings → Apps and integrations → Webhooks)
- Make sure you used `/webhook` at the end: `https://YOUR_RENDER_URL/webhook`
- Check that `SHOPIFY_WEBHOOK_SECRET` is set in Render

**"Getting 401 error"**
- Make sure webhook secret is correct
- This is a security check to ensure webhooks come from real Shopify

---

## File Structure

```
skateshop-telegram-bot/
├── bot.py              # Main bot code
├── requirements.txt    # Python dependencies
├── render.yaml        # Render deployment config
├── .env.example       # Environment variables template
└── README.md          # This file
```

---

## Need Help?

Check the Telegram message:
1. If no message arrives → Check Render logs
2. If message is incomplete → Bot might need code tweaks
3. If Shopify webhook fails → Check webhook secret

---

**Done!** Your order notification bot is now live. Every new order will notify your dad instantly via Telegram. 🛹
