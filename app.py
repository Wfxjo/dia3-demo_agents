import json
import uuid
from pathlib import Path

import streamlit as st
from llm_agent import ConversationAgent


class ConversationStorage:
    def __init__(self, history_path="chat_history.json"):
        self.history_path = Path(history_path)


    def load_conversations(self):
        """Return all valid saved conversations, most recent first."""
        if not self.history_path.exists():
            return []
        conversations = json.loads(
            self.history_path.read_text(encoding="utf-8")
        )
        return [
            conversation
            for conversation in conversations
            if "id" in conversation and "title" in conversation
        ]


    def save_conversation(self, conversation_id, title, messages):
        """Save a conversation at the top of the history file."""
        conversations = [
            conversation
            for conversation in self.load_conversations()
            if conversation["id"] != conversation_id
        ]
        conversations.insert(
            0,
            {
                "id": conversation_id,
                "title": title,
                "messages": messages,
            },
        )
        self.history_path.write_text(
            json.dumps(conversations, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


class ChatApp:
    TITLE_INSTRUCTION = (
        "Génère un titre très court (4 mots maximum) qui résume le thème "
        "de la question. Réponds uniquement par le titre, sans guillemets "
        "ni ponctuation finale."
    )


    def __init__(self):
        st.set_page_config(page_title="Jarvis")
        st.title("Barbe-Quasar")

        self.storage = ConversationStorage()

        # Streamlit relance le script à chaque message :
        # l'agent doit donc être gardé dans session_state
        if "agent" not in st.session_state:
            st.session_state.agent = ConversationAgent()
            st.session_state.conversation_id = None
            st.session_state.title = None

        self.agent = st.session_state.agent


    def get_messages(self):
        """Return the conversation without the system prompt."""
        return self.agent.conversation_history[1:]


    def set_messages(self, messages):
        """Keep the system prompt and replace the rest of the history."""
        system_message = self.agent.conversation_history[0]
        self.agent.conversation_history = [system_message] + messages


    def generate_title(self, question):
        response = self.agent.groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": self.TITLE_INSTRUCTION},
                {"role": "user", "content": question},
            ],
            model="openai/gpt-oss-120b",
            include_reasoning=False,
        ).choices[0].message.content

        return response.strip().strip('"')


    def start_new_conversation(self):
        self.set_messages([])
        st.session_state.conversation_id = None
        st.session_state.title = None


    def open_conversation(self, conversation):
        self.set_messages(conversation["messages"])
        st.session_state.conversation_id = conversation["id"]
        st.session_state.title = conversation["title"]


    def handle_user_input(self, user_input):
        self.agent.ask_llm(user_input)

        # Nouvelle conversation : on crée son identifiant et son titre
        if st.session_state.conversation_id is None:
            st.session_state.conversation_id = str(uuid.uuid4())
            st.session_state.title = self.generate_title(user_input)

        self.storage.save_conversation(
            st.session_state.conversation_id,
            st.session_state.title,
            self.get_messages(),
        )


    def display_messages(self):
        for message in self.get_messages():
            with st.chat_message(message["role"]):
                st.markdown(message["content"])


    def display_sidebar(self):
        with st.sidebar:
            st.button(
                "Nouvelle conversation",
                on_click=self.start_new_conversation,
                use_container_width=True,
            )
            st.divider()
            st.markdown("Historique")

            conversations = self.storage.load_conversations()

            if not conversations:
                st.info("Pas d'historique.")
            else:
                for conversation in conversations:
                    st.button(
                        conversation["title"],
                        key=conversation["id"],
                        on_click=self.open_conversation,
                        args=(conversation,),
                        use_container_width=True,
                    )


    def run(self):
        user_input = st.chat_input(
            "Que veux tu moussaillon ?",
            accept_file=False,
            accept_audio=False,
        )

        if user_input:
            self.handle_user_input(user_input)

        self.display_messages()
        self.display_sidebar()


ChatApp().run()