import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from scraper import scrape_website
from extractor import extract_grant_details
from bigin_client import push_to_bigin

load_dotenv()

async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not url.startswith("http"):
        await update.message.reply_text("Please send a valid URL starting with http or https!")
        return

    await update.message.reply_text(f"Got it! Processing {url} ...")

    try:
        raw_text = scrape_website(url)
        grant_data = extract_grant_details(raw_text, url)
        push_to_bigin(grant_data.model_dump())
        await update.message.reply_text(f"✅ Successfully pushed to Bigin!\n\n*{grant_data.oppurtunity_name}*", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

app = ApplicationBuilder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))

print("Bot is running...")
app.run_polling()
