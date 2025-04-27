import json
import sqlite3
from typing import Dict
from langchain.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


def load_user_db(path: str = 'users_messages.db') -> sqlite3.Connection:
    """
    Connection with SQLite local database.

    Parameters
    ----------
    path : str
        Path to local database with users' interactions (dialog history).

    Returns
    -------
    connection : sqlite3.Connection
        SQLite connection to database (created if didn't exist).
    """

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


def load_faiss_index(path="faiss_index") -> FAISS:
    """
    Connection with FAISS local vector store.

    Parameters
    ----------
    path : str
        Path to local FAISS vector store.

    Returns
    -------
    db : FAISS
        Loaded FAISS vectore store.
    """

    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-m3",
        model_kwargs={'device': "cpu"}
    )
    db = FAISS.load_local(
        path, embeddings, allow_dangerous_deserialization=True
    )
    return db


def load_config(path: str = "config.json") -> Dict:
    """
    Config upload in json format.

    Parameters
    ----------
    path : str
        Path to local config.

    Returns
    -------
    config : Dict
        Loaded json config.
    """

    with open(path, 'r', encoding="UTF-8") as cnfg:
        config = json.load(cnfg)

    with open(config['system_prompt_path'], 'r', encoding="UTF-8") as prmt:
        config['system_prompt'] = prmt.read()

    return config
