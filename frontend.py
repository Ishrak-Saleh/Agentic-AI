import streamlit as st
from backend import graph


col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
with col3: st.header("WeatherBot")

#Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I'm WeatherBot, what's your name?"},]

#Main chat display
for message in st.session_state.messages:
    if message["role"] == "assistant":
        with st.chat_message("assistant", avatar="🌤️"):
            st.write(message["content"])
    else:
        with st.chat_message(message["role"], avatar="👤"):
            st.write(message["content"])
#Input
if prompt := st.chat_input("Ask about weather..."):
    #Append user msgs to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.write(prompt)

    state = {"messages": st.session_state.messages}
    state = graph.invoke(state)

    #Append AI response to chat history
    response = state["messages"][-1].content
    st.session_state.messages.append({"role": "assistant", "content": response})

    #Show AI response
    with st.chat_message("assistant", avatar="🌤️"):
        st.write(response)
