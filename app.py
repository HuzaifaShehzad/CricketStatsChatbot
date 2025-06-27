import streamlit as st
import base64
from chatbot_backend import load_cricket_data, get_context_from_df, query_gemini_flash

# ✅ Always the first Streamlit command
st.set_page_config(page_title="🏏 RCB Gemini Cricket Stats Chatbot", layout="wide")

# ✅ Load and encode image as base64
@st.cache_resource
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ✅ Inject background image and RCB-themed CSS
def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        color: white;
    }}

    h1 {{
        color: #FFD700;
        text-shadow: 2px 2px black;
    }}

   

    .stTextInput > div > div > input {{
        background-color: #1F1F1F;
        color: white;
    }}

    .stButton>button {{
        background-color: #DA1818;
        color: white;
        border-radius: 6px;
        border: none;
    }}

    .stSpinner {{
        color: #FFD700 !important;
    }}
    </style>
    """
    st.markdown(page_bg_img, unsafe_allow_html=True)

# ✅ Apply the RCB background theme
set_png_as_page_bg("stadium.jpg")

# ✅ Load player data and prepare Gemini context
df = load_cricket_data("serena_warriors_full_stats.csv")
context = get_context_from_df(df)

# ✅ Title and layout
st.markdown("<h1 style='text-align:center;'>🏏 Gemini Cricket Stats Chatbot</h1>", unsafe_allow_html=True)
st.markdown("<div class='chatbox'>", unsafe_allow_html=True)

# ✅ Input for user queries
query = st.text_input("Ask something about cricket stats 👇", placeholder="e.g. Who has the highest strike rate?")

# ✅ Chatbot response
if query:
    with st.spinner("Thinking with Gemini Flash..."):
        try:
            answer = query_gemini_flash(context, query)

            # ✅ Display answer inside RCB chat bubble
            st.markdown(f"""
                <div style="
                    background-color: rgba(218, 24, 24, 0.9);
                    padding: 1rem;
                    border-radius: 12px;
                    border: 2px solid #FFD700;
                    color: white;
                    font-size: 16px;
                    margin-top: 1rem;
                ">
                    🗣️ <strong>Gemini says:</strong><br>{answer}
                </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error: {e}")

# ✅ Close the chatbox
st.markdown("</div>", unsafe_allow_html=True)
