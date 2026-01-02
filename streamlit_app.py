import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="wide"
)

# ================= UI =================
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

.row { display: flex; margin-bottom: 0.8rem; }
.row.user { justify-content: flex-end; }
.row.ai { justify-content: flex-start; }

.bubble {
    max-width: 75%;
    padding: 0.8rem 1rem;
    border-radius: 14px;
    line-height: 1.6;
    font-size: 0.95rem;
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
    "content": """
You are DarkFury.

Rules:
- Be helpful and honest.
- Do NOT block normal questions.
- If user asks something unsafe, give a warning instead of refusing.
- Be natural and conversational.
- No fake sources.
"""
}

# ================= CHAT UI =================
st.markdown("<div class='chat'>", unsafe_allow_html=True)

for m in st.session_state.messages:
    role = "user" if m["role"] == "user" else "ai"
    st.markdown(
        f"""
        <div class="row {role}">
            <div class="bubble {role}">
                {m["content"]}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

# ================= INPUT =================
user_input = st.chat_input("Ask anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[SYSTEM_PROMPT] + st.session_state.messages,
            temperature=0.7,
            max_tokens=600
        )

        reply = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": reply})

        st.rerun()

    except Exception as e:
        st.error("Something went wrong. Try again.")
        st.caption(str(e))
