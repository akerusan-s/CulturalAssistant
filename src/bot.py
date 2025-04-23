import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_huggingface import HuggingFaceEmbeddings

from loaders import load_user_db, load_faiss_index, load_config
from ..models.model_deepseek_v1 import DeepSeekWrapper


TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN missing")

config = load_config("../configs/config.json")

embeddings_for_faiss = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
user_messages_db = load_user_db(config["chat_db_path"])
faiss_db = load_faiss_index(embeddings_for_faiss, config["faiss_db_path"])
model = DeepSeekWrapper(config["system_prompt"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Start-message reply """
    await update.message.reply_text(config["start_message"])


async def bot_response(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ User Message Processing  """
    user_id = str(update.message.from_user.id)
    text = str(update.message.text)

    if text:
        messages = user_messages_db.cursor().execute(
            'SELECT user_message, assistant_message FROM UsersMessages WHERE (user_id = ?) AND (cleared = 0) ORDER BY id',
            (user_id,)
        ).fetchall()

        dialog_from_messages = []
        for (user_mes, assist_mes) in messages:
            dialog_from_messages.append({"role": "user", "content": str(user_mes)})
            dialog_from_messages.append({"role": "assistant", "content": str(assist_mes)})
        dialog_from_messages.append({"role": "user", "content": str(text)})

        rag_info = "Выбранные товары:\n" + "\n".join([
            str(doc.page_content) + " Ссылка на товар: " + doc.metadata["url"] for doc in faiss_db.similarity_search(text, k=15)
        ])

        answer = model.get_response(dialog_from_messages, rag_info)

        user_messages_db.cursor().execute(
            'INSERT INTO UsersMessages (user_id, user_message, assistant_message, cleared) VALUES (?, ?, ?, ?)',
            (user_id, text, answer, 0)
        )
        user_messages_db.commit()

        await update.message.reply_text(answer)


async def clear_context(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Clear assistant context """
    user_messages_db.cursor().execute(
        'UPDATE UsersMessages SET cleared = ? WHERE user_id = ?',
        (1, str(update.message.from_user.id))
    )
    user_messages_db.commit()
    await update.message.reply_text("Контекст обновлён")


def main() -> None:
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear_context", clear_context))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot_response))

    application.run_polling()


if __name__ == '__main__':
    main()
