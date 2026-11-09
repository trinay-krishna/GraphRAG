import operator

from typing import Annotated
from typing_extensions import TypedDict

from langchain.chat_models import init_chat_model
from langchain.messages import AnyMessage, SystemMessage, HumanMessage, ToolMessage

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver

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

tools_by_name = {
    tool.name : tool 
    for tool in tools
}

chat_model_with_tools = chat_model.bind_tools( tools = tools )

SYSTEM_PROMPT = """
    You are an intelligent Graph Database Assistant.
    Your role is to answer user queries by retrieving and reasoning over
    information stored in the Neo4j graph database.

    Use the available graph retrieval tools to fetch relevant information
    and provide accurate, clear, and concise answers based on the results.
"""

class MessagesState(TypedDict):
    messages: Annotated[ list[AnyMessage], operator.add ]


def llm_node( state: MessagesState ):

    model_response = chat_model_with_tools.invoke(
        [
            SystemMessage(
                content = SYSTEM_PROMPT
            )
        ]
        + state["messages"]
    )

    return {
        "messages" : [ model_response ]
    }


def tool_node( state: MessagesState ):
    results = []

    for tool_call in state["messages"][-1].tool_calls:
        tool = tools_by_name[tool_call["name"]]

        tool_result = tool.invoke( tool_call["args"] )

        results.append(
            ToolMessage(
                content = tool_result,
                tool_call_id = tool_call["id"]
            )
        )

    return {
        "messages" : results
    }

def should_call_tool( state: MessagesState ):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tool_node"

    return END


graph = StateGraph(MessagesState)

graph.add_node( "llm_node", llm_node )
graph.add_node( "tool_node", tool_node )

graph.add_edge( START, "llm_node" )

graph.add_conditional_edges(
    "llm_node",
    should_call_tool,
    [ "tool_node", END ]
)

graph.add_edge( "tool_node", "llm_node" )

checkpointer = InMemorySaver()

agent = graph.compile( checkpointer = checkpointer )


def chatbot( user_query : str, thread_id : str ):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    stream = agent.stream_events(
        {
            "messages": [
                HumanMessage(
                    content = user_query
                )
            ]
        },
        version = "v3",
        config = config
    )

    for message in stream.messages:
        for token in message.text:
            print(token, end = "", flush = True)
    print()
    
    final_state = stream.output 