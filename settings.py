from dotenv import load_dotenv
import os

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

load_dotenv(os.path.join(ROOT_DIR, ".env"), verbose=True)

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')