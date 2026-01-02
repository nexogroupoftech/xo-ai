import os
import html
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="wide"
)

# ================= UI STYLE =================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top left, #0b1220, #020617 45%, #000 100%);
    color: #e5e7eb;
    font-family: Inter, system-ui;
}

header { display: none; }

.chat {
    max-width: 900px;
    margin: auto;
    padding-top: 2rem;
}

.row {
    display: flex;
    margin-bottom: 0.8rem;
}

.row.user { justify-content: flex-end; }
.row.ai { justify-content: flex-start; }

.bubble {
    max-width: 75%;
    padding: 0.8rem 1rem;
    border-radius: 14px;
    line-height: 1.6;
    font-size: 0.95rem;
    white-space: pre-wrap;
}

.bubble.user {
    background: rgba(59,130,246,0.25);
    border: 1px solid rgba(59,130,246,0.7);
}

.bubble.ai {
    background: rgba(15,23,42,0.95);
    border: 1px solid rgba(148,163,184,0.25);
}
</style>
""", unsafe_allow_html=True)

# ================= STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= GROQ =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are DarkFury. Be helpful and natural. "
        "If a request is unsafe, warn instead of refusing."
    )
}

# ================= RENDER CHAT =================
st.markdown("<div class='chat'>", unsafe_allow_html=True)

for m in st.session_state.messages:
    role = "user" if m["role"] == "user" else "ai"
    safe_text = html.escape(m["content"])
    st.markdown(
        f"""
        <div class="row {role}">
            <div class="bubble {role}">
                {safe_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# ================= INPUT =================
user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    messages = [SYSTEM_PROMPT] + st.session_state.messages

    with st.spinner("Thinking…"):
        stream = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=600,
            stream=True
        )

        reply = ""
        placeholder = st.empty()

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            reply += delta
            placeholder.markdown(
                html.escape(reply),
                unsafe_allow_html=False
            )

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )

    st.rerun()
