import streamlit
from llm_agent import ConversationAgent


class ChatApp:
    WHISPER_MODEL = "whisper-large-v3"
    FILE_TYPES = ["txt", "md", "py", "csv"]


    def __init__(self):
        streamlit.set_page_config(page_title="Jarvis")
        streamlit.title("Barbe-Quasar")

        if "agent" not in streamlit.session_state:
            streamlit.session_state.agent = ConversationAgent()
            streamlit.session_state.displayed_messages = []

        self.agent = streamlit.session_state.agent
        self.displayed_messages = streamlit.session_state.displayed_messages


    def transcribe_audio(self, audio_file):
        return self.agent.groq_client.audio.transcriptions.create(
            file=("audio.wav", audio_file.read()),
            model=self.WHISPER_MODEL,
            temperature=0,
            response_format="text",
        )


    def read_file(self, uploaded_file):
        return uploaded_file.read().decode("utf-8")


    def build_question(self, user_input):
        question = [user_input.text] if user_input.text else []
        displayed_text = list(question)

        if user_input.audio:
            transcription = self.transcribe_audio(user_input.audio)
            question.append(transcription)
            displayed_text.append(transcription)

        for uploaded_file in user_input.files:
            file_content = self.read_file(uploaded_file)
            question.append(uploaded_file.name + " :\n" + file_content)
            displayed_text.append("📎 " + uploaded_file.name)

        return "\n\n".join(question), "\n\n".join(displayed_text)


    def display_messages(self):
        for message in self.displayed_messages:
            with streamlit.chat_message(message["role"]):
                streamlit.markdown(message["content"])


    def run(self):
        user_input = streamlit.chat_input(
            "Que veux tu moussaillon ?",
            accept_file=True,
            file_type=self.FILE_TYPES,
            accept_audio=True,
        )

        if user_input:
            question, displayed_text = self.build_question(user_input)

            if question:
                self.agent.ask_llm(question)
                answer = self.agent.conversation_history[-1]["content"]

                self.displayed_messages.append({"role": "user", "content": displayed_text})
                self.displayed_messages.append({"role": "assistant", "content": answer})

        self.display_messages()


ChatApp().run()