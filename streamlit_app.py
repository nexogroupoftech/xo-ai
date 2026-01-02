import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🤖",
    layout="wide"
)

# ================= XO-STYLE UI (CLEAN, BOXED, NO SLAB) =================
CUSTOM_CSS = """
<style>
    .stApp {
        background: radial-gradient(circle at top left, #151b2b 0%, #050816 40%, #02010a 100%) !important;
        color: #f9fafb !important;
    }

    header[data-testid="stHeader"] { background: transparent; }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 1200px !important;
    }

    /* CHAT WRAPPER — TRANSPARENT */
    .xo-chat-wrapper {
        padding: 0;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin: 0;
    }

    .xo-chat-scroll {
        padding: 0;
    }

    /* MESSAGE ROWS */
    .xo-msg-row { display: flex; margin-bottom: 0.45rem; }
    .xo-msg-row.user { justify-content: flex-end; }
    .xo-msg-row.assistant { justify-content: flex-start; }

    /* MESSAGE BUBBLES */
    .xo-msg-bubble {
        max-width: 80%;
        padding: 0.65rem 0.85rem;
        border-radius: 0.9rem;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .xo-msg-bubble.user {
        background: rgba(59,130,246,0.35);
        border: 1px solid rgba(59,130,246,0.8);
        color: #e5efff;
    }

    .xo-msg-bubble.assistant {
        background: rgba(31,41,55,0.92);
        border: 1px solid rgba(75,85,99,0.8);
        color: #f3f4f6;
    }

    .xo-msg-label {
        font-size: 0.65rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9ca3af;
        margin-bottom: 0.15rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ================= STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = False

# ================= TITLE =================
st.markdown("## DarkFury")
st.markdown(
    "<p style='opacity:0.6;margin-top:-12px;'>Silent • Fast • Intelligent</p>",
    unsafe_allow_html=True
)

# ================= GROQ CLIENT =================
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ================= SYSTEM PROMPT =================
SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are DarkFury — a precise, honest, and high-performance AI assistant.

CORE PRINCIPLES
- Accuracy over confidence.
- Never hallucinate facts or sources.
- If unsure, say so clearly.
- Never give medical, legal, or financial trading advice.
- Never predict prices or give buy/sell signals.

STYLE
- Professional, calm, concise.
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

# ================= CHAT RENDER (XO STYLE) =================
def render_chat_ui():
    st.markdown("<div class='xo-chat-wrapper'>", unsafe_allow_html=True)
    html = ["<div class='xo-chat-scroll'>"]

    for m in st.session_state.messages:
        role = m["role"]
        label = "You" if role == "user" else "DarkFury"
        text = (
            m["content"]
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        html.append(
            f"<div class='xo-msg-row {role}'>"
            f"<div class='xo-msg-bubble {role}'>"
            f"<div class='xo-msg-label'>{label}</div>"
            f"{text}</div></div>"
        )

    html.append("</div></div>")
    st.markdown("\n".join(html), unsafe_allow_html=True)

render_chat_ui()

# ================= USER INPUT =================
user_input = st.chat_input("Ask anything…")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.spinner("Thinking…"):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[SYSTEM_MESSAGE] + st.session_state.messages,
                temperature=0.4,
                max_tokens=500
            )
            reply = response.choices[0].message.content
            st.session_state.messages.append({
                "role": "assistant",
                "content": reply
            })
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": "Something went wrong. Please try again."
            })

    st.rerun()
