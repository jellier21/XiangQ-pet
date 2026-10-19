from fastapi import FastAPI

from handle.server.answer import AnswerTextContent
from handle.server.ping import PingPong


class HandleApi:
    def __init__(self,app):
        self.app = app
        super().__init__()

        @self.app.get("/ping")
        async def ping_pong():
            return PingPong()

        @self.app.get("/api/answer/text")
        async def answer_text(word: str, uuid: str):
            return AnswerTextContent(word, uuid)
