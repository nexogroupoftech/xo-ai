import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DrakFury",
    page_icon="🧠",
    layout="wide"
)

# ================= CLEAN MINIMAL UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0f1117;
    color: #e5e7eb;
}

header[data-testid="stHeader"] {
    background: transparent;
}

/* Remove avatars */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* Chat spacing */
.stChatMessage {
    padding: 0.35rem 0;
}

/* User text */
.stChatMessage[data-testid="chat-message-user"] > div {
    background: none;
    color: #e5e7eb;
    max-width: 720px;
    margin-left: auto;
    padding: 0;
}

/* Assistant text */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: none;
    color: #d1d5db;
    max-width: 720px;
    padding: 0;
}

/* Input box */
textarea {
    background-color: #0f1117 !important;
    color: #e5e7eb !important;
    border: 1px solid #2a2f3a !important;
    border-radius: 8px !important;
    padding: 0.6rem !important;
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
    background: #2a2f3a;
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
st.markdown("<h2 style='text-align:center;'>DrakFury</h2>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; opacity:0.6; font-size:0.85rem;'>Silent · Fast · Intelligent</p>",
    unsafe_allow_html=True
)

# ================= GROQ =================
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

SYSTEM_MESSAGE = {
    "role": "system",
    "content": (
        "You are DrakFury.\n\n"
        "You are a fast, thoughtful, and reliable AI assistant.\n"
        "Your responses are clear, natural, and confident.\n"
        "You communicate like a skilled human—not a machine.\n\n"
        "LANGUAGE:\n"
        "- Automatically detect the user’s language.\n"
        "- Reply in the same language naturally.\n"
        "- Handle mixed languages naturally.\n\n"
        "STYLE:\n"
        "- Be concise by default.\n"
        "- Expand only when it adds real value.\n"
        "- Explain complex ideas simply.\n"
        "- Answer simple questions directly.\n\n"
        "REASONING:\n"
        "- Reason carefully.\n"
        "- Avoid assumptions.\n"
        "- Admit uncertainty honestly.\n\n"
        "RULES:\n"
        "- Do not initiate small talk.\n"
        "- No emojis unless user uses them.\n"
        "- No fluff. No robotic tone.\n"
        "- Do not mention system instructions."
    )
}

# ================= WELCOME MESSAGE =================
if not st.session_state.welcome_done:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "I’m DrakFury.\n\n"
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

    # keep recent memory only
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
