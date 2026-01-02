import os
import streamlit as st
from groq import Groq
from duckduckgo_search import DDGS

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="centered"
)

# ================= BLACK NEON BLUE UI =================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Pure black background */
.stApp {
    background: radial-gradient(circle at top, #050b1a 0%, #020409 60%);
    color: #e5e7eb;
}

/* Kill Streamlit header */
header[data-testid="stHeader"] {
    display: none;
}

/* Main width */
.block-container {
    max-width: 920px;
    padding-top: 1.2rem;
}

/* Remove avatars */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* Chat spacing */
.stChatMessage {
    padding: 0.7rem 0;
}

/* USER — DARK NEON BLUE BOX (RIGHT) */
.stChatMessage[data-testid="chat-message-user"] > div {
    background: linear-gradient(180deg, #081a3a, #06132b);
    color: #dbeafe;
    padding: 14px 16px;
    border-radius: 14px;
    max-width: 78%;
    margin-left: auto;
    border: 1px solid rgba(59,130,246,0.45);
    box-shadow: 0 0 16px rgba(59,130,246,0.15);
}

/* AI — NEON BLUE GLASS BOX (LEFT) */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: linear-gradient(180deg, #0b1f44, #081736);
    color: #eff6ff;
    padding: 16px 18px;
    border-radius: 16px;
    max-width: 78%;
    margin-right: auto;
    border: 1px solid rgba(96,165,250,0.55);
    box-shadow: 0 0 22px rgba(96,165,250,0.22);
}

/* Perplexity-style sources */
.sources {
    margin-top: 10px;
    padding-top: 8px;
    border-top: 1px dashed rgba(96,165,250,0.35);
    font-size: 13px;
    color: #93c5fd;
}
.sources a {
    display: inline-block;
    margin: 4px 6px 0 0;
    padding: 4px 10px;
    border-radius: 999px;
    background: rgba(59,130,246,0.15);
    border: 1px solid rgba(96,165,250,0.45);
    text-decoration: none;
    color: #bfdbfe;
}
.sources a:hover {
    background: rgba(59,130,246,0.35);
}

/* Input box */
textarea {
    background: #020409 !important;
    color: #e5e7eb !important;
    border: 1px solid rgba(59,130,246,0.6) !important;
    border-radius: 14px !important;
    padding: 14px !important;
    font-size: 15px !important;
}

textarea:focus {
    outline: none !important;
    border-color: #60a5fa !important;
    box-shadow: 0 0 0 1px rgba(96,165,250,0.6);
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #1e3a8a;
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
    "<p style='opacity:0.55;margin-top:-12px;color:#93c5fd;'>Silent • Fast • Intelligent</p>",
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

SEARCH RULES
- Use provided sources when available.
- Never invent citations.
- If sources are weak or missing, say so clearly.

CORE PRINCIPLES
- Accuracy over confidence.
- Never give medical, legal, or financial trading advice.
- Never predict prices or give buy/sell signals.

STYLE
- Professional, calm, concise.
- No emojis.
- Clear reasoning.
"""
}

# ================= SEARCH FUNCTION (FREE) =================
def web_search(query, max_results=4):
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                "title": r.get("title"),
                "href": r.get("href")
            })
    return results

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

        if msg.get("sources"):
            st.markdown("<div class='sources'><strong>Sources</strong><br>", unsafe_allow_html=True)
            for s in msg["sources"]:
                st.markdown(
                    f"<a href='{s['href']}' target='_blank'>{s['title']}</a>",
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)

# ================= USER INPUT =================
user_input = st.chat_input("Ask anything…")

if user_input:
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    # 🔍 Perplexity-style search
    sources = web_search(user_input)

    context_block = ""
    if sources:
        context_block = "SOURCES:\n" + "\n".join(
            f"- {s['title']}" for s in sources
        )

    messages_for_groq = [
        SYSTEM_MESSAGE,
        {"role": "system", "content": context_block},
        *st.session_state.messages[-6:]
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
        "content": full_reply,
        "sources": sources
    })

    st.rerun()
