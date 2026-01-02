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
/* ===== GLOBAL FONT ===== */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ===== APP BACKGROUND ===== */
.stApp {
    background: radial-gradient(circle at top, #0b0f19 0%, #05070d 60%);
    color: #e5e7eb;
}

/* Remove Streamlit header */
header[data-testid="stHeader"] {
    display: none;
}

/* Remove avatars */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* ===== CHAT WRAPPER ===== */
.block-container {
    max-width: 900px;
    padding-top: 1.5rem;
}

/* ===== COMMON MESSAGE STYLE ===== */
.stChatMessage {
    padding: 0.4rem 0;
}

/* ===== USER MESSAGE (NEON BLUE GLASS) ===== */
.stChatMessage[data-testid="chat-message-user"] > div {
    background: rgba(30, 58, 138, 0.15); /* blue glass */
    border: 1px solid rgba(59, 130, 246, 0.35);
    border-radius: 14px;
    padding: 12px 14px;
    max-width: 72%;
    margin-left: auto;
    color: #e5e7eb;
    backdrop-filter: blur(12px);
    box-shadow:
        0 0 0 transparent,
        0 0 18px rgba(59, 130, 246, 0.15);
    transition: all 0.25s ease;
}

/* ===== ASSISTANT MESSAGE (SOFTER NEON) ===== */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: rgba(15, 23, 42, 0.55);
    border: 1px solid rgba(99, 102, 241, 0.25);
    border-radius: 14px;
    padding: 12px 14px;
    max-width: 72%;
    margin-right: auto;
    color: #c7d2fe;
    backdrop-filter: blur(14px);
    box-shadow:
        0 0 0 transparent,
        0 0 16px rgba(99, 102, 241, 0.12);
    transition: all 0.25s ease;
}

/* ===== HOVER FADE EFFECT (DISAPPEAR FEEL) ===== */
.stChatMessage > div:hover {
    opacity: 0.88;
}

/* ===== INPUT BAR ===== */
textarea {
    background: rgba(2, 6, 23, 0.9) !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(59, 130, 246, 0.6) !important;
    border-radius: 16px !important;
    padding: 14px !important;
    font-size: 15px !important;
    backdrop-filter: blur(10px);
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
