import os
import asyncio
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from scraper import scrape_website
from extractor import extract_grant_details
from bigin_client import push_to_bigin

load_dotenv()

# Simple health check server for Render
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def log_message(self, format, *args):
        pass

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()

# Bot logic
async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("Please send a valid URL starting with http or https!")
        return

    await update.message.reply_text(f"Got it! Processing {url} ...")

    try:
        print("Step 1: Scraping...")
        raw_text = scrape_website(url)
        print("Step 2: Extracting...")
        grant_data = extract_grant_details(raw_text, url)
        print("Step 3: Pushing to Bigin...")
        push_to_bigin(grant_data.model_dump())
        print("Step 4: Done!")
        await update.message.reply_text(f"✅ Successfully pushed to Bigin!\n\n*{grant_data.oppurtunity_name}*", parse_mode="Markdown")
    except Exception as e:
        print(f"Failed at: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set — check env vars")

    # Start health server in background
    threading.Thread(target=start_health_server, daemon=True).start()

    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

    print("Bot is running...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    # Keep running
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await app.updater.stop()
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(run_bot())