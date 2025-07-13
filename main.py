import streamlit as st

from classical_agent import ClassicalAgent
from database import create_user, get_user, update_user, submit_feedback_to_db, get_feedback_from_db
from database import init_db
from gen_ai_agent import GenAIAgent
from login_simulator import LoginSimulator

init_db()

st.set_page_config(page_title="Secure Login System", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stButton>button { background-color: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 5px; }
    .stButton>button:hover { background-color: #45a049; }
    .stTextInput>div>input { border-radius: 5px; border: 1px solid #ccc; padding: 10px; }
    .stSelectbox>div>div>select { border-radius: 5px; border: 1px solid #ccc; padding: 10px; }
    .stAlert { background-color: #e3f2fd; color: #0d47a1; border-radius: 5px; padding: 10px; }
    .sidebar .sidebar-content { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    .chat-message { padding: 10px; border-radius: 5px; margin: 5px 0; }
    .user-message { background-color: #e1f5fe; }
    .bot-message { background-color: #f1f1f1; }
    .loading-bubble { background-color: #f1f1f1; color: #888; padding: 10px; border-radius: 5px; margin: 5px 0; font-style: italic; }
    .header { font-size: 2.5em; color: #1e88e5; margin-bottom: 20px; }
    .subheader { font-size: 1.5em; color: #424242; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'login'
if 'username' not in st.session_state:
    st.session_state.username = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'recovery_step' not in st.session_state:
    st.session_state.recovery_step = 0
if 'chat_mode' not in st.session_state:
    st.session_state.chat_mode = None
if 'last_message' not in st.session_state:
    st.session_state.last_message = None
if 'insights_username' not in st.session_state:
    st.session_state.insights_username = None

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Login/Register", "Account Insights", "Recovery Chatbot"])
st.session_state.page = page

# Main content
st.markdown('<div class="main">', unsafe_allow_html=True)

if st.session_state.page == "Login/Register":
    st.markdown('<div class="header">Welcome to Secure Login System</div>', unsafe_allow_html=True)

    # Tabs for Login and Register
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.markdown('<div class="subheader">Login</div>', unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:
                user = get_user(username)
                if user and user[2] == password and not user[6]:
                    st.session_state.username = username
                    st.session_state.insights_username = username
                    st.success(f"Welcome back, {username}!")
                    st.session_state.page = "Account Insights"
                elif user and user[6]:
                    st.error("Account is locked. Please use the Recovery Chatbot.")
                else:
                    update_user(username, user[5] + 1 if user else 1, 1 if user and user[5] >= 2 else 0)
                    st.error("Invalid credentials or account locked.")

    with tab2:
        st.markdown('<div class="subheader">Register</div>', unsafe_allow_html=True)
        with st.form("register_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            email = st.text_input("Email")
            phone = st.text_input("Phone")
            register = st.form_submit_button("Register")

            if register:
                if create_user(new_username, new_password, email, phone):
                    st.success("Registration successful! Please log in.")
                else:
                    st.error("Username already exists.")

elif st.session_state.page == "Account Insights":
    st.markdown('<div class="header">Account Insights</div>', unsafe_allow_html=True)

    insights_username = st.text_input("Enter your username", key="insights_username_input")
    if st.button("Check Account Status"):
        if insights_username:
            st.session_state.insights_username = insights_username
        else:
            st.error("Please enter a username.")

    if st.session_state.insights_username:
        user = get_user(st.session_state.insights_username)
        if user:
            st.markdown(f'<div class="subheader">Account Status for {st.session_state.insights_username}</div>',
                        unsafe_allow_html=True)

            agent_type = st.selectbox("Select Agent for Status Explanation", ["Classical Agent", "GenAI Agent"])

            if agent_type == "Classical Agent":
                explanation = ClassicalAgent.get_classical_block_explanation(st.session_state.insights_username)
                st.markdown(f"**Classical Agent Explanation**: {explanation}")
            else:
                genai_explanation = GenAIAgent.get_genai_block_explanation(st.session_state.insights_username)
                st.markdown(f"**GenAI Agent Explanation**: {genai_explanation}")

            st.markdown('<div class="subheader">Submit Feedback</div>', unsafe_allow_html=True)
            with st.form("feedback_form"):
                rating = st.slider("Rating (1-5)", 1, 5, 3)
                comment = st.text_area("Comment")
                feedback_submit = st.form_submit_button("Submit Feedback")

                if feedback_submit:
                    submit_feedback_to_db(st.session_state.insights_username, rating, comment)
                    st.success("Feedback submitted successfully!")

            st.markdown('<div class="subheader">Previous Feedback</div>', unsafe_allow_html=True)
            feedback = get_feedback_from_db()
            if not feedback.empty:
                st.dataframe(
                    feedback[feedback['username'] == st.session_state.insights_username][['rating', 'comment']])
            else:
                st.info("No feedback available.")
        else:
            st.error("Username not found.")

elif st.session_state.page == "Recovery Chatbot":
    st.markdown('<div class="header">Account Recovery Chatbot</div>', unsafe_allow_html=True)

    # Username input
    username_input = st.text_input("Enter your username", key="chat_username")
    if st.button("Check Account"):
        if username_input:
            st.session_state.username = username_input
            user = get_user(username_input)
            if user:
                if user[6]:
                    st.session_state.chat_mode = "recovery"
                    st.session_state.chat_history = []
                    st.session_state.recovery_step = 1
                    response = LoginSimulator.start_genai_recovery_chat("", username_input)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                else:
                    st.session_state.chat_mode = "normal"
                    st.session_state.chat_history = []
                    st.session_state.recovery_step = 1
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": f"Hello, {username_input}! <b>Your account is active.</b><br> How can I assist you "
                                   f"today?"
                    })
                st.session_state.last_message = None
                st.rerun()
            else:
                st.error("Username not found.")
        else:
            st.error("Please enter a username.")

    if st.session_state.username and st.session_state.chat_mode:
        if 'processing_message' not in st.session_state:
            st.session_state.processing_message = False

        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                if msg['role'] == 'user':
                    st.markdown(f'<div class="chat-message user-message">You: {msg["content"]}</div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message bot-message">Bot: {msg["content"]}</div>',
                                unsafe_allow_html=True)

        bot_response_placeholder = st.empty()

        with st.form(key=f"chat_form_{st.session_state.recovery_step}", clear_on_submit=True):
            user_message = st.text_input("Your message",
                                         key=f"chat_input_{st.session_state.recovery_step}",
                                         placeholder="Type your message and press Enter")
            submit = st.form_submit_button("Send", use_container_width=True)

            if submit and user_message and not st.session_state.processing_message:
                st.session_state.processing_message = True

                if not (st.session_state.chat_history and
                        st.session_state.chat_history[-1]["role"] == "user" and
                        st.session_state.chat_history[-1]["content"] == user_message):
                    st.session_state.chat_history.append({"role": "user", "content": user_message})

                    with chat_container:
                        st.markdown(f'<div class="chat-message user-message">You: {user_message}</div>',
                                    unsafe_allow_html=True)

                    with bot_response_placeholder:
                        st.markdown('<div class="chat-message loading-bubble">Bot: Thinking...</div>',
                                    unsafe_allow_html=True)

                    if st.session_state.chat_mode == "recovery":
                        response = LoginSimulator.genai_chat_response(user_message, st.session_state.chat_history,
                                                                      st.session_state.username)
                    else:
                        response = LoginSimulator.genai_chat_response(
                            user_message,
                            st.session_state.chat_history,
                            st.session_state.username
                        )

                    st.session_state.chat_history.append({"role": "assistant", "content": response})

                    with bot_response_placeholder:
                        st.markdown(f'<div class="chat-message bot-message">Bot: {response}</div>',
                                    unsafe_allow_html=True)

                    st.session_state.recovery_step += 1

                    if st.session_state.chat_mode == "recovery" and "account is now unlocked" in response.lower():
                        st.session_state.recovery_step = 0
                        st.session_state.chat_mode = "normal"
                        st.session_state.insights_username = st.session_state.username
                        st.success("Recovery complete! You can now log in or continue chatting.")

                    st.session_state.processing_message = False

                    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)
