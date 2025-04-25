import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from loaders import load_user_db, load_faiss_index, load_config
from controller import BotController
from ..models.model_saiga import SaigaWrapper


TOKEN = os.environ.get("TOKEN")                             # telegram bot token
if not TOKEN:
    raise ValueError("Telegram token missing")

config = load_config("../configs/config.json")              # config with paths, system prompt and hello-message for bot

user_messages_db = load_user_db(config["chat_db_path"])     # text2text model in ModelWrapperBase class format
faiss_db = load_faiss_index(config["faiss_db_path"])        # RAG vector store (FAISS)
model = SaigaWrapper(config["system_prompt"])               # database with users interactions information (sqlite)

bot_controller = BotController(model, user_messages_db, faiss_db)       # bot controller (see: controller.py)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Start-message reply """
    await update.message.reply_text(config["start_message"])


async def bot_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ User Message Processing  """
    user_id = str(update.message.from_user.id)
    text = str(update.message.text)

    if text:
        answer = bot_controller.generate_answer(user_id, text)
        await update.message.reply_text(answer)


async def clear_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Clear assistant context.
    User messages seen in dialog will not be processed during answer generation.
    """
    bot_controller.clear_context(str(update.message.from_user.id))
    await update.message.reply_text("Контекст обновлён.")


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear_context", clear_context))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_response))

    application.run_polling()


if __name__ == '__main__':
    main()
