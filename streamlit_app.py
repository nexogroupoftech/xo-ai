import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="wide"
)

# ================= HARD RESET STREAMLIT =================
st.markdown("""
<style>
html, body {
    margin: 0 !important;
    padding: 0 !important;
}
header, footer {
    display: none !important;
}
[data-testid="stToolbar"],
[data-testid="stHeader"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] {
    display: none !important;
}
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}
.stApp {
    background: #05070d;
    color: #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# ================= CUSTOM UI CSS =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

* {
    font-family: 'Inter', sans-serif;
}

.chat-container {
    padding: 24px;
    max-width: 900px;
    margin: auto;
}

.brand {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 20px;
    color: #e5e7eb;
}

.msg {
    margin: 10px 0;
    line-height: 1.6;
}

.user {
    color: #93c5fd;
}

.ai {
    color: #c7d2fe;
}

.input-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: #05070d;
    padding: 14px;
    border-top: 1px solid #1e293b;
}

textarea {
    width: 100%;
    background: #020617 !important;
    color: #e5e7eb !important;
    border: 1px solid #2563eb !important;
    border-radius: 14px !important;
    padding: 14px !important;
    font-size: 15px !important;
}
</style>
""", unsafe_allow_html=True)

# ================= STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= BRAND =================
st.markdown(
    "<div class='chat-container'><div class='brand'>DarkFury</div></div>",
    unsafe_allow_html=True
)

# ================= GROQ =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
You are DarkFury — a precise, honest, and high-performance AI assistant.

RULES
- Accuracy over confidence.
- Never hallucinate facts.
- Never give medical, legal, or financial trading advice.
- Never predict prices or give buy/sell signals.
- If unsure, say so clearly.

STYLE
- Calm, concise, professional.
- No emojis.
- Clear reasoning.

You are DarkFury.
"""

# ================= CHAT DISPLAY =================
with st.container():
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        role = "user" if msg["role"] == "user" else "ai"
        label = "You" if role == "user" else "DarkFury"
        st.markdown(
            f"<div class='msg {role}'><strong>{label}:</strong> {msg['content']}</div>",
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ================= INPUT =================
user_input = st.text_area("", placeholder="Ask anything…", key="input")

if user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *st.session_state.messages
        ],
        temperature=0.4,
        max_tokens=400
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})

    st.session_state.input = ""
    st.rerun()
