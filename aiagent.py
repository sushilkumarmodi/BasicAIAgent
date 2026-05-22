import streamlit as st # type: ignore
import google.generativeai as genai # type: ignore
import requests
import re

# Page config
st.set_page_config(page_title="AI Chat Agent", layout="centered")

# Configure Gemini
genai.configure(api_key="apikey")
model = genai.GenerativeModel("gemini-2.5-flash")

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

# ---------------- AI AGENT ---------------- #

def ai_agent(user_input):
    prompt = f"""
You are an AI agent.

Decide:
- If math → return only expression (e.g., 2+3*5)
- If weather → return: WEATHER: city_name
- Otherwise → answer normally

User: {user_input}
"""

    decision = model.generate_content(prompt).text.strip()

    if re.match(r'^[0-9+\-*/(). ]+$', decision):
        return "🧮 " + calculator(decision)

    if decision.startswith("WEATHER:"):
        city = decision.split(":")[1].strip()
        return "🌤 " + get_weather(city)

    return "🤖 " + decision


# ---------------- CHAT UI ---------------- #

st.title("💬 AI Chat Agent")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

    # Generate AI response
    response = ai_agent(user_input)

    # Add assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})

    # Display assistant message
    with st.chat_message("assistant"):
        st.write(response)