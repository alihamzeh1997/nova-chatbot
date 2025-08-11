import streamlit as st
import requests
import uuid
import json
from datetime import datetime

# Configure Streamlit page
st.set_page_config(
    page_title="ChatGPT",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with dark gradient design inspired by the UI template
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {visibility: hidden;}
    
    /* Global dark theme */
    .stApp {
        background: linear-gradient(135deg, #1a1d29 0%, #26293b 100%);
        color: #ffffff;
    }
    
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 56rem;
        margin: 0 auto;
        background: transparent;
    }
    
    /* Header styling */
    .chat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }
    
    .chat-title {
        font-size: 1.75rem;
        font-weight: 600;
        color: #ffffff;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .session-info {
        font-size: 0.875rem;
        color: rgba(255, 255, 255, 0.7);
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        padding: 1.5rem 0;
        border-radius: 1rem;
        margin-bottom: 1rem;
    }
    
    /* User message styling */
    [data-testid="chat-message-user"] {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(147, 51, 234, 0.15) 100%);
        border: 1px solid rgba(59, 130, 246, 0.2);
        border-radius: 1rem;
        backdrop-filter: blur(10px);
        margin-left: 4rem;
    }
    
    [data-testid="chat-message-user"] > div {
        background: transparent;
        padding: 1.5rem;
        color: #ffffff;
        border-radius: 1rem;
    }
    
    /* Assistant message styling */
    [data-testid="chat-message-assistant"] {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.2);
        border-radius: 1rem;
        backdrop-filter: blur(10px);
        margin-right: 4rem;
    }
    
    [data-testid="chat-message-assistant"] > div {
        background: transparent;
        padding: 1.5rem;
        color: #ffffff;
        border-radius: 1rem;
    }
    
    /* Input styling */
    .stChatInput > div {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 1.5rem;
        backdrop-filter: blur(20px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    .stChatInput input {
        background: transparent !important;
        border: none !important;
        color: #ffffff !important;
        padding: 1rem 1.5rem !important;
        font-size: 1rem !important;
    }
    
    .stChatInput input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 1.5rem !important;
        border-radius: 0.75rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.6) !important;
    }
    
    /* Email container styling */
    .email-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 70vh;
        text-align: center;
    }
    
    .email-form {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 3rem;
        border-radius: 1.5rem;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        max-width: 450px;
        width: 100%;
    }
    
    /* Form inputs */
    .stTextInput > div > div > input {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 0.75rem !important;
        color: #ffffff !important;
        padding: 0.75rem 1rem !important;
        backdrop-filter: blur(10px) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    .stTextInput label {
        color: #ffffff !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* Welcome message */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
        border-radius: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(20px);
        padding: 3rem;
        margin: 2rem 0;
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .welcome-subtitle {
        font-size: 1.125rem;
        color: rgba(255, 255, 255, 0.8);
        margin-bottom: 2rem;
    }
    
    /* Error styling */
    .stAlert > div {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.2) 100%) !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
        color: #fca5a5 !important;
        border-radius: 0.75rem !important;
    }
    
    /* Success styling */
    .stSuccess > div {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.2) 0%, rgba(5, 150, 105, 0.2) 100%) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        color: #6ee7b7 !important;
        border-radius: 0.75rem !important;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }
</style>
""", unsafe_allow_html=True)

# N8N Configuration
N8N_TIMEOUT = 30  # Request timeout in seconds

def get_webhook_url():
    """Get webhook URL from secrets"""
    try:
        return st.secrets["webhook"]["url"]
    except KeyError:
        st.error("❌ Webhook URL not configured in secrets. Please add it to .streamlit/secrets.toml")
        st.stop()

def initialize_session():
    """Initialize session state variables"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "is_loading" not in st.session_state:
        st.session_state.is_loading = False
    
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    
    if "email_submitted" not in st.session_state:
        st.session_state.email_submitted = False

def send_message_to_n8n(message, session_id, user_email):
    """Send message to n8n workflow and return response"""
    webhook_url = get_webhook_url()
    
    try:
        payload = {
            "message": message,
            "session_id": session_id,
            "user_email": user_email,
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            webhook_url,
            json=payload,
            timeout=N8N_TIMEOUT,
            headers={"Content-Type": "application/json"}
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"Connection error: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid response format from server."}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

def display_chat_header():
    """Display modern dark-themed header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<h1 class="chat-title">🤖 AI Assistant</h1>', unsafe_allow_html=True)
    
    with col2:
        session_short = st.session_state.session_id[:8]
        if st.button("🔄 New Chat", key="new_chat", help="Start a fresh conversation"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.email_submitted = False
            st.session_state.user_email = None
            st.rerun()
        
        st.markdown(f'<div class="session-info">💬 Session: {session_short}</div>', 
                   unsafe_allow_html=True)

def display_email_form():
    """Display email input form with dark gradient design"""
    st.markdown('<div class="email-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="email-form">
        <h2 style="color: #ffffff; margin-bottom: 1rem; font-weight: 600; font-size: 1.75rem;">Welcome to AI Chat</h2>
        <p style="color: rgba(255, 255, 255, 0.8); margin-bottom: 2rem; font-size: 1rem; line-height: 1.5;">Enter your email to start an intelligent conversation</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("email_form", clear_on_submit=False):
        email = st.text_input(
            "Email Address",
            placeholder="your.email@example.com",
            help="We'll use this to personalize your chat experience"
        )
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            submitted = st.form_submit_button("🚀 Start Chatting", use_container_width=True)
        
        if submitted:
            if email and "@" in email and "." in email:
                st.session_state.user_email = email
                st.session_state.email_submitted = True
                st.rerun()
            else:
                st.error("Please enter a valid email address")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_welcome_message():
    """Display welcome message when no messages exist"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-title">✨ How can I assist you today?</div>
        <div class="welcome-subtitle">Ask me anything - I'm here to help with your questions and tasks</div>
    </div>
    """, unsafe_allow_html=True)

def display_chat_messages():
    """Display all chat messages"""
    if not st.session_state.messages:
        display_welcome_message()
    else:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

def main():
    # Initialize session
    initialize_session()
    
    # Check if user has entered email
    if not st.session_state.email_submitted:
        display_email_form()
        return
    
    # Display header
    display_chat_header()
    
    # Display existing chat messages
    display_chat_messages()
    
    # Chat input
    if prompt := st.chat_input(
        "💭 Type your message here...", 
        disabled=st.session_state.is_loading,
        key="chat_input"
    ):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Show loading state
        st.session_state.is_loading = True
        
        # Display assistant response placeholder
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Send message to n8n
                response = send_message_to_n8n(
                    prompt, 
                    st.session_state.session_id, 
                    st.session_state.user_email
                )
                
                # Handle response
                if "error" in response:
                    st.error(f"❌ {response['error']}")
                    assistant_response = "Sorry, I encountered an error. Please try again."
                else:
                    # Handle your specific n8n response format: [{"output": "message"}]
                    try:
                        if isinstance(response, list) and len(response) > 0:
                            # Extract from array format
                            first_item = response[0]
                            if isinstance(first_item, dict) and "output" in first_item:
                                assistant_response = first_item["output"]
                            else:
                                assistant_response = str(first_item)
                        elif isinstance(response, dict):
                            # Fallback to other possible formats
                            assistant_response = (
                                response.get("output") or 
                                response.get("response") or 
                                response.get("message") or 
                                response.get("text") or
                                str(response)
                            )
                        else:
                            assistant_response = str(response)
                    except Exception as e:
                        st.error(f"Error parsing response: {str(e)}")
                        assistant_response = "Sorry, I couldn't parse the response from the server."
                
                # Display assistant response
                st.markdown(assistant_response)
        
        # Add assistant response to messages
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
        
        # Reset loading state
        st.session_state.is_loading = False
        
        # Rerun to update the interface
        st.rerun()

if __name__ == "__main__":
    main()