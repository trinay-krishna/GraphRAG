from langchain.chat_models import init_chat_model

llm = init_chat_model(
    model="ollama:llama3.2",
    temperature=0
)

def get_llm( ):
    return llm 

def invoke_llm( query ):
    return llm.invoke(query)
