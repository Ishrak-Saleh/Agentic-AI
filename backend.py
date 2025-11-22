import os
import requests
from dotenv import load_dotenv
from typing import Annotated

load_dotenv()
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

from langchain.chat_models import init_chat_model

llm = init_chat_model("google_genai:gemini-2.0-flash")
#print(llm.invoke("Hello how are you?"))

class State(TypedDict):
    messages: Annotated[list, add_messages]
    #add_messages is a reducer function, instead of overwriting values it accumulates msgs

@tool
def get_weather_data(city: str) -> str:
    '''Get current weather data using OpenWeatherMap API'''
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': API_KEY,
        'units': 'metric'
    }
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if response.status_code == 200: #HTTP status code for API response
            temp = data['main']['temp']
            humidity = data['main']['humidity']
            condition = data['weather'][0]['description']
            return "Weather in " + city + ": " + condition + ", Temperature: " + str(temp) + "°C, Humidity: " + str(humidity) + "%"
        else:
            return "Could not fetch weather data for " + city + ". Error: " + data.get('message', 'Unknown error')
    except Exception as e:
        return "Error fetching weather data: " + str(e)


tools = [get_weather_data]
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State) -> State:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

builder = StateGraph(State)

builder.add_node("chatbot", chatbot)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition)   #For only when the tools required, tools_condition returns the tools or __end__
builder.add_edge("tools", "chatbot")

#Create hte graph instance
graph = builder.compile()
