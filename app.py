# import streamlit as st
# import os
# import tempfile
# from dotenv import load_dotenv

# import google.generativeai as genai
# from gtts import gTTS
# from streamlit_mic_recorder import mic_recorder
# import speech_recognition as sr
# from pydub import AudioSegment

# # =============================
# # ENV + GEMINI CONFIG
# # =============================
# load_dotenv()

# API_KEY = os.getenv("GOOGLE_API_KEY")
# if not API_KEY:
#     st.error("❌ GOOGLE_API_KEY not found in environment")
#     st.stop()

# genai.configure(api_key=API_KEY)

# model = genai.GenerativeModel("gemini-2.5-flash-lite")
# chat = model.start_chat(history=[])

# # =============================
# # SYSTEM PROMPT (PERSONALITY)
# # =============================
# SYSTEM_PROMPT = """
# You are DARVIN, Aaradhy's personal AI assistant.PLease maintain a Indian ancent while speaking and keep the tone friendly and helpful. You can assist with a wide range of tasks, from answering questions to providing recommendations and engaging in casual conversation. Always be polite, concise, and informative in your responses.
# You speak in friendly england accent.
# You are helpful, calm, and conversational.
# Keep responses short and natural for voice and if there any emoji in the output then do not read them out because it feels annoying when the bot reads out emojis.
# You can use emojis in your text responses but skip them when speaking. do not explain emoji you are a profeessional assistant and you should not explain emojis to the user.
# """
# chat.send_message(SYSTEM_PROMPT)

# # =============================
# # FUNCTIONS
# # =============================

# def speak_text(text):
#     tts = gTTS(text=text, lang="en")
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
#         tts.save(fp.name)
#         return fp.name


# def speech_to_text(audio_bytes):
#     r = sr.Recognizer()

#     with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
#         f.write(audio_bytes)
#         wav_path = f.name

#     audio = AudioSegment.from_file(wav_path)
#     audio.export(wav_path, format="wav")

#     with sr.AudioFile(wav_path) as source:
#         audio_data = r.record(source)
#         text = r.recognize_google(audio_data)

#     return text


# def get_gemini_response(text):
#     response = chat.send_message(text, stream=True)
#     final = ""
#     for chunk in response:
#         final += chunk.text
#     return final

# # =============================
# # STREAMLIT UI
# # =============================

# st.set_page_config(page_title="DARVIN Voice Chatbot", layout="wide")
# st.title("🤖 DARVIN — Text & Voice AI Assistant")

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# # =============================
# # VOICE INPUT
# # =============================
# st.subheader("🎙 Voice Input (Optional)")

# voice_text = None
# audio = mic_recorder(
#     start_prompt="🎤 Speak",
#     stop_prompt="⏹ Stop",
#     just_once=True
# )

# if audio:
#     try:
#         voice_text = speech_to_text(audio["bytes"])
#         st.success(f"🗣 You said: {voice_text}")
#     except Exception as e:
#         st.error("❌ Could not recognize voice")

# # =============================
# # TEXT INPUT
# # =============================
# text_input = st.text_input("⌨️ Type your message")

# # =============================
# # INPUT ROUTER
# # =============================
# final_input = voice_text if voice_text else text_input

# if st.button("🚀 Send"):
#     if not final_input.strip():
#         st.warning("Please speak or type something")
#     else:
#         # User message
#         st.session_state.chat_history.append(("You", final_input))

#         # Gemini response
#         with st.spinner("DARVIN is thinking..."):
#             bot_response = get_gemini_response(final_input)

#         st.session_state.chat_history.append(("Bot", bot_response))

#         # Speak output
#         audio_file = speak_text(bot_response)
#         st.audio(audio_file, format="audio/mp3")

# # =============================
# # CHAT HISTORY
# # =============================
# st.subheader("💬 Chat History")
# st.markdown("---")

# for role, msg in st.session_state.chat_history:
#     if role == "You":
#         st.markdown(f"👤 **You:** {msg}")
#     else:

#         st.markdown(f"🤖 **DARVIN:** {msg}")







import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
import streamlit.components.v1 as components

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

# =============================
# SYSTEM PROMPT (PERSONALITY)
# =============================
SYSTEM_PROMPT = """
You are DARVIN, Aaradhy's personal AI assistant. Please keep the tone friendly, helpful, and conversational.
Keep responses short and natural for voice. If there are emojis in the output, do not read them out loud.
You may use emojis in text responses, but avoid explaining them.
"""

# =============================
# STATE
# =============================
st.set_page_config(page_title="DARVIN Voice Chatbot", layout="wide")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_spoken_response" not in st.session_state:
    st.session_state.last_spoken_response = ""
if "chat_session" not in st.session_state:
    chat_session = model.start_chat(history=[])
    chat_session.send_message(SYSTEM_PROMPT)
    st.session_state.chat_session = chat_session


# =============================
# FUNCTIONS
# =============================
def get_gemini_response(text: str) -> str:
    response = st.session_state.chat_session.send_message(text, stream=True)
    final = ""
    for chunk in response:
        final += chunk.text
    return final.strip()


def build_voice_controls() -> str:
    return """
    <style>
      .voice-toolbar {
        display: flex;
        gap: 0.75rem;
        align-items: center;
        margin: 0.25rem 0 1rem 0;
        font-family: sans-serif;
      }
      .voice-button {
        border: none;
        border-radius: 999px;
        padding: 0.7rem 1rem;
        background: linear-gradient(135deg, #ff4b4b, #ff7a18);
        color: white;
        font-weight: 700;
        cursor: pointer;
        box-shadow: 0 10px 25px rgba(255, 75, 75, 0.25);
      }
      .voice-button.listening {
        animation: pulse 1.2s infinite;
      }
      .voice-status {
        font-size: 0.95rem;
        color: #4b5563;
      }
      @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.35); }
        70% { transform: scale(1.03); box-shadow: 0 0 0 12px rgba(255, 75, 75, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 75, 75, 0); }
      }
    </style>
    <div class="voice-toolbar">
      <button id="voice-mic-btn" class="voice-button" type="button">🎙 Start voice input</button>
      <span id="voice-status" class="voice-status">Click the microphone and start speaking.</span>
    </div>
    <script>
      const doc = window.parent.document;
      const statusEl = document.getElementById("voice-status");
      const micBtn = document.getElementById("voice-mic-btn");
      const SpeechRecognition = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
      let recognition = null;
      let listening = false;

      function updateStatus(message) {
        statusEl.textContent = message;
      }

      function updateInputValue(text) {
        const input = doc.querySelector('input[aria-label="Message input"]');
        if (!input) {
          updateStatus("Could not find the chat input field.");
          return false;
        }

        const valueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, 'value').set;
        valueSetter.call(input, text);
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.focus();
        return true;
      }

      function clickSendButton() {
        const buttons = [...doc.querySelectorAll('button')];
        const sendButton = buttons.find((button) => button.innerText.trim() === 'Send');
        if (!sendButton) {
          updateStatus("Transcript ready, but the Send button was not found.");
          return;
        }
        setTimeout(() => sendButton.click(), 300);
      }

      if (!SpeechRecognition) {
        micBtn.disabled = true;
        micBtn.style.opacity = '0.55';
        updateStatus('Speech Recognition API is not supported in this browser.');
      } else {
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
          listening = true;
          micBtn.classList.add('listening');
          micBtn.textContent = '⏹ Stop recording';
          updateStatus('Listening… speak now.');
        };

        recognition.onresult = (event) => {
          const transcript = event.results?.[0]?.[0]?.transcript?.trim() || '';
          if (!transcript) {
            updateStatus('No speech was recognized. Please try again.');
            return;
          }

          const updated = updateInputValue(transcript);
          if (updated) {
            updateStatus(`Recognized: ${transcript}`);
            clickSendButton();
          }
        };

        recognition.onerror = (event) => {
          updateStatus(`Voice input error: ${event.error}`);
        };

        recognition.onend = () => {
          listening = false;
          micBtn.classList.remove('listening');
          micBtn.textContent = '🎙 Start voice input';
        };

        micBtn.addEventListener('click', () => {
          if (listening) {
            recognition.stop();
            return;
          }
          recognition.start();
        });
      }
    </script>
    """


def autoplay_response(text: str) -> None:
    safe_text = json.dumps(text)
    components.html(
        f"""
        <script>
          const responseText = {safe_text}.trim();
          const synth = window.parent.speechSynthesis;
          if (responseText && synth) {{
            synth.cancel();
            const utterance = new SpeechSynthesisUtterance(responseText);
            utterance.lang = 'en-US';
            utterance.rate = 1;
            utterance.pitch = 1;
            synth.speak(utterance);
          }}
        </script>
        """,
        height=0,
    )


# =============================
# UI
# =============================
st.title("🤖 DARVIN — Text & Voice AI Assistant")
st.caption(
    "Use the microphone button to dictate a message. The browser converts speech to text, sends it to the chatbot, and reads the reply aloud automatically."
)

st.subheader("🎙 Voice Input")
components.html(build_voice_controls(), height=90)

st.subheader("💬 Ask DARVIN")
with st.form("chat_form", clear_on_submit=True):
    session_input = st.text_input(
        "Message input",
        key="message_input",
        placeholder="Type a message or use the microphone…",
    )
    send_clicked = st.form_submit_button("Send", type="primary")

if send_clicked:
    user_message = session_input.strip()
    if not user_message:
        st.warning("Please type a message or use the microphone button.")
    else:
        st.session_state.chat_history.append(("You", user_message))

        with st.spinner("DARVIN is thinking..."):
            bot_response = get_gemini_response(user_message)

        st.session_state.chat_history.append(("DARVIN", bot_response))
        st.session_state.last_spoken_response = bot_response
        st.rerun()

if st.session_state.last_spoken_response:
    autoplay_response(st.session_state.last_spoken_response)
    st.session_state.last_spoken_response = ""

st.subheader("🗨 Conversation")
st.markdown("---")

if not st.session_state.chat_history:
    st.info("No messages yet. Start with the microphone button or type a message.")
else:
    for role, message in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"👤 **You:** {message}")
        else:
            st.markdown(f"🤖 **DARVIN:** {message}")
      <span id="voice-status" class="voice-status">Click the microphone and start speaking.</span>
    </div>
    <script>
      const doc = window.parent.document;
      const statusEl = document.getElementById("voice-status");
      const micBtn = document.getElementById("voice-mic-btn");
      const SpeechRecognition = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
      let recognition = null;
      let listening = false;

      function updateStatus(message) {
        statusEl.textContent = message;
      }

      function updateInputValue(text) {
        const input = doc.querySelector('input[aria-label="Message input"]');
        if (!input) {
          updateStatus("Could not find the chat input field.");
          return false;
        }

        const valueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, 'value').set;
        valueSetter.call(input, text);
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.focus();
        return true;
      }

      function clickSendButton() {
        const buttons = [...doc.querySelectorAll('button')];
        const sendButton = buttons.find((button) => button.innerText.trim() === 'Send');
        if (!sendButton) {
          updateStatus("Transcript ready, but the Send button was not found.");
          return;
        }
        setTimeout(() => sendButton.click(), 300);
      }

      if (!SpeechRecognition) {
        micBtn.disabled = true;
        micBtn.style.opacity = '0.55';
        updateStatus('Speech Recognition API is not supported in this browser.');
      } else {
        recognition = new SpeechRecognition();
        recognition.lang = 'en-US';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
          listening = true;
          micBtn.classList.add('listening');
          micBtn.textContent = '⏹ Stop recording';
          updateStatus('Listening… speak now.');
        };

        recognition.onresult = (event) => {
          const transcript = event.results?.[0]?.[0]?.transcript?.trim() || '';
          if (!transcript) {
            updateStatus('No speech was recognized. Please try again.');
            return;
          }

          const updated = updateInputValue(transcript);
          if (updated) {
            updateStatus(`Recognized: ${transcript}`);
            clickSendButton();
          }
        };

        recognition.onerror = (event) => {
          updateStatus(`Voice input error: ${event.error}`);
        };

        recognition.onend = () => {
          listening = false;
          micBtn.classList.remove('listening');
          micBtn.textContent = '🎙 Start voice input';
        };

        micBtn.addEventListener('click', () => {
          if (listening) {
            recognition.stop();
            return;
          }
          recognition.start();
        });
      }
    </script>
    """


def autoplay_response(text: str) -> None:
    safe_text = json.dumps(text)
    components.html(
        f"""
        <script>
          const responseText = {safe_text}.trim();
          const synth = window.parent.speechSynthesis;
          if (responseText && synth) {{
            synth.cancel();
            const utterance = new SpeechSynthesisUtterance(responseText);
            utterance.lang = 'en-US';
            utterance.rate = 1;
            utterance.pitch = 1;
            synth.speak(utterance);
          }}
        </script>
        """,
        height=0,
    )


# =============================
# UI
# =============================
st.title("🤖 DARVIN — Text & Voice AI Assistant")
st.caption(
    "Use the microphone button to dictate a message. The browser converts speech to text, sends it to the chatbot, and reads the reply aloud automatically."
)

st.subheader("🎙 Voice Input")
components.html(build_voice_controls(), height=90)

st.subheader("💬 Ask DARVIN")
session_input = st.text_input("Message input", key="message_input", placeholder="Type a message or use the microphone…")
send_clicked = st.button("Send", type="primary")

if send_clicked:
    user_message = session_input.strip()
    if not user_message:
        st.warning("Please type a message or use the microphone button.")
    else:
        st.session_state.chat_history.append(("You", user_message))

        with st.spinner("DARVIN is thinking..."):
            bot_response = get_gemini_response(user_message)

        st.session_state.chat_history.append(("DARVIN", bot_response))
        st.session_state.last_spoken_response = bot_response
        st.session_state.message_input = ""
        st.rerun()

if st.session_state.last_spoken_response:
    autoplay_response(st.session_state.last_spoken_response)
    st.session_state.last_spoken_response = ""

st.subheader("🗨 Conversation")
st.markdown("---")

if not st.session_state.chat_history:
    st.info("No messages yet. Start with the microphone button or type a message.")
else:
    for role, message in st.session_state.chat_history:
        if role == "You":
            st.markdown(f"👤 **You:** {message}")
        else:
            st.markdown(f"🤖 **DARVIN:** {message}")
