from typing import List, Tuple, Dict
from collections import OrderedDict

from ..models.model_wrapper import ModelWrapperBase


class BotController:
    """ Controller class that represents connection between models/data sources and user queries. """

    def __init__(self, model: ModelWrapperBase, users_data, rag_data) -> None:
        self.model = model                  # text2text model in ModelWrapperBase class format
        self.users_data = users_data        # database with users interactions information (sqlite)
        self.rag_data = rag_data            # RAG vector store (FAISS)

    def load_dialog_and_rag_history(self, user_id: str) -> Tuple[List[Dict[str, str]], List]:
        """
        Loading of user interactions history with bot.

        Parameters
        ----------
        user_id : str
            User id in telegram.

        Returns
        -------
        dialog_from_messages : List
            Dialog history of bot with the user in format [{"role": ["user" | "assistant"], "content": text}, ...].
        rag_items : List
            Items in RAG store that were used during the dialog.
        """

        messages = self.users_data.cursor().execute(
            """
            SELECT user_message, assistant_message, rag_addition 
            FROM UsersMessages 
            WHERE (user_id = ?) AND (cleared = 0) 
            ORDER BY id
            """,
            (user_id,)
        ).fetchall()

        dialog_from_messages = []       # messages history  [{"role": ["user" | "assistant"], "content": text}, ...]
        rag_items = []                  # rag history       ["Название: ..., Ссылка: ...", ...]
        for (user_mes, assist_mes, rag_addition) in messages:
            dialog_from_messages.append({"role": "user", "content": str(user_mes)})
            dialog_from_messages.append({"role": "assistant", "content": str(assist_mes)})
            rag_items.extend(rag_addition.split('\n'))

        rag_items = list(OrderedDict.fromkeys(rag_items))  # drop duplicated rag items with order

        return dialog_from_messages, rag_items

    def generate_answer(self, user_id: str, user_text: str) -> str:
        """
        Generation of model response for user query considering RAG addition.

        Parameters
        ----------
        user_id : str
            User id in telegram.
        user_text : str
            User message content (text).

        Returns
        -------
        answer : str
            Model response for user query and added RAG information.
        """

        # history messages and items
        dialog_from_messages_history, rag_items_history = self.load_dialog_and_rag_history(user_id)

        # current query addition to the history
        dialog_from_messages_history.append({"role": "user", "content": str(user_text)})
        rag_items_history.extend(
            [
                str(doc.page_content) + " Ссылка на товар: " + str(doc.metadata["url"]) for doc in
                self.rag_data.similarity_search(user_text, k=5)
            ]
        )

        # only last 10 items of RAG are involved to avoid context (memory) overload
        # a good place to implement reranker
        rag_items_history = rag_items_history[-10:]

        rag_info = "Выбранные товары:\n"\
                   + "\n".join(rag_items_history)\
                   + f"\n Количество сообщений от тебя: {(len(dialog_from_messages_history) - 1) // 2} \n"

        answer = self.model.get_response(
            dialog_from_messages_history,
            rag_info
        )

        # update history of interactions in database
        self.create_note_in_source(user_id, user_text, answer, rag_items_history)
        return answer

    def create_note_in_source(self, user_id: str, user_text: str, answer: str, rag_items_history: List[str]) -> None:
        """
        Loading of model response for user query with RAG information to database (sqlite).

        Parameters
        ----------
        user_id : str
            User id in telegram.
        user_text : str
            User message content (text)
        answer : str
            Model response
        rag_items_history : List[str]
            RAG items considered during answer generation
        """

        self.users_data.cursor().execute(
            """
            INSERT 
            INTO UsersMessages (user_id, user_message, assistant_message, rag_addition, cleared) 
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, user_text, answer, "\n".join(rag_items_history), 0)
        )
        self.users_data.commit()

    def clear_context(self, user_id: str) -> None:
        """
        Set status of messages in database (sqlite) to "cleared = 1".
        These messages will not be processed during answer generation.

        Parameters
        ----------
        user_id : str
            User id in telegram.
        """

        self.users_data.cursor().execute(
            'UPDATE UsersMessages SET cleared = ? WHERE user_id = ?',
            (1, str(user_id))
        )
        self.users_data.commit()
