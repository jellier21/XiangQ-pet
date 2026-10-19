from Agent.model.model import InitModel
from langchain_core.messages import HumanMessage


def AnswerTextContent(word: str, uuid: str) -> str:
    llm = InitModel()
    config = {"configurable": {"thread_id": uuid}}
    result = llm.invoke([HumanMessage(content=word)], config=config)
    return {
        "message": result.content
    }
