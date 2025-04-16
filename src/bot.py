from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import os

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN missing")

user_messages = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение."""
    # user_id = update.message.from_user.id
    # if user_id not in user_messages:
    #     user_messages[user_id] = []
    await update.message.reply_text("Привет! Я бот, который сохраняет все твои сообщения и отправляет их тебе.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Сохраняет сообщение и отправляет его обратно пользователю."""
    user_id = update.message.from_user.id
    text = update.message.text
    if user_id not in user_messages:
        user_messages[user_id] = []
    if text:
        user_messages[user_id].append(text)  # Добавляем сообщение в список
        await update.message.reply_text(f"Сообщение сохранено: {text}")


async def get_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет пользователю все сохраненные сообщения."""
    user_id = update.message.from_user.id
    if user_id in user_messages and user_messages[user_id]:
        messages_string = "\n".join(user_messages[user_id])
        await update.message.reply_text(f"Все твои сообщения:\n{messages_string}")
    else:
        await update.message.reply_text("У тебя пока нет сохраненных сообщений.")


def main() -> None:
    """Запускает бота."""
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("get_all", get_all_messages))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    application.run_polling()


if __name__ == '__main__':
    main()
