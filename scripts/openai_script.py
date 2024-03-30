import base64
import requests
import json
import os
import datetime

from openai import OpenAI

from settings import OPENAI_API_KEY
from scripts.db_handler import GenericDBHandler, Conversation, Assistant, Thread


# GPTWrapper is a base class for GPTAssistantWrapper and GPTGeneralWrapper
class GPTWrapper:
    def __init__(self, api_key=None, db_url='sqlite:///conv.db'):
        super().__init__()
        # Initialize OpenAI client
        if api_key:
            self._client = OpenAI(api_key=api_key)
        self._is_gpt_available = True if api_key else False
        self._db_handler = ''
        self.init_db(db_url)

    def is_gpt_available(self):
        return self._is_gpt_available

    def set_api(self, api_key):
        try:
            response = requests.get('https://api.openai.com/v1/models', headers={'Authorization': f'Bearer {api_key}'})
            self._is_gpt_available = response.status_code == 200
            if self._is_gpt_available:
                self._api_key = api_key
                self._client = OpenAI(api_key=api_key)

            return self._is_gpt_available
        except Exception as e:
            print(e)
            return False

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
        self.__run_id = None
        self._attributes = ['name', 'instructions', 'tools', 'model']

    def clear_assistant(self):
        self._db_handler.delete(Assistant)

    def init_assistant(self, name, instructions, tools, model):
        assistant_obj = {"name": name,
                         "instructions": instructions,
                         "tools": tools,
                         "model": model}

        # Search row with name
        assistant = self._db_handler.query_table(Assistant, {"name": name})
        if assistant:
            self.__assistant_id = assistant[0].assistant_id
            print(f"Assistant {name} already exists")
        else:
            # Initialize assistant
            assistant = self._client.beta.assistants.create(
                **assistant_obj
            )

            self.__assistant_id = assistant.id

            assistant_obj = {
                "assistant_id": self.__assistant_id,
                "name": name,
                "instructions": instructions,
                "tools": tools[0]['type'],
                "model": model,
                "timestamp": datetime.datetime.fromtimestamp(assistant.created_at),
            }

            self._db_handler.append(Assistant, assistant_obj)

    def set_thread(self, name):
        if self.__assistant_id is None:
            raise ValueError('Assistant is not initialized yet')
        else:
            thread = self._db_handler.query_table(Thread, {"name": name, "assistant_id": self.__assistant_id})
            if thread:
                print(f"Thread {name} already exists")
                self.__thread_id = thread[0].thread_id
            else:
                thread = self._client.beta.threads.create()
                self.__thread_id = thread.id
                thread_obj = {"thread_id": self.__thread_id,
                              "name": name,
                              "assistant_id": self.__assistant_id}
                self._db_handler.append(Thread, thread_obj)

    def send_message(self, message_str, instructions=''):
        self._client.beta.threads.messages.create(
            thread_id=self.__thread_id,
            role="user",
            content=message_str
        )

        if self.__run_id:
            pass
        else:
            run = self._client.beta.threads.runs.create(
                thread_id=self.__thread_id,
                assistant_id=self.__assistant_id,
                instructions=instructions,
            )
            self.__run_id = run.id

        response = self._client.beta.threads.runs.retrieve(
          thread_id=self.__thread_id,
          run_id=self.__run_id
        )

        while response.status == "in_progress" or response.status == "queued":
            response = self._client.beta.threads.runs.retrieve(thread_id=self.__thread_id, run_id=self.__run_id)

        messages = self._client.beta.threads.messages.list(thread_id=self.__thread_id)
        message_data = messages.dict()["data"][0]
        content_data = message_data["content"][0]
        print(content_data)

    def get_assistant_attributes(self):
        return self._attributes


class GPTGeneralWrapper(GPTWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._text_attributes = [
            'model',
            'messages',
            'n',
            'stream',
            'response_format',
        ]
        self._image_attributes = [
            'model',
            'prompt',
            'n',
            'style',
            'size',
            'response_format',
        ]

    def get_image_url_from_local(self, image_path):
        # Function to encode the image
        def encode_image(image_path):
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

        base64_image = encode_image(image_path)
        return f'data:image/jpeg;base64,{base64_image}'

    def get_message_obj(self, role, content):
        return {"role": role, "content": content}

    def get_arguments(
        self,
        model="gpt-4-0125-preview",
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
        images=[],
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
            if len(images) > 0:
                multiple_images_content = []
                for image in images:
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
            else:
                self._db_handler.append(Conversation, self.get_message_obj("user", cur_text))
                openai_arg['messages'].append({"role": "user", "content": cur_text})
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
            if self.is_gpt_available():
                response = self._client.chat.completions.create(**openai_arg)
                response_content = response.choices[0].message.content
                self._db_handler.append(Conversation, self.get_message_obj('assistant', response_content))

                return response_content
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
                if self.is_gpt_available():
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

    def get_text_attributes(self):
        return self._text_attributes

    def get_image_attributes(self):
        return self._image_attributes

def is_gpt_vision(model: str):
    return model == 'gpt-4-vision-preview'

db_url = 'sqlite:///conv.db'

# # # For GPT test
# # wrapper = GPTGeneralWrapper(api_key=OPENAI_API_KEY, db_url='sqlite:///conv.db')
# # while True:
# #     text = input("Enter the prompt: ")
# #     if text == 'exit':
# #         break
# #     print(wrapper.get_text_response(wrapper.get_arguments(cur_text=text)))
#
# wrapper = GPTAssistantWrapper(api_key=OPENAI_API_KEY, db_url=db_url)
# obj = {"name": "Math Tutor",
#       "instructions": "You are a personal math tutor. Write and run code to answer math questions.",
#       "tools": [{"type": "code_interpreter"}], # Only one type available
#       "model": "gpt-4-0125-preview"}
# wrapper.init_assistant(**obj)
# wrapper.set_thread(name='ABC')
# wrapper.send_message(message_str="What is 2+2?", instructions='Please address the user as Jane Doe. The user has a premium account.')