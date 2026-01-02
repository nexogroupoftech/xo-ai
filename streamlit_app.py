import os
import streamlit as st
from groq import Groq
from tavily import TavilyClient

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="wide"
)

# ================= STYLE =================
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top left, #0b1220, #020617 45%, #000 100%);
    color: #e5e7eb;
    font-family: Inter, system-ui;
}

header { display: none; }

/* Header */
.app-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.5rem;
}

.logo {
    width: 34px;
    height: 34px;
    border-radius: 8px;
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: black;
}

/* Chat */
.chat {
    max-width: 900px;
    margin: auto;
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

/* Sources */
.sources {
    margin-top: 0.6rem;
    padding: 0.6rem;
    border-radius: 10px;
    border: 1px solid rgba(59,130,246,0.4);
    background: rgba(2,6,23,0.9);
    font-size: 0.8rem;
}

.sources a {
    color: #60a5fa;
    text-decoration: none;
}

.confidence {
    margin-top: 0.4rem;
    font-size: 0.75rem;
    color: #93c5fd;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="chat">
  <div class="app-header">
    <div class="logo">DF</div>
    <h3>DarkFury</h3>
  </div>
</div>
""", unsafe_allow_html=True)

# ================= STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= CLIENTS =================
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

MODEL = "llama-3.1-8b-instant"

SYSTEM_PROMPT = {
    "role": "system",
    "content": """
You are DarkFury.
Be helpful and natural.
If a request is unsafe, warn instead of refusing.
Use web sources ONLY if provided.
Never hallucinate sources.
"""
}

# ================= HELPERS =================
def needs_search(query: str) -> bool:
    keywords = ["latest", "news", "today", "define", "who is", "what is", "when", "current"]
    return any(k in query.lower() for k in keywords)

def run_search(query: str):
    result = tavily.search(query, max_results=4)
    return result.get("results", [])

def calc_confidence(n_sources: int):
    if n_sources >= 4:
        return "90%"
    if n_sources == 3:
        return "80%"
    if n_sources == 2:
        return "70%"
    if n_sources == 1:
        return "60%"
    return "50%"

# ================= CHAT RENDER =================
st.markdown("<div class='chat'>", unsafe_allow_html=True)

for m in st.session_state.messages:
    role = "user" if m["role"] == "user" else "ai"
    st.markdown(
        f"""
        <div class="row {role}">
            <div class="bubble {role}">
                {m["content"]}
                {m.get("extra","")}
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

    sources_html = ""
    confidence = "50%"

    context = ""
    sources = []

    if needs_search(user_input):
        results = run_search(user_input)
        for r in results:
            sources.append(r["url"])
            context += f"- {r['content']}\n"

        confidence = calc_confidence(len(sources))

    messages = [SYSTEM_PROMPT]
    if context:
        messages.append({"role": "system", "content": f"Web context:\n{context}"})

    messages += st.session_state.messages

    with st.spinner("Thinking…"):
        stream = groq.chat.completions.create(
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
            placeholder.markdown(reply)

    if sources:
        sources_html = "<div class='sources'><strong>Sources</strong><ul>"
        for s in sources:
            sources_html += f"<li><a href='{s}' target='_blank'>{s}</a></li>"
        sources_html += f"</ul><div class='confidence'>Confidence: {confidence}</div></div>"

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "extra": sources_html
    })

    st.rerun()
