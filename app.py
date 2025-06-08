import streamlit as st
import os
import json
import random
from uuid import uuid4

# Load intents JSON safely
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, 'stride.json')

with open(json_path, 'r') as file:
    data = json.load(file)
intents = data['intents']

# Flatten all questions from all intents for selection
all_questions = []
question_to_intent = {}
for intent in intents:
    for question in intent['text']:
        all_questions.append(question)
        question_to_intent[question] = intent  # map question to its intent

def get_response_from_question(question):
    intent = question_to_intent.get(question)
    if intent:
        return random.choice(intent['responses'])
    return "I'm sorry, I didn't understand that."

# Initialize sessions storage
if "chat_sessions" not in st.session_state:
    st.session_state.chat_sessions = {}

if "current_session" not in st.session_state:
    new_id = str(uuid4())
    st.session_state.chat_sessions[new_id] = ["Chatbot: Hello! How can I assist you today?"]
    st.session_state.current_session = new_id

# Sidebar UI with navigation
st.sidebar.title("Stride Sync")

page = st.sidebar.radio("Navigate", ["Chatbot", "About Stride Sync"])

if page == "About Stride Sync":
    st.title("About Stride Sync")

    st.markdown("""
    **Welcome to Stride Sync**, your personalized gym trainer and fitness companion! Our mission is to help you reach your fitness goals by offering you a comprehensive platform to track your workouts, food intake, and more.

    ### Our Vision
    We believe that fitness should be accessible to everyone. That's why Stride Sync was designed to offer users a personalized fitness plan based on their unique needs, tracking workouts, food, and other health metrics in one place. Whether you're a beginner or an experienced gym-goer, we have something for you!

    ### What We Offer
    - **Exercise Tracking:** Record your workouts and keep track of progress.
    - **Food Tracking:** Monitor your food intake and maintain a balanced diet.
    - **Personalized Fitness Plan:** Get tailored plans based on your goals and preferences.
    - **BMI Calculator:** Easily calculate and monitor your Body Mass Index (BMI).
    - **Workout Logs:** Keep a log of all your workouts for better progress tracking.

    ### Why Stride Sync?
    Stride Sync is more than just an app—it's a full fitness companion that adapts to your needs. With detailed logs, progress tracking, and personalized advice, Stride Sync ensures you're always moving in the right direction, no matter your starting point.

    ### Get Started
    Ready to take the first step towards your fitness journey? Start chatting now!
    """)

elif page == "Chatbot":
    # Sidebar chat session management buttons
    st.sidebar.title("💬 Chat Sessions")

    def create_new_session():
        new_id = str(uuid4())
        st.session_state.chat_sessions[new_id] = ["Chatbot: Hello! How can I assist you today?"]
        st.session_state.current_session = new_id

    if st.sidebar.button("➕ New Chat"):
        create_new_session()

    if st.sidebar.button("🗑️ Clear All Chats"):
        st.session_state.chat_sessions = {}
        create_new_session()

    # List all chat sessions in sidebar with numbering & highlight current
    for idx, session_id in enumerate(list(st.session_state.chat_sessions.keys()), start=1):
        session_label = f"Chat #{idx}"
        if session_id == st.session_state.current_session:
            session_label = f"➡️ {session_label}"
        if st.sidebar.button(session_label, key=session_id):
            st.session_state.current_session = session_id

    st.title("🤖 FitBuddy")

    # Current chat history
    chat_history = st.session_state.chat_sessions[st.session_state.current_session]

    st.markdown("### Chat History")
    st.markdown("---")

    # Function to display chat nicely with copy buttons, answer background black & white text
    def display_chat(chat_history):
        for message in chat_history:
            if isinstance(message, dict):
                question = message['question']
                answer = message['answer']

                st.markdown(f"**You:** {question}")
                st.markdown(
                    f"""
                    <div style="
                        background-color: black; 
                        color: white; 
                        padding: 10px; 
                        border-radius: 8px; 
                        margin-bottom: 8px; 
                        position: relative;
                        font-family: monospace;
                    ">
                        {answer}
                        <button 
                            style="
                                position: absolute; 
                                right: 10px; 
                                top: 10px; 
                                cursor: pointer;
                                background: transparent;
                                border: none;
                                color: white;
                                font-size: 16px;
                            " 
                            onclick="navigator.clipboard.writeText(`{answer}`)">
                            📋 Copy
                        </button>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("---")
            else:
                # Plain chatbot intro message or others
                st.markdown(f"_{message}_")

    display_chat(chat_history)

    # User selects a question
    selected_question = st.selectbox("Choose a question to ask:", all_questions)

    # Use a form for sending questions
    with st.form(key="chat_form"):
        send_button = st.form_submit_button("Send")

    if send_button and selected_question:
        answer = get_response_from_question(selected_question)
        st.session_state.chat_sessions[st.session_state.current_session].append({
            "question": selected_question,
            "answer": answer
        })

    # Clear current chat button (separate from Clear All)
    if st.button("🧹 Clear Current Chat"):
        st.session_state.chat_sessions[st.session_state.current_session] = ["Chatbot: Hello! How can I assist you today?"]

    # Share chat button outputs full chat text to copy/share
    if st.button("📤 Share Current Chat"):
        share_text = ""
        for message in chat_history:
            if isinstance(message, dict):
                share_text += f"Q: {message['question']}\nA: {message['answer']}\n\n"
            else:
                share_text += f"{message}\n\n"
        st.text_area("Copy and share your chat below:", share_text, height=300)
