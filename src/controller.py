from ..models.model_wrapper import ModelWrapperBase


class BotController:
    """ Controller class that represents connection between models/data sources and user queries """

    def __init__(self, model: ModelWrapperBase, users_data, rag_data) -> None:
        self.model = model                  # text2text model in ModelWrapperBase class format
        self.users_data = users_data        # database with users interactions information (sqlite)
        self.rag_data = rag_data            # RAG vector store (FAISS)

    def load_dialog_and_rag_history(self, user_id: str):

        messages = self.users_data.cursor().execute(
            """
            SELECT user_message, assistant_message, rag_addition 
            FROM UsersMessages 
            WHERE (user_id = ?) AND (cleared = 0) 
            ORDER BY id
            """,
            (user_id,)
        ).fetchall()

        dialog_from_messages = []
        rag_items = []
        for (user_mes, assist_mes, rag_addition) in messages:
            dialog_from_messages.append({"role": "user", "content": str(user_mes)})
            dialog_from_messages.append({"role": "assistant", "content": str(assist_mes)})
            rag_items.extend(rag_addition.split('\n'))

        rag_items = list(set(rag_items))

        return dialog_from_messages, rag_items

    def generate_answer(self, user_id: str, user_text: str) -> str:

        dialog_from_messages_history, rag_items_history = self.load_dialog_and_rag_history(user_id)

        dialog_from_messages_history.append({"role": "user", "content": str(user_text)})
        rag_items_history.extend(
            [
                str(doc.page_content) + " Ссылка на товар: " + doc.metadata["url"] for doc in
                self.rag_data.similarity_search(user_text, k=5)
            ]
        )
        rag_info = "Выбранные товары:\n" + "\n".join(rag_items_history)

        answer = self.model.get_response(
            dialog_from_messages_history,
            rag_info
        )

        self.create_note_in_source(user_id, user_text, answer, rag_items_history)
        return answer

    def create_note_in_source(self, user_id, user_text, answer, rag_items_history) -> None:
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
        self.users_data.cursor().execute(
            'UPDATE UsersMessages SET cleared = ? WHERE user_id = ?',
            (1, str(user_id))
        )
        self.users_data.commit()
