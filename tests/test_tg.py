import logging
import os

from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Received start from {update.effective_chat.id}")
    await update.message.reply_text("Hello testing")

async def forcefestival(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    print(f"Received forcefestival from {update.effective_chat.id} with args {context.args}")
    await update.message.reply_text(f"Testing forcefestival: arg was {context.args}")

def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("forcefestival", forcefestival))
    print("Starting polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
