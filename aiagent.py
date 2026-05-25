import streamlit as st # type: ignore
import google.generativeai as genai # type: ignore
import requests
import re


# Configure API
genai.configure(api_key="YOUR_API_KEY")
model = genai.GenerativeModel("gemini-1.5-pro")

st.set_page_config(page_title="AI Chat Agent", layout="centered")
st.title("💬 AI Chat Agent with Memory")

# ---------------- TOOLS ---------------- #

def calculator(expression):
    try:
        if re.match(r'^[0-9+\-*/(). ]+$', expression):
            return str(eval(expression))
        return "Invalid expression"
    except:
        return "Calculation error"

def get_weather(city):
    try:
        url = f"https://wttr.in/{city}?format=3"
        response = requests.get(url)
        return response.text
    except:
        return "Weather API error"

# ---------------- MEMORY + CONTEXT ---------------- #

def ai_agent(user_input, chat_history):
    # Convert history into context
    history_text = ""
    for msg in chat_history:
        role = msg["role"]
        content = msg["content"]
        history_text += f"{role}: {content}\n"

    # Prompt with context
    prompt = f"""
You are a smart AI assistant with memory.

Conversation so far:
{history_text}

Now handle the latest user input.

Rules:
- If math → return only expression
- If weather → return: WEATHER: city_name
- Otherwise → answer normally, using context if needed

User: {user_input}
"""

    decision = model.generate_content(prompt).text.strip()

    # Tool: Calculator
    if re.match(r'^[0-9+\-*/(). ]+$', decision):
        return "🧮 " + calculator(decision)

    # Tool: Weather
    if decision.startswith("WEATHER:"):
        city = decision.split(":")[1].strip()
        return "🌤 " + get_weather(city)

    return "🤖 " + decision


# ---------------- CHAT UI ---------------- #

# Store chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Show user message
    with st.chat_message("user"):
        st.write(user_input)

    # Get response WITH memory
    response = ai_agent(user_input, st.session_state.messages)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Show assistant response
    with st.chat_message("assistant"):
        st.write(response)

# Clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
