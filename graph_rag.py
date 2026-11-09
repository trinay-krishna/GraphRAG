import operator

from typing import Annotated
from typing_extensions import TypedDict

from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

from langgraph.graph import StateGraph, MessagesState, START, END

from fetch_graph import fetch_subgraph_from_query
from text2cypher import text2cypher

chat_model = init_chat_model(
    model = "ollama:llama3.2",
    temperature = 0
)

tools = [
    fetch_subgraph_from_query,
    text2cypher
]

chat_model_with_tools = chat_model.bind_tools( tools = tools )

class MessagesState(TypedDict):
    messages: Annotated[ list[AnyMessage], operator.add ]





graph = StateGraph(MessagesState)

