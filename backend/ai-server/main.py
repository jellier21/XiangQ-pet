from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from handle.handle import HandleApi

app = FastAPI()
HandleApi(app)
