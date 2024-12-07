import os
import json
import openai
from lyricsgenius import Genius
from openai import OpenAI
from lyrica.VectorDB import Dictbased_VectorDB
from server.config import create_logger

from dotenv import load_dotenv

load_dotenv()


logger = create_logger(__name__, level="DEBUG")
