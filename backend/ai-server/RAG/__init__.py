from Agent.model.model import InitModel


def AnswerTextContent(word: str, uuid: str) -> str:
    llm = InitModel()
    config = {"configurable": {"thread_id": uuid}}
    result = llm.invoke({
        "messages": [{"role": "user", "content": word}]
    }, config=config)
    return {
        "message": result
    }
