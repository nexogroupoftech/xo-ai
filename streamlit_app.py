import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="centered"
)

# ================= NEON BLUE GLASS UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* ===== RESET EVERYTHING ===== */
html, body {
    margin: 0 !important;
    padding: 0 !important;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ===== KILL STREAMLIT HEADER & SPACE ===== */
header,
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] {
    display: none !important;
    height: 0 !important;
}

/* ===== REMOVE TOP GAP ===== */
.block-container {
    padding-top: 0.6rem !important;
    margin-top: 0 !important;
    max-width: 900px;
}

/* ===== APP BACKGROUND ===== */
.stApp {
    background: radial-gradient(circle at top, #0b0f19 0%, #05070d 60%);
    color: #e5e7eb;
}

/* ===== REMOVE AVATARS ===== */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* ===== CHAT SPACING ===== */
.stChatMessage {
    padding: 0.45rem 0;
}

/* ===== USER MESSAGE ===== */
.stChatMessage[data-testid="chat-message-user"] > div {
    background: rgba(30, 58, 138, 0.18);
    border: 1px solid rgba(59, 130, 246, 0.45);
    border-radius: 16px;
    padding: 14px 16px;
    max-width: 72%;
    margin-left: auto;
    color: #e5e7eb;
    backdrop-filter: blur(12px);
    box-shadow: 0 0 18px rgba(59, 130, 246, 0.18);
}

/* ===== ASSISTANT MESSAGE ===== */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: rgba(15, 23, 42, 0.65);
    border: 1px solid rgba(99, 102, 241, 0.28);
    border-radius: 16px;
    padding: 14px 16px;
    max-width: 72%;
    margin-right: auto;
    color: #c7d2fe;
    backdrop-filter: blur(14px);
    box-shadow: 0 0 16px rgba(99, 102, 241, 0.14);
}

/* ===== INPUT BAR ===== */
textarea {
    background: rgba(2, 6, 23, 0.95) !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(59, 130, 246, 0.6) !important;
    border-radius: 18px !important;
    padding: 14px !important;
    font-size: 15px !important;
}

textarea:focus {
    outline: none !important;
    border-color: #60a5fa !important;
    box-shadow: 0 0 0 1px #60a5fa;
}

/* ===== SCROLLBAR ===== */
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
        <div style="opacity:0.5;font-size:0.85rem;">Silent - Fast - Intelligent</div>
    </div>
    """,
    unsafe_allow_html=True
)

# ================= SESSION STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = False

# ================= GROQ CLIENT =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ================= FULL MASTER PROMPT =================
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
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages_for_groq,
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
