# pyqt-ai
[![](https://dcbadge.vercel.app/api/server/cHekprskVE)](https://discord.gg/cHekprskVE)

## Description
This is a showcase of bundle of chatbots and image generators using OpenAI, llamaindex, replicate, etc on PyQt/PySide.

This can be used in pyqt6, pyside6.

Using SQLite as database, which is lighthearted and easy to use.

## Applications list
* OpenAI Chatbot
* DALLE Image Generator
* GPT Assistant Chatbot
* GPT Vision Chatbot
* LlamaIndex with OpenAI Chatbot
* Replicate Image Generator
* Ollama Chatbot Example (using LangChain) - You need Ollama to run this successfully

## Directory Structure
```
/examples
/scripts
/widgets
```

## Requirements
```
# GUI
qtpy
PyQt6
PySide6

# OPENAI
openai

# DB
sqlalchemy
psycopg2

# llamaindex
llama-index
pillow

# langchain
langgraph
langchain_ollama

# replicate
replicate

# ETC
requests
black
```

## How to Install
```sh
# Clone the repo
>>> git clone ~
# Install requirements
>>> pip install -r requirements.txt
# Run application you want
>>> python examples/*.py
```

## Preview
https://youtu.be/owRaR_2ZfcM
