# FIXED VERSION — BLUE BLOCK REMOVED COMPLETELY
# Only ONE change: removed background + border from chat wrapper.
# Everything else stays the same.

import os
from typing import List, Dict
import streamlit as st
from groq import Groq

st.set_page_config(page_title="XO AI — Nexo.corp", page_icon="🤖", layout="wide")

# ---------- CSS FIX (blue block removed) ----------
CUSTOM_CSS = """
<style>
    .stApp {
        background: radial-gradient(circle at top left, #151b2b 0, #050816 40%, #02010a 100%) !important;
        color: #f9fafb !important;
    }

    header[data-testid="stHeader"] { background: transparent; }

    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1.5rem !important;
        max-width: 1200px !important;
    }

    /* BLUE BLOCK REMOVED COMPLETELY */
    .xo-chat-wrapper {
        padding: 0;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin: 0;
        height: auto !important;
        min-height: 0 !important;
    }

    .xo-chat-scroll {
        padding: 0;
    }

    /* Chat bubbles */
    .xo-msg-row { display: flex; margin-bottom: 0.45rem; }
    .xo-msg-row.user { justify-content: flex-end; }
    .xo-msg-row.assistant { justify-content: flex-start; }

    .xo-msg-bubble {
        max-width: 80%;
        padding: 0.6rem 0.8rem;
        border-radius: 0.9rem;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .xo-msg-bubble.user {
        background: rgba(59, 130, 246, 0.35);
        border: 1px solid rgba(59, 130, 246, 0.8);
    }

    .xo-msg-bubble.assistant {
        background: rgba(31, 41, 55, 0.9);
        border: 1px solid rgba(75, 85, 99, 0.8);
    }

    .xo-msg-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #9ca3af;
        margin-bottom: 0.15rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------- MODEL MAP ----------
MODEL_ID_MAP = {
    "llama3-8b-8192": "llama-3.1-8b-instant",
    "llama3-70b-8192": "llama-3.3-70b-versatile",
}

MODES = ["Study Helper", "Idea Generator", "Planner", "Friendly Chat"]

# ---------- STATE ----------
def init_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "mode" not in st.session_state:
        st.session_state.mode = "Friendly Chat"

# ---------- GROQ ----------

def client():
    return Groq(api_key=os.environ.get("GROQ_API_KEY"))

# ---------- PROMPTS ----------

def system_prompt():
    base = (
        "You are XO AI from Nexo.corp. Simple, calm, respectful. "
        "No financial or harmful content. Step-by-step when needed."
    )
    return base

# ---------- CHAT UI ----------

def render_chat(model_id):
    st.markdown("<div class='xo-chat-wrapper'>", unsafe_allow_html=True)

    html = ["<div class='xo-chat-scroll'>"]

    for m in st.session_state.messages:
        role = m["role"]
        label = "You" if role == "user" else "XO AI"
        cls = role
        text = (
            m["content"].replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        html.append(
            f"<div class='xo-msg-row {cls}'>"
            f"<div class='xo-msg-bubble {cls}'>"
            f"<div class='xo-msg-label'>{label}</div>"
            f"{text}</div></div>"
        )

    html.append("</div>")
    st.markdown("\n".join(html), unsafe_allow_html=True)

    user_input = st.chat_input("Ask XO AI...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking…"):
            try:
                response = client().chat.completions.create(
                    model=MODEL_ID_MAP.get(model_id, model_id),
                    messages=[{"role": "system", "content": system_prompt()}] + st.session_state.messages,
                )
                reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error("XO AI hit a limit. Try again.")
                st.caption(str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- MAIN ----------

def main():
    init_state()

    with st.expander("Model settings", expanded=False):
        model = st.radio("Choose Groq model", ["llama3-8b-8192", "llama3-70b-8192"], horizontal=True)

    render_chat(model)

main()
