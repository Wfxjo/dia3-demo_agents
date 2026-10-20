import streamlit as st
from llm_agent import ConversationAgent


class ChatApp:
    WHISPER_MODEL = "whisper-large-v3-turbo"


    def __init__(self):
        st.set_page_config(page_title="Jarvis")
        st.title("Barbe-Quasar")

        if "agent" not in st.session_state:
            st.session_state.agent = ConversationAgent()

        self.agent = st.session_state.agent


    def transcribe_audio(self, audio_file):
        """Transcribe an audio file to text with Groq's Whisper model."""
        return self.agent.groq_client.audio.transcriptions.create(
            file=("audio.wav", audio_file.read()),
            model=self.WHISPER_MODEL,
            response_format="text",
        )


    def display_messages(self):
        for message in self.agent.conversation_history[1:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    def run(self):
        user_input = st.chat_input(
            "Que veux tu moussaillon ?",
            accept_file=True,
            accept_audio=True,
        )

        if user_input:
            question = user_input_text

            if user_input_audio:
                try:
                    question = self.transcribe_audio(user_input_audio)
                except Exception as error:
                    st.error(f"Erreur de transcription : {error}")
                    question = None

            if question:
                self.agent.ask_llm(question)

        self.display_messages()

        if user_upload_file:
            try:
                question = self.read_file(user_upload_file)




ChatApp().run()