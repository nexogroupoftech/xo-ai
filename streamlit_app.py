import streamlit as st
from groq import Groq

st.set_page_config(
    page_title="XO AI",
    page_icon="🤖",
    layout="wide"
)

# ---- Groq Client ----
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
MODEL_NAME = "llama-3.1-8b-instant"

SYSTEM_PROMPT = """
You are XO AI: calm, clear, helpful, professional.
Respond with accuracy. Keep answers short unless user asks otherwise.
Understand user emotions and reply respectfully.
"""

# ---- State ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- Title ----
st.markdown(
    "<h1 style='text-align:center; color:white; margin-top:20px;'>XO AI</h1>",
    unsafe_allow_html=True
)

st.markdown("---")

# ---- Chat Window ----
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        role = "You" if msg["role"] == "user" else "XO AI"
        bubble_color = "#1f1f1f" if msg["role"] == "user" else "#2c2c2c"

        st.markdown(
            f"""
            <div style="
                background:{bubble_color};
                padding:12px 18px;
                border-radius:12px;
                margin:10px 0;
                width:fit-content;
                max-width:80%;
            ">
                <b>{role}:</b><br>{msg["content"]}
            </div>
            """,
            unsafe_allow_html=True
        )

# ---- Input Bar ----
st.markdown("<br>", unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    user_input = st.text_input("Ask XO AI anything...", "")
    submit = st.form_submit_button("Send")

if submit and user_input.strip():
    st.session_state.messages.append({"role": "user", "content": user_input})

    msgs = [{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=msgs
    )

    answer = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": answer})

    st.experimental_rerun()

