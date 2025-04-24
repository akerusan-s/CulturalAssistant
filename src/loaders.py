import sqlite3
import json
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def load_user_db(path='users_messages.db'):
    connection = sqlite3.connect(path)
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UsersMessages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        user_message TEXT NOT NULL,
        assistant_message TEXT NOT NULL,
        rag_addition TEXT NOT NULL,
        cleared INTEGER NOT NULL
    )
    ''')

    connection.commit()
    return connection


def load_faiss_index(path="faiss_index"):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    db = FAISS.load_local(
        path, embeddings, allow_dangerous_deserialization=True
    )
    return db


def load_config(path):
    with open(path, 'r', encoding="UTF-8") as f:
        config = json.load(f)
    return config
