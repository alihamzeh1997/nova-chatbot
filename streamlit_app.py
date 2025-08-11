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

# Custom CSS to make it look like ChatGPT
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 48rem;
        margin: 0 auto;
    }
    
    /* Header styling */
    .chat-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        border-bottom: 1px solid #e5e5e5;
        margin-bottom: 1rem;
    }
    
    .chat-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #202123;
        margin: 0;
    }
    
    .session-info {
        font-size: 0.875rem;
        color: #6b7280;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        padding: 1.5rem 0;
    }
    
    /* User message styling */
    [data-testid="chat-message-user"] {
        background-color: transparent;
    }
    
    [data-testid="chat-message-user"] > div {
        background-color: #f7f7f8;
        padding: 1rem 1.5rem;
        border-radius: 1rem;
        margin-left: 2rem;
        max-width: 70%;
        margin-left: auto;
    }
    
    /* Assistant message styling */
    [data-testid="chat-message-assistant"] {
        background-color: transparent;
    }
    
    [data-testid="chat-message-assistant"] > div {
        background-color: transparent;
        padding: 1rem 0;
        max-width: 100%;
    }
    
    /* Input styling */
    .stChatInput > div {
        border-radius: 1.5rem;
        border: 1px solid #d1d5db;
        background-color: white;
    }
    
    .stChatInput input {
        border: none;
        padding: 1rem 1.5rem;
        font-size: 1rem;
    }
    
    /* Button styling */
    .new-chat-btn {
        background-color: #10a37f;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 500;
    }
    
    .new-chat-btn:hover {
        background-color: #0d9668;
    }
    
    /* Email input styling */
    .email-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 60vh;
        text-align: center;
    }
    
    .email-form {
        background-color: white;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        max-width: 400px;
        width: 100%;
    }
    
    /* Spinner styling */
    .stSpinner > div {
        border-top-color: #10a37f;
    }
    
    /* Welcome message */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 50vh;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 600;
        color: #202123;
        margin-bottom: 0.5rem;
    }
    
    .welcome-subtitle {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
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
    """Display ChatGPT-like header"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown('<h1 class="chat-title">ChatGPT</h1>', unsafe_allow_html=True)
    
    with col2:
        session_short = st.session_state.session_id[:8]
        if st.button("🔄 New Chat", key="new_chat", help="Start a new conversation"):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.session_state.email_submitted = False
            st.session_state.user_email = None
            st.rerun()
        
        st.markdown(f'<div class="session-info">Session: {session_short}</div>', 
                   unsafe_allow_html=True)

def display_email_form():
    """Display email input form"""
    st.markdown('<div class="email-container">', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="email-form">
        <h2 style="color: #202123; margin-bottom: 1rem;">Welcome to ChatGPT</h2>
        <p style="color: #6b7280; margin-bottom: 1.5rem;">Please enter your email address to start chatting</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("email_form", clear_on_submit=False):
        email = st.text_input(
            "Email Address",
            placeholder="Enter your email address",
            help="We'll use this to personalize your experience"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            submitted = st.form_submit_button("Start Chatting", use_container_width=True)
        
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
        <div class="welcome-title">How can I help you today?</div>
        <div class="welcome-subtitle">Start a conversation by typing a message below</div>
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
        "Message ChatGPT...", 
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