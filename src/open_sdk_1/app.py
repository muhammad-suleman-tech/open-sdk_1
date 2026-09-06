import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from agents import Runner, SQLiteSession

from open_sdk_1.app_agents import triage_agent

load_dotenv()

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Kisan Dost - AI Agronomy Helpline",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Custom CSS (Eliminates Margins, Custom Background & Kisan Portrait) ---
st.markdown("""
    <style>
    /* Full App Background */
    .stApp {
        background: linear-gradient(135deg, #0f3325 0%, #1b4d3e 40%, #2e7d32 80%, #388e3c 100%) !important;
        color: #ffffff;
    }
    
    /* Remove Default Streamlit Top and Bottom Whitespace Padding */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }

    /* Style Chat Input Bar Wrapper */
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stChatInputContainer {
        border-radius: 15px !important;
        border: 2px solid #ffd54f !important;
        background-color: #ffffff !important;
        margin-bottom: 0px !important;
    }

    /* FORCED BLACK TEXT FIX FOR CHAT INPUT & ALL INNER CONTAINERS */
    .stChatInputContainer *, 
    .stChatInputContainer textarea, 
    div[data-baseweb="input"] *,
    div[data-baseweb="textarea"] *,
    textarea[data-testid="stChatInputTextArea"] {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        background-color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 600 !important;
        caret-color: #000000 !important;
    }

    /* Placeholder Text Color */
    .stChatInputContainer textarea::placeholder,
    textarea[data-testid="stChatInputTextArea"]::placeholder {
        color: #555555 !important;
        -webkit-text-fill-color: #555555 !important;
    }

    /* Hero Banner with Farmer Portrait and Logo */
    .hero-banner {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(12px);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 20px 30px;
        margin-top: 15px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .hero-text {
        text-align: left;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffd54f;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.4);
        margin: 0;
    }
    .hero-subtitle {
        font-size: 1.1rem;
        color: #e8f5e9;
        font-weight: 500;
        margin-top: 5px;
    }
    
    /* Farmer Portrait Badge */
    .farmer-badge {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        border: 3px solid #ffd54f;
        object-fit: cover;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    /* Feature Cards Dashboard */
    .feature-card {
        background: rgba(255, 255, 255, 0.15);
        border-radius: 12px;
        padding: 12px;
        text-align: center;
        color: white;
        border: 1px solid rgba(255, 255, 255, 0.2);
        font-weight: 600;
    }

    /* Chat Messages Styling */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 15px !important;
        padding: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
        margin-bottom: 12px !important;
    }

    /* Force text inside chat bubbles to pure black */
    .stChatMessage, .stChatMessage p, .stChatMessage div, .stChatMessage span, .stChatMessage li {
        color: #000000 !important;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #091e17 0%, #11382b 100%) !important;
        border-right: 2px solid rgba(255, 255, 255, 0.1) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    /* Buttons Styling */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #ffd54f 0%, #ffb300 100%) !important;
        color: #0d2818 !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 10px 16px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. Hero Header with Farmer Portrait & Logo ---
st.markdown("""
    <div class="hero-banner">
        <div class="hero-text">
            <div class="hero-title">🌾 KISAN DOST (KISAAN KA HUMSAFAR)</div>
            <div class="hero-subtitle">24/7 AI Agronomy Helpline for Pakistani Farmers</div>
            <div style="font-size: 1.4rem; margin-top: 8px;">🚜 🌾 💧 ☀️ 📈 🌿</div>
        </div>
        <div>
            <img src="https://cdn-icons-png.flaticon.com/512/1995/1995515.png" class="farmer-badge" alt="Kisan Portrait">
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 4. Interactive Stat Widgets ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown('<div class="feature-card">🌱 Crop Advice<br><small>Rabi & Kharif</small></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="feature-card">🧪 Fertilizer Plan<br><small>Urea & DAP NPK</small></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="feature-card">🐛 Pest Control<br><small>Dosage & Safety</small></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="feature-card">📈 Mandi Rates<br><small>Punjab Wholesale</small></div>', unsafe_allow_html=True)

st.write("")

# --- 5. Sidebar: Farmer Controls & Quick Presets ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1995/1995515.png", width=110)
    st.markdown("## 👨‍🌾 Farmer Portal")
    st.markdown("---")
    st.write("💡 **Ask anything in Roman Urdu or English!**")

    st.markdown("### 📌 Quick Questions")
    
    preset_query = None
    if st.button("🌱 5 Acre Crop Recommendation"):
        preset_query = "Mery pass 5 acre zameen hai Faisalabad me, Rabi season me konsi fasal ugau?"
    if st.button("🧪 Fertilizer Cost Calculator"):
        preset_query = "Wheat crop ke liye 5 acre par kitni Urea aur DAP lagegi?"
    if st.button("🐛 Whitefly Pest Spray"):
        preset_query = "Kapas ke patte muRh rahe hain aur sufaid makhi hai, kya spray karu?"
    if st.button("📈 Mandi Rates Today"):
        preset_query = "Faisalabad mandi me gandum aur kapas ka kya rate hai?"

    st.markdown("---")
    if st.button("🧹 Clear Chat History"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Assalam-o-Alaikum! Main Kisan Dost hoon. Aap apnee fasal, khad, ya keeday mar dawa ke baray mein sawal pooch sakty hain."}
        ]
        st.rerun()

# --- 6. Session & Chat History Initialization ---
if "session" not in st.session_state:
    st.session_state.session = SQLiteSession("kisan_dost_session.db")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Assalam-o-Alaikum! Main Kisan Dost hoon. Aap apnee fasal, khad, keeday mar dawa, ya mandi ke raton ke baray mein Roman Urdu ya English mein pooch sakty hain."}
    ]

# --- 7. Render Conversation ---
for msg in st.session_state.messages:
    avatar = "👨‍🌾" if msg["role"] == "user" else "🤖"
    st.chat_message(msg["role"], avatar=avatar).write(msg["content"])

# --- 8. Handle Prompts ---
user_input = st.chat_input("Apna sawal yahan likhein... (e.g. 5 acre zameen ke liye khad ka hisab bataen)")

if preset_query:
    user_input = preset_query

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user", avatar="👨‍🌾").write(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("🚜 Kisan Dost information ikatha kar raha hai..."):
            try:
                async def run_agent():
                    return await Runner.run(
                        triage_agent,
                        input=user_input,
                        session=st.session_state.session
                    )

                result = asyncio.run(run_agent())
                response_text = result.final_output

                st.write(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")