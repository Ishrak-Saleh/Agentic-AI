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
    '''Get comprehensive weather data using WeatherAPI'''
    API_KEY = os.getenv("WEATHER_API_KEY")  #https://www.weatherapi.com/
    BASE_URL = "http://api.weatherapi.com/v1/current.json"

    params = {
        'key': API_KEY,
        'q': city,
        'aqi': 'yes'  #Air quality data
    }

    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()

        if 'error' not in data:
            current = data['current']
            location = data['location']

            return (
                    "Weather in " + location['name'] + ", " + location['country'] + ":\n" +
                    "Condition: " + current['condition']['text'] + "\n" +
                    "Temperature: " + str(current['temp_c']) + "°C (Feels like: " + str(
                current['feelslike_c']) + "°C)\n" +
                    "Humidity: " + str(current['humidity']) + "%\n" +
                    "Wind: " + str(current['wind_kph']) + " km/h " + current['wind_dir'] + "\n" +
                    "Visibility: " + str(current['vis_km']) + " km\n" +
                    "UV Index: " + str(current['uv']) + "\n" +
                    "Air Quality: " + str(current.get('air_quality', {}).get('us-epa-index', 'N/A'))
            )
        else: return "Error: " + data['error']['message']
    except Exception as e: return "Error fetching weather data: " + str(e)

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
