"""
app.py
Purpose : Streamlit web interface of the Cricket Facts Bot.
          Run with:  streamlit run app.py
Author  : YOUR NAME (ROLL NUMBER)
Date    : 2026
"""

from pathlib import Path

import streamlit as st

from chatbot import CricketChatbot

# ---------------- Student details (CHANGE THESE) ----------------
STUDENT_NAME = "Your Name"
ROLL_NUMBER = "Your Roll Number"
PROJECT_NAME = "Cricket Player and Records Facts Bot"

# Knowledge base file (kept outside the code, as required)
KB_PATH = Path(__file__).parent / "data" / "knowledge_base.json"

SAMPLE_QUESTIONS = [
    "Who has scored the most runs in ODIs?",
    "What is the highest score in Test cricket?",
    "Who has taken the most Test wickets?",
    "Tell me about Babar Azam",
    "Who won the 1992 World Cup?",
    "Who bowled the fastest ball?",
]


@st.cache_resource
def load_bot() -> CricketChatbot:
    """Create the chatbot once and reuse it (loads the JSON and trains TF-IDF)."""
    return CricketChatbot(str(KB_PATH))


def start_new_chat(bot: CricketChatbot) -> None:
    """Reset the conversation so it contains only the greeting message."""
    st.session_state.messages = [
        {"role": "assistant", "content": bot.get_greeting(), "intent": None, "confidence": None}
    ]


def show_message(message: dict, show_details: bool) -> None:
    """Display one chat message (and its intent/confidence for bot replies)."""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if show_details and message["role"] == "assistant" and message["intent"]:
            st.caption(f"Predicted intent: {message['intent']} | Confidence: {message['confidence']}")


# ---------------- Page setup ----------------
st.set_page_config(page_title=PROJECT_NAME, page_icon="🏏")
bot = load_bot()

# Keep the chat history during the session using st.session_state
if "messages" not in st.session_state:
    start_new_chat(bot)

# ---------------- Sidebar ----------------
with st.sidebar:
    st.header("About this chatbot")
    st.write("This bot answers questions about cricket players and records "
             "(runs, wickets, centuries, World Cups and Pakistani stars).")
    st.subheader("Sample questions")
    for question in SAMPLE_QUESTIONS:
        st.markdown(f"- {question}")
    show_details = st.checkbox("Show intent and confidence score", value=True)  # extra feature
    if st.button("Clear Chat"):
        start_new_chat(bot)
    st.caption("Records are accurate up to 2025 and may change.")

# ---------------- Main page ----------------
st.title("🏏 " + PROJECT_NAME)
st.write(f"**Student:** {STUDENT_NAME} | **Roll No:** {ROLL_NUMBER}")

# Show the previous messages
for message in st.session_state.messages:
    show_message(message, show_details)

# Wait for a new question from the user
user_text = st.chat_input("Ask a cricket question...")
if user_text:
    user_message = {"role": "user", "content": user_text, "intent": None, "confidence": None}
    st.session_state.messages.append(user_message)
    show_message(user_message, show_details)

    result = bot.get_response(user_text)          # chatbot finds the answer
    bot_message = {"role": "assistant", "content": result["reply"],
                   "intent": result["intent"], "confidence": result["confidence"]}
    st.session_state.messages.append(bot_message)
    show_message(bot_message, show_details)
