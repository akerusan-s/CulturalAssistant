from typing import List, Dict


class ModelWrapperBase:
    """ Base wrapper class that implements interface for models' responses """

    def __init__(self, system_prompt: str):
        """
        Initialization of parameters, tokenizers, embeddings and a sytem prompt

        Parameters
        ----------
        system_prompt : str
            System prompt for all answer generations.

        """
        pass

    def get_response(self, dialog: List[Dict], rag_information: str) -> str:
        """
        Model response generation conditioned by dialog history.

        Parameters
        ----------
        dialog : [{"role": ["user" | "assistant"], "content": str}, ...] list of dicts
            Representation of a dialog between model and user.
        rag_information: str
            RAG information for the last query of a dialog compressed in string

        Returns
        -------
        response : str
            Model response.


        """
        pass
