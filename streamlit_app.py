import os
import time
import streamlit as st
from groq import Groq
from tavily import TavilyClient

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury Pro",
    page_icon="🤖",
    layout="wide"
)

# ================= UI =================
CUSTOM_CSS = """
<style>
.stApp {
    background: radial-gradient(circle at top left, #151b2b 0%, #050816 40%, #02010a 100%);
    color: #f9fafb;
}
header[data-testid="stHeader"] { display: none; }

.block-container {
    max-width: 1200px;
    padding-top: 1.5rem;
}

.xo-msg-row { display:flex; margin-bottom:0.45rem; }
.xo-msg-row.user { justify-content:flex-end; }
.xo-msg-row.assistant { justify-content:flex-start; }

.xo-msg-bubble {
    max-width:80%;
    padding:0.65rem 0.85rem;
    border-radius:0.9rem;
    font-size:0.9rem;
}

.xo-msg-bubble.user {
    background: rgba(59,130,246,0.35);
    border:1px solid rgba(59,130,246,0.8);
}

.xo-msg-bubble.assistant {
    background: rgba(31,41,55,0.92);
    border:1px solid rgba(75,85,99,0.8);
}

.xo-msg-label {
    font-size:0.65rem;
    letter-spacing:0.08em;
    color:#9ca3af;
    margin-bottom:0.15rem;
}

.xo-sources {
    margin-top:0.4rem;
    font-size:0.75rem;
    color:#93c5fd;
}

.xo-sources a {
    display:inline-block;
    margin-right:6px;
    padding:2px 8px;
    border-radius:999px;
    border:1px solid rgba(59,130,246,0.6);
    background:rgba(59,130,246,0.15);
    text-decoration:none;
    color:#bfdbfe;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ================= AUTH =================
if "user" not in st.session_state:
    with st.form("login"):
        st.subheader("Login to DarkFury")
        email = st.text_input("Email")
        submit = st.form_submit_button("Continue")
        if submit and email:
            st.session_state.user = email
            st.session_state.messages = []
            st.rerun()
    st.stop()

# ================= STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_sources" not in st.session_state:
    st.session_state.show_sources = True

# ================= TITLE =================
st.markdown("## DarkFury Pro")
st.caption(f"Logged in as {st.session_state.user}")

with st.expander("⚙️ Settings", expanded=False):
    st.session_state.show_sources = st.toggle("Show sources", True)

# ================= CLIENTS =================
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

MODEL = "llama-3.1-8b-instant"

SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are DarkFury — a precise, honest AI assistant.
Use provided sources when available.
Never invent citations.
If sources are weak, say so clearly.
"""
}

# ================= SEARCH =================
def web_search(query):
    result = tavily.search(query=query, max_results=4)
    return result.get("results", [])

def confidence_score(sources):
    if not sources:
        return 30
    score = min(90, 40 + len(sources) * 15)
    return score

# ================= CHAT UI =================
def render_chat():
    for m in st.session_state.messages:
        role = m["role"]
        label = "You" if role == "user" else "DarkFury"

        st.markdown(
            f"<div class='xo-msg-row {role}'>"
            f"<div class='xo-msg-bubble {role}'>"
            f"<div class='xo-msg-label'>{label}</div>"
            f"{m['content']}</div></div>",
            unsafe_allow_html=True
        )

        if role == "assistant" and st.session_state.show_sources:
            sources = m.get("sources", [])
            confidence = m.get("confidence")

            if sources:
                st.markdown(f"**Confidence:** {confidence}%", unsafe_allow_html=True)
                st.markdown("<div class='xo-sources'>", unsafe_allow_html=True)
                for s in sources:
                    st.markdown(
                        f"<a href='{s['url']}' target='_blank'>{s['title']}</a>",
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

render_chat()

# ================= INPUT =================
user_input = st.chat_input("Ask anything…")

if user_input:
    st.session_state.messages.append({"role":"user","content":user_input})

    # Search first
    sources = web_search(user_input)
    confidence = confidence_score(sources)

    context = "\n".join(f"- {s['title']}" for s in sources)

    placeholder = st.empty()
    streamed = ""

    stream = groq.chat.completions.create(
        model=MODEL,
        messages=[
            SYSTEM_MESSAGE,
            {"role":"system","content":f"SOURCES:\n{context}"},
            *st.session_state.messages
        ],
        stream=True
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        streamed += delta
        placeholder.markdown(
            f"<div class='xo-msg-row assistant'>"
            f"<div class='xo-msg-bubble assistant'>"
            f"<div class='xo-msg-label'>DarkFury</div>"
            f"{streamed}</div></div>",
            unsafe_allow_html=True
        )
        time.sleep(0.01)

    st.session_state.messages.append({
        "role":"assistant",
        "content":streamed,
        "sources":sources,
        "confidence":confidence
    })

    st.rerun()
