"""
This is for using Ollama and LangChain together in a script.
"""

import subprocess
from langchain_ollama import ChatOllama


class OllamaWrapper:
    def __init__(self):
        self.__llm = ""
        self.__model_name = ""

    def get_model_name(self):
        """
        Get the name of the current model.
        """
        return self.__model_name

    def set_model_name(self, model_name):
        """
        Set the name of the current model.
        """
        self.__model_name = model_name
        self.__llm = ChatOllama(model=model_name)

    def download_model(self, model):
        """
        Download the specified model using Ollama CLI.
        """
        subprocess.run(f"ollama pull {model}", shell=True, check=True)

    def model_exists(self, model):
        """
        Check if the specified model exists.
        """
        result = subprocess.run(
            f"ollama list", shell=True, capture_output=True, text=True
        )
        return model in result.stdout

    def get_ollama_models(self):
        cmd = ["ollama", "list"]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

        if result.returncode != 0:
            raise RuntimeError(f"Failed to run ollama list: {result.stderr}")

        lines = result.stdout.strip().split("\n")
        if len(lines) < 2:
            return []

        headers = lines[0].split()

        models = []
        for line in lines[1:]:
            parts = line.split()

            if len(parts) >= 2:
                model_name = parts[0]
                size = "".join(parts[2:4])

                models.append({"NAME": model_name, "SIZE": size})

        return models

    def remove_model(self, model):
        """
        Remove the specified model using Ollama CLI.
        """
        subprocess.run(f"ollama rm {model}", shell=True, check=True)

    def send_message(self, message):
        """
        Send a message to the LLM and return the response.
        """
        response = self.__llm.invoke(message)
        return response

    def get_message_obj(self, role, content):
        return {"role": role, "content": content}
