import os
import time
import streamlit as st
from groq import Groq
from tavily import TavilyClient

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🤖",
    layout="wide"
)

# ================= UI =================
st.markdown("""
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

.xo-msg-row { display:flex; margin-bottom:0.5rem; }
.xo-msg-row.user { justify-content:flex-end; }
.xo-msg-row.assistant { justify-content:flex-start; }

.xo-msg-bubble {
    max-width:80%;
    padding:0.65rem 0.85rem;
    border-radius:0.9rem;
    font-size:0.9rem;
    line-height:1.5;
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
    margin-bottom:0.2rem;
}

.xo-sources {
    margin-top:0.4rem;
}

.xo-source-pill {
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:4px 10px;
    margin-right:6px;
    margin-top:6px;
    border-radius:999px;
    background: rgba(59,130,246,0.15);
    border:1px solid rgba(59,130,246,0.6);
    font-size:0.75rem;
    color:#bfdbfe;
    text-decoration:none;
}

.xo-source-pill img {
    width:16px;
    height:16px;
    border-radius:4px;
}
</style>
""", unsafe_allow_html=True)

# ================= STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ================= CLIENTS =================
groq = Groq(api_key=os.environ.get("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.environ.get("TAVILY_API_KEY"))

MODEL = "llama-3.1-8b-instant"

SYSTEM = {
    "role": "system",
    "content": (
        "You are DarkFury — precise and honest. "
        "Use sources if provided. Never invent citations."
    )
}

# ================= SEARCH =================
def web_search(query):
    try:
        res = tavily.search(query=query, max_results=4)
        return res.get("results", [])
    except Exception:
        return []

def confidence_score(srcs):
    if not srcs:
        return 30
    return min(90, 40 + len(srcs) * 15)

# ================= SOURCES UI =================
def render_sources(sources):
    html = ["<div class='xo-sources'>"]
    for s in sources:
        url = s["url"]
        title = s["title"]
        domain = url.split("/")[2]
        clearbit = f"https://logo.clearbit.com/{domain}"
        favicon = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"

        html.append(
            f"""
            <a class="xo-source-pill" href="{url}" target="_blank">
                <img src="{clearbit}" onerror="this.src='{favicon}'">
                {title}
            </a>
            """
        )
    html.append("</div>")
    st.markdown("".join(html), unsafe_allow_html=True)

# ================= CHAT RENDER =================
def render_chat():
    for m in st.session_state.messages:
        role = m["role"]
        st.markdown(
            f"<div class='xo-msg-row {role}'>"
            f"<div class='xo-msg-bubble {role}'>"
            f"<div class='xo-msg-label'>{'You' if role=='user' else 'DarkFury'}</div>"
            f"{m['content']}</div></div>",
            unsafe_allow_html=True
        )

        if role == "assistant" and m.get("sources"):
            st.markdown(f"**Confidence:** {m['confidence']}%")
            render_sources(m["sources"])

render_chat()

# ================= INPUT =================
prompt = st.chat_input("Ask anything…")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    sources = web_search(prompt)
    conf = confidence_score(sources)

    context = "\n".join(f"- {s['title']}" for s in sources)

    reply_text = ""
    placeholder = st.empty()

    # ---- TRY STREAMING ----
    try:
        stream = groq.chat.completions.create(
            model=MODEL,
            messages=[
                SYSTEM,
                {"role": "system", "content": f"SOURCES:\n{context}"},
                *st.session_state.messages
            ],
            stream=True,
            max_tokens=500,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            reply_text += delta
            placeholder.markdown(
                f"<div class='xo-msg-row assistant'>"
                f"<div class='xo-msg-bubble assistant'>"
                f"<div class='xo-msg-label'>DarkFury</div>"
                f"{reply_text}</div></div>",
                unsafe_allow_html=True
            )

    # ---- FALLBACK (NO CRASH) ----
    except Exception:
        resp = groq.chat.completions.create(
            model=MODEL,
            messages=[
                SYSTEM,
                {"role": "system", "content": f"SOURCES:\n{context}"},
                *st.session_state.messages
            ],
            max_tokens=500,
        )
        reply_text = resp.choices[0].message.content

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply_text,
        "sources": sources,
        "confidence": conf
    })

    st.rerun()
