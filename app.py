import streamlit as st
from llm_agent import ConversationAgent


class ChatApp:
    WHISPER_MODEL = "whisper-large-v3-turbo"
    ALLOWED_FILE_TYPES = ["txt", "md", "py", "csv"]


    def __init__(self):
        st.set_page_config(page_title="Jarvis")
        st.title("Barbe-Quasar")

        if "agent" not in st.session_state:
            st.session_state.agent = ConversationAgent()

        self.agent = st.session_state.agent


    def transcribe_audio(self, audio_file):
        return self.agent.groq_client.audio.transcriptions.create(
            file=("audio.wav", audio_file.read()),
            model=self.WHISPER_MODEL,
            response_format="text",
        )


    def read_uploaded_file(self, uploaded_file):
        return uploaded_file.read().decode("utf-8")


    def combine_inputs_into_text(self, user_input):
        question_parts = []

        if user_input_text:
            question_parts.append(user_input_text)

        if user_input.audio:
            try:
                question_parts.append(self.transcribe_audio(user_input.audio))
            except Exception as error:
                st.error(f"Erreur de transcription : {error}")

        for uploaded_file in user_input.files:
            try:
                file_content = self.read_uploaded_file(uploaded_file)
                question_parts.append(
                    f"Contenu du fichier {uploaded_file.name} :\n"
                    f"{file_content}"
                )
            except Exception as error:
                st.error(f"Erreur de lecture du fichier : {error}")

        return "\n\n".join(question_parts)


    def display_messages(self):
        for message in self.agent.conversation_history[1:]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    def run(self):
        user_input = st.chat_input(
            "Que veux tu moussaillon ?",
            accept_file=True,
            file_type=self.ALLOWED_FILE_TYPES,
            accept_audio=True,
        )

        if user_input:
            question = self.build_question(user_input)