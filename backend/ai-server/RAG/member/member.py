from langchain_openai import OpenAIEmbeddings


def InsertMemberText(type,word):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector = embeddings.embed_query(word)