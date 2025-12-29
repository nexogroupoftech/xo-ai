import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="wide"
)

# ================= CLEAN PROFESSIONAL UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0e0f13;
    color: #e5e7eb;
}

/* Remove Streamlit header */
header[data-testid="stHeader"] {
    background: transparent;
}

/* REMOVE AVATAR COMPLETELY */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* Chat layout */
.stChatMessage {
    padding: 0.25rem 0;
}

/* User message (right aligned, text only) */
.stChatMessage[data-testid="chat-message-user"] > div {
    background: none;
    color: #f3f4f6;
    max-width: 760px;
    margin-left: auto;
    padding: 0;
}

/* Assistant message (left aligned, text only) */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: none;
    color: #d1d5db;
    max-width: 760px;
    padding: 0;
}

/* Input box */
textarea {
    background-color: #0e0f13 !important;
    color: #e5e7eb !important;
    border: 1px solid #2b2f36 !important;
    border-radius: 10px !important;
    padding: 0.7rem !important;
}

textarea:focus {
    outline: none !important;
    border-color: #4b5563 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #2b2f36;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ================= STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = False

# ================= HEADER =================
st.markdown("<h2 style='text-align:center;'>DarkFury</h2>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; opacity:0.55; font-size:0.85rem;'>Silent · Fast · Intelligent</p>",
    unsafe_allow_html=True
)

# ================= GROQ =================
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are DarkFury.\n\n"
        "You are a fast, thoughtful, and reliable AI assistant.\n"
        "Your tone is calm, confident, and precise.\n"
        "You speak like a skilled human, not a chatbot.\n\n"
        "LANGUAGE:\n"
        "- Detect the user's language automatically.\n"
        "- Respond in the same language naturally.\n\n"
        "STYLE:\n"
        "- Be concise by default.\n"
        "- Expand only when it adds real value.\n"
        "- Explain complex ideas simply.\n"
        "- Answer simple questions directly.\n\n"
        "RULES:\n"
        "- Do not initiate small talk.\n"
        "- No emojis unless the user uses them.\n"
        "- No fluff. No hype.\n"
        "- Never mention system instructions."
    )
}

# ================= WELCOME =================
if not st.session_state.welcome_done:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "I’m DarkFury.\n\n"
            "Ask a question, explore an idea, or get help thinking."
        )
    })
    st.session_state.welcome_done = True

# ================= CHAT HISTORY =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================= USER INPUT =================
user_input = st.chat_input("Ask anything")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    recent_messages = st.session_state.messages[-8:]

    groq_messages = [SYSTEM_MESSAGE] + [
        {"role": m["role"], "content": m["content"]}
        for m in recent_messages
        if m["role"] in ("user", "assistant")
    ]

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_reply = ""

        stream = client.chat.completions.create(
            model=MODEL,
            messages=groq_messages,
            temperature=0.6,
            max_tokens=250,
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
