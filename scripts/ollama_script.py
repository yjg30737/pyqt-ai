"""
This is for using Ollama and LangChain together in a script.
"""

import subprocess
from langchain_ollama import ChatOllama


class OllamaWrapper:
    def __init__(self):
        self.__llm = ""
        self.__model_name = ""

    # Check if Ollama is installed
    @staticmethod
    def is_ollama_installed():
        try:
            subprocess.run(["ollama", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    # Check if Ollama is running
    @staticmethod
    def run_ollama_serve():
        """Starts the Ollama service in a subprocess."""
        subprocess.Popen(["ollama", "serve"])

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

        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=5)

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
        if not self.__llm:
            raise ValueError("Model is not set. Please set a model before sending a message.")
        response = self.__llm.invoke(message)
        return response

    def get_message_obj(self, role, content):
        return {"role": role, "content": content}
