import base64
import requests
import json
import os
import datetime

from openai import OpenAI

from scripts.db_handler import GenericDBHandler, Conversation, Assistant, Thread

TEXT_MODELS = ['gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo'],
IMAGE_MODELS = ['dall-e-3']

# GPTWrapper is a base class for GPTAssistantWrapper and GPTGeneralWrapper
class GPTWrapper:
    def __init__(self, api_key=None, db_url='sqlite:///conv.db'):
        super().__init__()
        self._client = None
        # Initialize OpenAI client
        self._is_available = True if api_key else False
        if api_key and self._is_available:
            self.set_api(api_key)
        self._db_handler = ''
        self.init_db(db_url)

    def is_available(self):
        return self._is_available

    def set_api(self, api_key):
        self._api_key = api_key
        self._client = OpenAI(api_key=api_key)
        os.environ['OPENAI_API_KEY'] = api_key

    def request_and_set_api(self, api_key):
        try:
            response = requests.get('https://api.openai.com/v1/models', headers={'Authorization': f'Bearer {api_key}'})
            self._is_available = response.status_code == 200
            if self._is_available:
                self.set_api(api_key)
            return self._is_available
        except Exception as e:
            print(e)
            return False

    def get_message_obj(self, role, content):
        return {"role": role, "content": content}

    def init_db(self, db_url):
        self._db_handler = GenericDBHandler(db_url)

    def get_conversations(self):
        return self._db_handler.get_conversations()

    def append(self, message):
        self._db_handler.append(message)


class GPTAssistantWrapper(GPTWrapper):
    def __init__(self, api_key=None, db_url='sqlite:///conv.db'):
        super().__init__(api_key=api_key, db_url=db_url)
        self.__assistant_id = None
        self.__thread_id = None
        self.__assistants = []

    def get_assistants(self, order='desc', limit=None):
        if self._client is None:
            return None
        assistants = self._client.beta.assistants.list(order=order, limit=limit)
        assistants = [{
            "assistant_id": assistant.id,
            "name": assistant.name,
            "instructions": assistant.instructions,
            "tools": assistant.tools,
            "model": assistant.model,
            "thread": '',
        } for assistant in assistants]
        self.__assistants = assistants
        return self.__assistants

    def set_current_assistant(self, assistant_id):
        self.__assistant_id = assistant_id
        self.__set_current_thread()

    def __set_current_thread(self):
        if self.__assistant_id is None:
            raise ValueError('Assistant is not initialized yet')
        else:
            # thread = self._db_handler.query_table(Thread, {"name": name, "assistant_id": self.__assistant_id})
            # if thread:
            #     print(f"Thread {name} already exists")
            #     self.__thread_id = thread[0].thread_id
            # else:
            thread = self._client.beta.threads.create()
            self.__thread_id = thread.id
            for assistant in self.__assistants:
                if assistant["assistant_id"] == self.__assistant_id:
                    assistant["thread"] = self.__thread_id
                    break
            # self._db_handler.append(Thread, thread_obj)

    def send_message(self, message_str, instructions=''):
        user_obj = self.get_message_obj("user", message_str)
        self._db_handler.append(Conversation, user_obj)

        self._client.beta.threads.messages.create(
            thread_id=self.__thread_id,
            role="user",
            content=message_str
        )

        run = self._client.beta.threads.runs.create(
            thread_id=self.__thread_id,
            assistant_id=self.__assistant_id,
            instructions=instructions,
        )

        response = self._client.beta.threads.runs.retrieve(
          thread_id=self.__thread_id,
          run_id=run.id
        )

        while response.status == "in_progress" or response.status == "queued":
            response = self._client.beta.threads.runs.retrieve(thread_id=self.__thread_id, run_id=run.id)

        response = self._client.beta.threads.messages.list(thread_id=self.__thread_id)
        response = response.dict()["data"][0]
        response = self.get_message_obj(response['role'], response['content'][0]['text']['value'])
        self._db_handler.append(Conversation, response)
        return response


class GPTGeneralWrapper(GPTWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_image_url_from_local(self, image_path):
        # Function to encode the image
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        base64_image = encode_image(image_path)
        return f'data:image/jpeg;base64,{base64_image}'

    def get_arguments(
        self,
        model="gpt-4o",
        system="You are a very helpful assistant.",
        n=1,
        temperature=1,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        response_format="text",
        objective: dict = {},
        cur_text: str = '',
        use_max_tokens=False,
        max_tokens=128000,
        stream=False,
        images_for_vision=[],
    ):
        system_obj = self.get_message_obj("system", system)
        previous_messages = [system_obj] + self.get_conversations()

        if response_format == 'text':
            pass
        else:
            cur_text = objective["cur_text"] + " " + str(objective["json_format"])
        try:
            openai_arg = {
                "model": model,
                "messages": previous_messages,
                "n": n,
                "temperature": temperature,
                "top_p": top_p,
                "frequency_penalty": frequency_penalty,
                "presence_penalty": presence_penalty,
                "stream": stream,
                "response_format": {"type": response_format},
            }

            # If there is at least one image, it should add
            if len(images_for_vision) > 0:
                multiple_images_content = []
                for image in images_for_vision:
                    multiple_images_content.append(
                        {
                            'type': 'image_url',
                            'image_url': {
                                'url': self.get_image_url_from_local(image)
                            }
                        }
                    )

                multiple_images_content = [
                                              {
                                                  "type": "text",
                                                  "text": cur_text
                                              }
                                          ] + multiple_images_content[:]
                openai_arg['messages'].append({"role": "user", "content": multiple_images_content})
            user_obj = self.get_message_obj("user", cur_text)
            self._db_handler.append(Conversation, user_obj)
            openai_arg['messages'].append(user_obj)
            # If current model is "vision", default max token set to very low number by openai,
            # so let's set this to 4096 which is relatively better.
            if is_gpt_vision(model):
                openai_arg['max_tokens'] = 4096
            if use_max_tokens:
                openai_arg['max_tokens'] = max_tokens

            return openai_arg
        except Exception as e:
            raise Exception(e)

    def get_text_response(self, openai_arg):
        try:
            if self.is_available():
                response = self._client.chat.completions.create(**openai_arg)
                response = response.choices[0].message
                response = self.get_message_obj(response.role, response.content)
                self._db_handler.append(Conversation, response)

                return response
            else:
                raise ValueError('GPT is not available')
        except Exception as e:
            raise Exception(e)

    def get_image_response(self, model='dall-e-3', prompt="""
        Photorealistic,
        Close-up portrait of a person for an ID card, neutral background, professional attire, clear facial features, eye-level shot, soft lighting to highlight details without harsh shadows, high resolution for print quality --ar 1:1
        """, n=1, style='vivid', size='1024x1024', response_format='b64_json'):
            image_data = ''
            try:
                if self.is_available():
                    response = self._client.images.generate(
                        model=model,
                        prompt=prompt,
                        n=n,
                        style=style,
                        size=size,
                        response_format=response_format,
                    )
                    for _ in response.data:
                        image_data = _.b64_json
                    return image_data
                else:
                    raise ValueError('GPT is not available')
            except Exception as e:
                print(e)
                raise Exception(e)

def is_gpt_vision(model: str):
    return model == 'gpt-4-vision-preview'