import streamlit as st
from backend import graph

st.title("🌤️ WeatherBot")
#Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm WeatherBot, how can I help you?"},]

#Main chat display
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
#Input
if prompt := st.chat_input("Ask about weather..."):
    #Append user msgs to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    state = {"messages": st.session_state.messages}
    state = graph.invoke(state)

    #Append AI response to chat history
    response = state["messages"][-1].content
    st.session_state.messages.append({"role": "assistant", "content": response})

    #Show AI response
    with st.chat_message("assistant"):
        st.write(response)
