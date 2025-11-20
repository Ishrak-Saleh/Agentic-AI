from dotenv import load_dotenv
from typing import Annotated

load_dotenv()

from typing_extensions import TypedDict
from langchain.chat_models import init_chat_model
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

from langchain.chat_models import init_chat_model

llm = init_chat_model("google_genai:gemini-2.0-flash")
#llm.invoke("Hello how are you?")

class State(TypedDict):
    messages: Annotated[list, add_messages]
    #add_messages is a reducer function, instead of overwriting values it accumulates msgs

def chatbot(state: State) -> State:
    return {"messages": [llm.invoke(state["messages"])]}

builder = StateGraph(State)
builder.add_node("chatbot_node", chatbot)

builder.add_edge(START, "chatbot_node")
builder.add_edge("chatbot_node", END)

graph = builder.compile()

message = {"role": "user", "content": "Hello!"}
response = graph.invoke({"messages": [message]})
response["messages"]

print(response)