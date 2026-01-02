import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="centered"
)

# ================= MODERN DARK UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* App background */
.stApp {
    background: radial-gradient(circle at top, #0b0f19 0%, #05070d 60%);
    color: #e5e7eb;
}

/* Remove Streamlit header */
header[data-testid="stHeader"] {
    display: none;
}

/* Chat container */
.block-container {
    max-width: 900px;
    padding-top: 2rem;
}

/* Remove avatars */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* Chat messages */
.stChatMessage {
    padding: 0.4rem 0;
}

/* User bubble */
.stChatMessage[data-testid="chat-message-user"] > div {
    background: linear-gradient(135deg, #1f2933, #111827);
    border-radius: 12px;
    padding: 12px 14px;
    max-width: 75%;
    margin-left: auto;
    color: #e5e7eb;
}

/* Assistant bubble */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: linear-gradient(135deg, #0b1220, #020617);
    border-radius: 12px;
    padding: 12px 14px;
    max-width: 75%;
    margin-right: auto;
    color: #cbd5f5;
    border: 1px solid rgba(99,102,241,0.25);
}

/* Input bar */
textarea {
    background: #020617 !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(99,102,241,0.6) !important;
    border-radius: 14px !important;
    padding: 14px !important;
    font-size: 15px !important;
}

textarea:focus {
    outline: none !important;
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 1px #6366f1;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ================= TOP BAR =================
st.markdown(
    """
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:1rem;">
        <div style="font-size:1.4rem;font-weight:600;">DarkFury</div>
        <div style="opacity:0.5;font-size:0.85rem;">Silent · Fast · Intelligent</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ================= SESSION =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = False

# ================= GROQ =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ================= FULL MASTER PROMPT =================
SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are DarkFury — a precise, honest, and high-performance AI assistant.

RULES
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
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    recent = st.session_state.messages[-8:]

    messages = [SYSTEM_MESSAGE] + [
        {"role": m["role"], "content": m["content"]}
        for m in recent
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.4,
            max_tokens=450,
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
