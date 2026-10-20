import streamlit
from llm_agent import ConversationAgent


class ChatApp:
    WHISPER_MODEL = "whisper-large-v3"


    def __init__(self):
        streamlit.set_page_config(page_title="Jarvis")
        streamlit.title("Barbe-Quasar")

        if "agent" not in streamlit.session_state:
            streamlit.session_state.agent = ConversationAgent()

        self.agent = streamlit.session_state.agent


    def transcribe_audio(self, audio_file):
        return self.agent.groq_client.audio.transcriptions.create(
            file=("audio.wav", audio_file.read()),
            model=self.WHISPER_MODEL,
            temperature=0,
            response_format="text",
        )


    def build_question(self, user_input):
        if user_input.audio:
            return self.transcribe_audio(user_input.audio)
        return user_input.text


    def display_messages(self):
        for message in self.agent.conversation_history[1:]:
            with streamlit.chat_message(message["role"]):
                streamlit.markdown(message["content"])


    def run(self):
        user_input = streamlit.chat_input(
            "Que veux tu moussaillon ?",
            accept_file=False,
            accept_audio=True,
        )

        if user_input:
            question = self.build_question(user_input)

            if question:
                self.agent.ask_llm(question)

        self.display_messages()


ChatApp().run()