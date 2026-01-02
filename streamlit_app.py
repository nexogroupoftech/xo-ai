import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="centered"
)

# ================= NEW MODERN UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* App background */
.stApp {
    background-color: #0b0d12;
    color: #e5e7eb;
}

/* Remove Streamlit header */
header[data-testid="stHeader"] {
    display: none;
}

/* Main width */
.block-container {
    max-width: 860px;
    padding-top: 1.2rem;
}

/* Remove avatars */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* Chat spacing */
.stChatMessage {
    padding: 0.6rem 0;
}

/* USER MESSAGE */
.stChatMessage[data-testid="chat-message-user"] > div {
    background: #1c1f26;
    color: #e5e7eb;
    padding: 14px 16px;
    border-radius: 14px;
    max-width: 78%;
    margin-left: auto;
    box-shadow: inset 0 0 0 1px #2a2f3a;
}

/* AI MESSAGE */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: #12151c;
    color: #d1d5db;
    padding: 14px 16px;
    border-radius: 14px;
    max-width: 78%;
    margin-right: auto;
    box-shadow: inset 0 0 0 1px #1f2430;
}

/* Input */
textarea {
    background-color: #0b0d12 !important;
    color: #e5e7eb !important;
    border: 1px solid #2a2f3a !important;
    border-radius: 12px !important;
    padding: 14px !important;
}

textarea:focus {
    outline: none !important;
    border-color: #4f46e5 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #2a2f3a;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ================= STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = False

# ================= TITLE =================
st.markdown("## DarkFury")
st.markdown(
    "<p style='opacity:0.5;margin-top:-12px;'>Silent • Fast • Intelligent</p>",
    unsafe_allow_html=True
)

# ================= GROQ CLIENT =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ================= SYSTEM PROMPT =================
SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are DarkFury — a precise, honest, and high-performance AI assistant.

CORE PRINCIPLES
- Accuracy over confidence.
- Never hallucinate facts or sources.
- Never give medical, legal, or financial trading advice.
- Never predict prices or give buy/sell signals.
- If unsure, say so clearly.

STYLE
- Calm, professional, concise.
- No emojis.
- Clear reasoning.

You are not ChatGPT.
You are DarkFury.
"""
}

# ================= WELCOME =================
if not st.session_state.welcome_done:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "I’m DarkFury. Ask anything."
    })
    st.session_state.welcome_done = True

# ================= CHAT HISTORY =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================= INPUT =================
user_input = st.chat_input("Ask anything…")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    recent = st.session_state.messages[-8:]

    messages_for_groq = [SYSTEM_MESSAGE] + [
        {"role": m["role"], "content": m["content"]}
        for m in recent
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages_for_groq,
            temperature=0.4,
            max_tokens=500,
            stream=True
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            full_reply += delta
            placeholder.markdown(full_reply)

    st.session_state.messages.append({
        "role": "assistant",
        "content": full_reply
    })

    st.rerun()
