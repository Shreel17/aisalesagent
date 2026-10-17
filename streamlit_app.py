
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Sales Qualification Agent",
    layout="centered",
)

st.title("AI Sales Qualification Agent")
st.write(
    "Tell us about your business needs. "
    "Our assistant will help understand your requirements."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Describe your requirements...")

if prompt:
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    history = st.session_state.messages[:-1]

    try:
        with st.chat_message("assistant"):
            with st.spinner("Understanding your requirements..."):
                response = requests.post(
                    f"{API_URL}/chat",
                    json={
                        "message": prompt,
                        "history": history,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                answer = response.json()["reply"]

            st.markdown(answer)

        st.session_state.messages.append(
            {"role": "assistant", "content": answer}
        )

    except requests.RequestException:
        st.error(
            "Could not connect to the AI agent. "
            "Please make sure the FastAPI server is running."
        )
