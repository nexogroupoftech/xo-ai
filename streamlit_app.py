import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="centered"
)

# ================= SAFE CHATGPT-STYLE UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Background */
.stApp {
    background-color: #0f1117;
    color: #e5e7eb;
}

/* Remove Streamlit header */
header[data-testid="stHeader"] {
    display: none;
}

/* Chat width */
.block-container {
    max-width: 900px;
    padding-top: 1rem;
}

/* Remove avatars */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* Chat spacing */
.stChatMessage {
    padding: 0.5rem 0;
}

/* USER MESSAGE (RIGHT BOX) */
.stChatMessage[data-testid="chat-message-user"] > div {
    background-color: #1f2937;
    color: #e5e7eb;
    padding: 12px 14px;
    border-radius: 12px;
    max-width: 75%;
    margin-left: auto;
}

/* AI MESSAGE (LEFT BOX) */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background-color: #111827;
    color: #d1d5db;
    padding: 12px 14px;
    border-radius: 12px;
    max-width: 75%;
    margin-right: auto;
    border: 1px solid #1f2937;
}

/* Input box */
textarea {
    background-color: #0f1117 !important;
    color: #e5e7eb !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
    padding: 12px !important;
}

textarea:focus {
    outline: none !important;
    border-color: #6366f1 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #374151;
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
st.markdown("### DarkFury")
st.markdown("<p style='opacity:0.6;margin-top:-10px;'>Silent · Fast · Intelligent</p>", unsafe_allow_html=True)

# ================= GROQ CLIENT =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ================= FULL MASTER SYSTEM PROMPT =================
SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are DarkFury — a precise, honest, and high-performance AI assistant.

CORE RULES
- Accuracy over confidence.
- Never hallucinate facts or sources.
- Never give medical, legal, or financial trading advice.
- Never predict prices or give buy/sell signals.
- If unsure, say so clearly.

STYLE
- Calm, structured, professional.
- No emojis.
- Clear reasoning.
- Ask clarifying questions instead of guessing.

You are not ChatGPT.
You are DarkFury.
"""
}

# ================= WELCOME MESSAGE =================
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

# ================= USER INPUT =================
user_input = st.chat_input("Ask anything…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    recent_messages = st.session_state.messages[-8:]

    messages_for_groq = [SYSTEM_MESSAGE] + [
        {"role": m["role"], "content": m["content"]}
        for m in recent_messages
        if m["role"] in ("user", "assistant")
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
