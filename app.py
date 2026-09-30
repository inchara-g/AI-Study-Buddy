import smtplib
import base64
from email.mime.text import MIMEText

import streamlit as st
from google import genai
from google.genai import types

from prompts import (
    SYSTEM_PROMPT,
    WELCOME_MESSAGE_TEMPLATE,
    SUMMARY_REQUEST_PROMPT,
)


# -----------------------------
# Page settings
# -----------------------------
st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="📚",
)


# -----------------------------
# Secrets
# -----------------------------
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
GMAIL_ADDRESS = st.secrets["GMAIL_ADDRESS"]
GMAIL_APP_PASSWORD = st.secrets["GMAIL_APP_PASSWORD"]


# -----------------------------
# Gemini client
# -----------------------------
@st.cache_resource
def get_gemini_client():
    return genai.Client(api_key=GEMINI_API_KEY)


client = get_gemini_client()


# -----------------------------
# Email function
# -----------------------------
def send_email(to_address, subject, body):
    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_address

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(message)


# -----------------------------
# Gemini chat function
# -----------------------------
def ask_gemini(parts):
    import time

    for attempt in range(3):
        try:
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=parts,
                previous_interaction_id=st.session_state.get(
                    "last_interaction_id"
                ),
            )

            st.session_state.last_interaction_id = interaction.id

            return interaction.output_text

        except Exception as e:
            error_message = str(e).lower()

            if "429" in error_message or "rate limit" in error_message:
                return (
                    "Gemini's daily free-tier request limit has been reached. "
                    "Please try again after the quota resets."
                )

            elif "503" in error_message or "high demand" in error_message:
                if attempt < 2:
                    time.sleep(3)
                else:
                    return (
                        "Gemini is temporarily busy. "
                        "Please try asking again in a few seconds."
                    )

            else:
                raise

# -----------------------------
# Display previous messages
# -----------------------------
def display_message(message):
    with st.chat_message(message["role"]):
        for part in message["parts"]:
            if part["type"] == "text":
                st.markdown(part["content"])

            elif part["type"] == "image":
                st.image(
                    part["content"],
                    caption="Uploaded question",
                    use_container_width=True,
                )


# -----------------------------
# First-time setup
# -----------------------------
if "onboarded" not in st.session_state:
    st.session_state.onboarded = False

if not st.session_state.onboarded:

    st.title("📚 AI Study Buddy")
    st.write("Your simple AI assistant for studying and revision.")

    name = st.text_input("Enter your name")

    email = st.text_input("Enter your email")

    if st.button("Start Studying 🚀"):

        if not name or not email:
            st.warning("Please enter both your name and email.")

        else:
            st.session_state.name = name
            st.session_state.email = email

           
            st.session_state.last_interaction_id = None

            st.session_state.messages = [
                {
                    "role": "assistant",
                    "parts": [
                        {
                            "type": "text",
                            "content": WELCOME_MESSAGE_TEMPLATE.format(
                                name=name
                            ),
                        }
                    ],
                }
            ]

            st.session_state.onboarded = True

            st.rerun()

    st.stop()


# -----------------------------
# Main application
# -----------------------------
st.title("📚 AI Study Buddy")

st.caption(
    f"Welcome, {st.session_state.name}! "
    "Ask a question or upload a question image."
)


# -----------------------------
# Show previous messages
# -----------------------------
for message in st.session_state.messages:
    display_message(message)


# -----------------------------
# Send study summary
# -----------------------------
if st.button("📧 Send Study Summary to Email"):

    with st.spinner("Preparing your study summary..."):

        summary = ask_gemini(
            [
                {
                    "type": "text",
                    "text": SUMMARY_REQUEST_PROMPT
                }
            ]
        )

    try:

        send_email(
            st.session_state.email,
            "Your AI Study Buddy Summary",
            summary,
        )

        st.success(
            f"Study summary sent to {st.session_state.email} 📧"
        )

    except Exception as e:

        st.error(
            f"Could not send the email: {e}"
        )


# -----------------------------
# Chat input
# -----------------------------
prompt = st.chat_input(
    "Ask your study question...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png"],
)


if prompt:

    user_text = prompt.text
    uploaded_file = prompt.files[0] if prompt.files else None

    parts = []
    display_parts = []

    # Text question
    if user_text:

        parts.append({
    "type": "text",
    "text": user_text
     })

        display_parts.append(
            {
                "type": "text",
                "content": user_text,
            }
        )

    # Uploaded question image
    if uploaded_file:

        photo_bytes = uploaded_file.getvalue()

        image_part = {
            "type": "image",
            "data": base64.b64encode(photo_bytes).decode("utf-8"),
            "mime_type": uploaded_file.type,
    }

        parts.append(image_part)

        display_parts.append(
        {
            "type": "image",
            "content": photo_bytes,
        }
    )

    # Show user's message
    st.session_state.messages.append(
        {
            "role": "user",
            "parts": display_parts,
        }
    )

    for part in display_parts:

        if part["type"] == "text":

            with st.chat_message("user"):
                st.markdown(part["content"])

        elif part["type"] == "image":

            with st.chat_message("user"):
                st.image(
                    part["content"],
                    caption="Uploaded question",
                    use_container_width=True,
                )


    # Get AI response
    with st.chat_message("assistant"):

        with st.spinner("Thinking..."):

            answer = ask_gemini(parts)

        st.markdown(answer)


    # Save AI response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "parts": [
                {
                    "type": "text",
                    "content": answer,
                }
            ],
        }
    )