import os

from llama_index.llms.openai import OpenAI
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader

from scripts.openai_script import GPTWrapper

from scripts.db_handler import GenericDBHandler, Conversation


class GPTLlamaIndexWrapper(GPTWrapper):
    """
    Currently this is only for loader and query engine.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._index = None
        self._query_engine = None

    # TODO: Implement this
    # def set_llm_model(self, temparature=0, model='gpt-4'):
    #     self.__llm = OpenAI(temperature=temparature, model=model)

    def set_directory(self, directory="./example"):
        documents = SimpleDirectoryReader(directory).load_data()
        self._index = VectorStoreIndex.from_documents(documents)

    def set_query_engine(self, streaming=False, similarity_top_k=3):
        if self._index is None:
            raise Exception(
                "Index must be initialized first. Call set_directory or set_files first."
            )
        try:
            self._query_engine = self._index.as_query_engine(
                streaming=streaming, similarity_top_k=similarity_top_k
            )
        except Exception as e:
            raise Exception(f"Error in setting query engine: {e}")

    def get_llamaindex_response_from_documents(self, message_str):
        user_obj = self.get_message_obj("user", message_str)
        self._db_handler.append(Conversation, user_obj)

        if self._query_engine is None:
            raise Exception(
                "Query engine is not initialized. Call set_query_engine first."
            )
        try:
            response = self._query_engine.query(
                message_str,
            )

            response = response.response

            response = self.get_message_obj("assistant", response)
            self._db_handler.append(Conversation, response)
            return response
        except Exception as e:
            raise Exception(f"Error in getting response: {e}")
