import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="centered"
)

# ================= LIGHT GROK / APPLE UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Apple-style white background */
.stApp {
    background: linear-gradient(180deg, #f9fafb 0%, #ffffff 60%);
    color: #111827;
}

/* Remove Streamlit header */
header[data-testid="stHeader"] {
    display: none;
}

/* Main width */
.block-container {
    max-width: 920px;
    padding-top: 1.5rem;
}

/* Remove avatars */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* Chat spacing */
.stChatMessage {
    padding: 0.7rem 0;
}

/* USER MESSAGE — LIGHT BLUE CARD */
.stChatMessage[data-testid="chat-message-user"] > div {
    background: #eef4ff;
    color: #1e3a8a;
    padding: 14px 16px;
    border-radius: 14px;
    max-width: 78%;
    margin-left: auto;
    border: 1px solid #dbeafe;
}

/* AI MESSAGE — WHITE GLASS CARD */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: rgba(255,255,255,0.9);
    color: #111827;
    padding: 16px 18px;
    border-radius: 16px;
    max-width: 78%;
    margin-right: auto;
    border: 1px solid #e5e7eb;
    box-shadow: 0 6px 20px rgba(0,0,0,0.04);
}

/* Sources block (Perplexity-style) */
.sources {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px dashed #e5e7eb;
    font-size: 13px;
    color: #475569;
}

.sources span {
    display: inline-block;
    margin-right: 8px;
    padding: 4px 8px;
    border-radius: 999px;
    background: #f1f5f9;
    border: 1px solid #e5e7eb;
}

/* Input box */
textarea {
    background: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #c7d2fe !important;
    border-radius: 14px !important;
    padding: 14px !important;
    font-size: 15px !important;
}

textarea:focus {
    outline: none !important;
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 1px rgba(99,102,241,0.4);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #cbd5f5;
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
st.markdown("## DarkFury")
st.markdown(
    "<p style='opacity:0.6;margin-top:-12px;'>Silent • Fast • Intelligent</p>",
    unsafe_allow_html=True
)

# ================= GROQ CLIENT =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
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

SEARCH & SOURCES
- If external information is referenced, clearly separate it as Sources.
- Never invent sources.
- If no sources are available, say so.

STYLE
- Professional, calm, concise.
- No emojis.
- Apple-like clarity.

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

        # Placeholder Perplexity-style sources (UI only)
        if msg["role"] == "assistant" and "Sources:" in msg["content"]:
            st.markdown(
                """
                <div class="sources">
                    <strong>Sources</strong><br>
                    <span>Wikipedia</span>
                    <span>Official Docs</span>
                </div>
                """,
                unsafe_allow_html=True
            )

# ================= USER INPUT =================
user_input = st.chat_input("Ask anything…")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

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
