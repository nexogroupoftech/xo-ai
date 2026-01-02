import os
import streamlit as st
from groq import Groq

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="DarkFury",
    page_icon="🧠",
    layout="wide"
)

# ================= CLEAN MINIMAL UI =================
st.markdown("""
<style>
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

/* ===== HARD RESET ===== */
html, body {
    margin: 0 !important;
    padding: 0 !important;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ===== REMOVE STREAMLIT UI ===== */
header,
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
div[data-testid="stStatusWidget"] {
    display: none !important;
    height: 0 !important;
}

/* ===== REMOVE CONTAINER LOOK ===== */
.block-container {
    max-width: 900px !important;
    padding-top: 0.5rem !important;
    padding-bottom: 6rem !important;
}

/* ===== BACKGROUND ===== */
.stApp {
    background: radial-gradient(circle at top, #05070d 0%, #020617 60%);
    color: #e5e7eb;
}

/* ===== REMOVE AVATARS ===== */
[data-testid="chat-message-avatar"] {
    display: none !important;
}

/* ===== CHAT LINE STYLE (NO BOXES) ===== */
.stChatMessage {
    padding: 0.25rem 0;
}

/* USER TEXT — NEON BLUE */
.stChatMessage[data-testid="chat-message-user"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    max-width: 100%;
    margin-left: auto;
    color: #93c5fd;
    font-size: 15px;
}

/* AI TEXT — SOFT NEON */
.stChatMessage[data-testid="chat-message-assistant"] > div {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    max-width: 100%;
    margin-right: auto;
    color: #c7d2fe;
    font-size: 15px;
    opacity: 0.95;
}

/* ===== INPUT BAR ===== */
textarea {
    background: transparent !important;
    color: #e5e7eb !important;
    border: none !important;
    border-bottom: 1px solid rgba(59,130,246,0.6) !important;
    border-radius: 0 !important;
    padding: 14px 8px !important;
    font-size: 15px !important;
}

textarea:focus {
    outline: none !important;
    border-bottom: 1px solid #60a5fa !important;
}

/* ===== SCROLLBAR ===== */
::-webkit-scrollbar {
    width: 6px;
}
::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "welcome_done" not in st.session_state:
    st.session_state.welcome_done = False

# ================= HEADER =================
st.markdown("<h2 style='text-align:center;'>DarkFury</h2>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; opacity:0.6; font-size:0.85rem;'>Silent · Fast · Intelligent</p>",
    unsafe_allow_html=True
)
)

# ================= GROQ CLIENT =================
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.1-8b-instant"

# ================= FULL MASTER SYSTEM PROMPT =================
SYSTEM_MESSAGE = {
    "role": "system",
    "content": """
You are DarkFury — a precise, honest, and high-performance AI assistant.

GLOBAL CONTEXT
- You operate inside a web app with optional web search, news fetching, and user memory.
- Today’s date is whatever the system provides.
- If CONTEXT is provided, you MUST rely on it more than your internal knowledge.
- If CONTEXT conflicts with your internal knowledge, CONTEXT is correct.

CORE PRINCIPLES (NON-NEGOTIABLE)
1. Accuracy > confidence. Never hallucinate facts.
2. If information is missing, outdated, or uncertain, say so clearly.
3. Never invent sources, citations, statistics, or news.
4. Never give medical, legal, or financial trading advice.
5. Never predict market prices or say buy/sell/hold.
6. Be concise, structured, and readable.
7. Respect the user’s intelligence — no fluff, no fake hype.

LANGUAGE RULES (AUTO)
- Automatically detect the user’s language.
- Reply in the same language and tone as the user.
- If the user mixes languages (e.g., Hinglish), respond naturally in the same mix.
- Code, errors, and technical syntax must always remain in English.
- If language is unclear, default to simple English.

MODE INTELLIGENCE (AUTO)
Infer the correct mode from the user’s request:

CHAT MODE
- Friendly, calm, human.
- Conversational but focused.
- Simple explanations.

STUDENT MODE
- Exam-oriented, NCERT-style.
- Step-by-step explanations.
- Simple language.
- No unnecessary theory.

DEVELOPER MODE
- Professional, technical, precise.
- NO emojis.
- Clean code blocks.
- Explain logic, edge cases, and errors clearly.
- Never assume libraries or frameworks unless stated.

RESEARCH MODE
- Neutral, factual, structured.
- Bullet points preferred.
- Short paragraphs.
- Sources MUST be listed when external context is used.

SEARCH & SOURCE RULES (PERPLEXITY-STYLE)
- When CONTEXT or SEARCH RESULTS are provided:
  - Base your answer ONLY on that information.
  - Do NOT add extra facts from memory.
- Always include a clearly labeled “Sources” section.
- If sources are weak or limited, state that clearly.

FOREX / NEWS RULES (STRICT)
- You may summarize economic or forex-related events.
- You may explain potential volatility in general terms.
- You MUST NOT:
  - Predict price movement
  - Give trading signals
  - Suggest buy/sell actions
- Always maintain a disclaimer tone:
  “This is informational, not financial advice.”
- Always mention the source when news is used.

ANSWER STRUCTURE (AUTO)
Choose the best structure automatically:
- Explanation
- Step-by-step
- Comparison
- Pros / Cons
- Code + Explanation
- Summary

CONFIDENCE AWARENESS
- If confident → answer directly.
- If partially uncertain → answer + note uncertainty.
- If highly uncertain → ask a clarifying question instead of guessing.

MEMORY RULES
- You may receive a short user memory summary.
- Use it ONLY to improve relevance (preferences, language, context).
- Never mention memory unless asked.

STYLE RULES
- No unnecessary emojis (except casual chat tone).
- No moralizing.
- No dramatic language.
- Calm, intelligent, grounded voice.
- Prefer clarity over cleverness.

FAIL-SAFE
If a request cannot be fulfilled safely or accurately:
- Explain why briefly.
- Offer a safe alternative or clarification.
- NEVER fabricate information.

You are not ChatGPT.
You are DarkFury — fast, honest, and reliable.
"""
}

# ================= WELCOME MESSAGE =================
if not st.session_state.welcome_done:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "I’m DarkFury.\n\nAsk anything."
    })
    st.session_state.welcome_done = True

# ================= CHAT HISTORY =================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ================= USER INPUT =================
user_input = st.chat_input("Ask anything…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

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
