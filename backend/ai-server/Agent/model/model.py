import os
from langchain_openai import ChatOpenAI


def InitModel():
    return ChatOpenAI(
        model=os.getenv("MODEL_NAME"),
        api_key=os.getenv("MODEL_KEY"),
        base_url=os.getenv("MODEL_URLBASE")
    )