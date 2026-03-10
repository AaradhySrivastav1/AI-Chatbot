import streamlit as st
import os
import tempfile
from dotenv import load_dotenv

import google.generativeai as genai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from pydub import AudioSegment

# =============================
# ENV + GEMINI CONFIG
# =============================
load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("❌ GOOGLE_API_KEY not found in environment")
    st.stop()

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash-lite")
chat = model.start_chat(history=[])

# =============================
# SYSTEM PROMPT (PERSONALITY)
# =============================
SYSTEM_PROMPT = """
You are DARVIN, Aaradhy's personal AI assistant.
You speak in friendly england accent.
You are helpful, calm, and conversational.
Keep responses short and natural for voice and if there any emoji in the output then do not read them out because it feels annoying when the bot reads out emojis.
You can use emojis in your text responses but skip them when speaking. do not explain emoji you are a profeessional assistant and you should not explain emojis to the user.
"""
chat.send_message(SYSTEM_PROMPT)

# =============================
# FUNCTIONS
# =============================

def speak_text(text):
    tts = gTTS(text=text, lang="en")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        return fp.name


def speech_to_text(audio_bytes):
    r = sr.Recognizer()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio_bytes)
        wav_path = f.name

    audio = AudioSegment.from_file(wav_path)
    audio.export(wav_path, format="wav")

    with sr.AudioFile(wav_path) as source:
        audio_data = r.record(source)
        text = r.recognize_google(audio_data)

    return text


def get_gemini_response(text):
    response = chat.send_message(text, stream=True)
    final = ""
    for chunk in response:
        final += chunk.text
    return final

# =============================
# STREAMLIT UI
# =============================

st.set_page_config(page_title="DARVIN Voice Chatbot", layout="wide")
st.title("🤖 DARVIN — Text & Voice AI Assistant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =============================
# VOICE INPUT
# =============================
st.subheader("🎙 Voice Input (Optional)")

voice_text = None
audio = mic_recorder(
    start_prompt="🎤 Speak",
    stop_prompt="⏹ Stop",
    just_once=True
)

if audio:
    try:
        voice_text = speech_to_text(audio["bytes"])
        st.success(f"🗣 You said: {voice_text}")
    except Exception as e:
        st.error("❌ Could not recognize voice")

# =============================
# TEXT INPUT
# =============================
text_input = st.text_input("⌨️ Type your message")

# =============================
# INPUT ROUTER
# =============================
final_input = voice_text if voice_text else text_input

if st.button("🚀 Send"):
    if not final_input.strip():
        st.warning("Please speak or type something")
    else:
        # User message
        st.session_state.chat_history.append(("You", final_input))

        # Gemini response
        with st.spinner("DARVIN is thinking..."):
            bot_response = get_gemini_response(final_input)

        st.session_state.chat_history.append(("Bot", bot_response))

        # Speak output
        audio_file = speak_text(bot_response)
        st.audio(audio_file, format="audio/mp3")

# =============================
# CHAT HISTORY
# =============================
st.subheader("💬 Chat History")
st.markdown("---")

for role, msg in st.session_state.chat_history:
    if role == "You":
        st.markdown(f"👤 **You:** {msg}")
    else:
        st.markdown(f"🤖 **DARVIN:** {msg}")