import streamlit as st
from groq import Groq
from datetime import datetime
import html

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="XO AI",
    page_icon="🤖",
    layout="wide",
)

# -----------------------------
# GROQ CLIENT
# -----------------------------
# Make sure GROQ_API_KEY is set in Streamlit secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
DEFAULT_MODEL = "llama-3.1-8b-instant"

# -----------------------------
# SYSTEM PROMPT
# -----------------------------
SYSTEM_PROMPT = """
You are XO AI, a calm, professional and intelligent assistant created by Nexo.corp.

- Be clear, respectful and mature.
- Strong at: studies, maths, coding, tech, business, psychology, productivity and daily life.
- Understand user emotions and reply with empathy when needed.
- Use short paragraphs and bullet points when helpful.
- Do not be cringe or childish.
- If you are not sure, say so honestly and explain the uncertainty.
"""

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    # store only role + content (timestamps separate)
    st.session_state.messages = []
if "times" not in st.session_state:
    st.session_state.times = []  # parallel list of timestamps


def add_message(role: str, content: str):
    """Add a chat message with current time."""
    st.session_state.messages.append({"role": role, "content": content})
    st.session_state.times.append(datetime.now().strftime("%I:%M %p"))


def reset_chat():
    st.session_state.messages = []
    st.session_state.times = []


# -----------------------------
# BASIC STYLES (CLEAN DARK UI)
# -----------------------------
st.markdown(
    """
<style>
body, .stApp {
    background: #111215;
    color: #ffffff;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

/* center container */
.block-container {
    max-width: 900px;
    padding-top: 1.2rem;
    padding-bottom: 2rem;
}

/* hide default chrome */
header, #MainMenu, footer {visibility: hidden;}

/* Title */
.app-title {
    font-size: 1.6rem;
    font-weight: 600;
}

/* Chat window */
.chat-window {
    margin-top: 1rem;
    background: #15171a;
    border-radius: 14px;
    border: 1px solid #2c2f33;
    padding: 16px;
    max-height: calc(100vh - 260px);
    overflow-y: auto;
}

/* message rows */
.msg-row {
    display: flex;
    margin-bottom: 12px;
}
.msg-row.user { justify-content: flex-end; }
.msg-row.assistant { justify-content: flex-start; }

/* bubbles */
.bubble {
    max-width: 78%;
    padding: 10px 14px;
    border-radius: 14px;
    font-size: 0.95rem;
    line-height: 1.4;
    word-wrap: break-word;
}
.bubble.assistant {
    background: #000000;
    border: 1px solid #303238;
}
.bubble.user {
    background: #1c1f24;
    border: 1px solid #3a3d42;
}

/* timestamp */
.msg-time {
    font-size: 0.7rem;
    color: #9ca3af;
    margin-top: 4px;
    text-align: right;
}

/* input area */
.input-box {
    margin-top: 1rem;
    background: #15171a;
    border-radius: 999px;
    border: 1px solid #2c2f33;
    padding: 6px 14px;
}

/* send button */
.stButton>button {
    border-radius: 999px;
    border: none;
    background: #6366f1;
    color: white;
    padding: 6px 20px;
    font-size: 0.9rem;
}

/* text input visual */
div[data-baseweb="input"] {
    background: transparent !important;
    border: none !important;
}
div[data-baseweb="input"] > div {
    background: transparent !important;
    border: none !important;
}
div[data-baseweb="input"] input {
    background: transparent !important;
    color: #f5f5f5 !important;
    font-size: 0.95rem !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# HEADER
# -----------------------------
h1_left, h1_right = st.columns([0.7, 0.3])
with h1_left:
    st.markdown("<div class='app-title'>XO AI (Free)</div>", unsafe_allow_html=True)
with h1_right:
    if st.button("New chat"):
        reset_chat()
        st.rerun()

st.write("---")

# -----------------------------
# MODEL DROPDOWN (optional)
# -----------------------------
model_choice = st.selectbox(
    "Groq model:",
    [
        "LLaMA-3.1-8B (fast & smart)",
        "Mixtral-8x7B (reasoning)",
        "Gemma-2-9B (clean tone)",
    ],
)
MODEL_MAP = {
    "LLaMA-3.1-8B (fast & smart)": "llama-3.1-8b-instant",
    "Mixtral-8x7B (reasoning)": "mixtral-8x7b-32768",
    "Gemma-2-9B (clean tone)": "gemma2-9b-it",
}
model_name = MODEL_MAP.get(model_choice, DEFAULT_MODEL)

# -----------------------------
# CHAT WINDOW
# -----------------------------
st.markdown("<div class='chat-window'>", unsafe_allow_html=True)

def safe(text: str) -> str:
    return html.escape(text).replace("\n", "<br>")

for idx, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    cls = "user" if role == "user" else "assistant"
    text = safe(msg["content"])
    time_str = st.session_state.times[idx]

    st.markdown(
        f"""
        <div class="msg-row {cls}">
            <div class="bubble {cls}">
                {text}
                <div class="msg-time">{time_str}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# INPUT AREA
# -----------------------------
st.markdown("<div class='input-box'>", unsafe_allow_html=True)
with st.form("chat-input", clear_on_submit=True):
    c1, c2 = st.columns([0.85, 0.15])
    with c1:
        user_text = st.text_input(
            "",
            placeholder="Ask XO AI anything...",
            label_visibility="collapsed",
        )
    with c2:
        send = st.form_submit_button("Send")
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# HANDLE SEND
# -----------------------------
if send and user_text.strip():
    user_text = user_text.strip()
    add_message("user", user_text)

    with st.spinner("XO is thinking..."):
        # build history for Groq (only role + content)
        history = [{"role": "system", "content": SYSTEM_PROMPT}]
        history.extend(st.session_state.messages)

        response = client.chat.completions.create(
            model=model_name,
            messages=history,
            temperature=0.4,
            max_tokens=700,
        )
        answer = response.choices[0].message.content.strip()

    add_message("assistant", answer)
    st.rerun()
