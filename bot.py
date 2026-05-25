import os
import sys
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbzj2TV03a4gPfsHgfG-JAdOWx_mSRNZa7dozFck7Uq8XtaBtPvaJvDxuZt66U0rPUdi/exec"
PORT = int(os.getenv("PORT", 10000))

if not TOKEN:
    print("ERROR: BOT_TOKEN is not set!")
    sys.exit(1)

# ── Health check server ────────────────────────────────────
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_http():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    server.serve_forever()

t = threading.Thread(target=run_http, daemon=True)
t.start()
print(f"Health server running on port {PORT}")

# ── Telegram Bot ───────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مرحباً! ابعت أي مصروف أو دخل وأنا هسجله 📊")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    chat_id = update.message.chat_id

    try:
        r = requests.get(WEB_APP_URL, params={
            "action": "inbox",
            "chat_id": chat_id,
            "message": text
        }, timeout=10)
        result = r.json()
        if result.get("success"):
            await update.message.reply_text("✅ تم الاستلام، هتتضاف لما AI يشوفها")
        else:
            await update.message.reply_text("❌ حصل خطأ في التسجيل")
    except Exception as e:
        print("Error:", e)
        await update.message.reply_text("❌ حصل خطأ في الاتصال")

async def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
