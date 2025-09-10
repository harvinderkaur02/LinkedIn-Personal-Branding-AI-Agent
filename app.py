
import streamlit as st
import os
import random
from datetime import date
from io import BytesIO
from dotenv import load_dotenv
import google.generativeai as genai 

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit

from database import init_db, add_post, get_posts, register_user, login_user, get_user, update_user,  add_draft, get_drafts, delete_draft, get_user_stats
import base64
import pandas as pd
import matplotlib.pyplot as plt
from openpyxl import Workbook
import bcrypt
import mysql.connector
import json
import pyperclip
import re                                               # for email validation

# ---------- Load keys ----------
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(page_title="LinkedIn AI Branding Agent", layout="wide")
st.title("🤖 LinkedIn Personal Branding AI Agent")
st.caption("Generate, schedule, and export LinkedIn posts effortlessly with AI. Perfect for building your personal brand, tracking engagement, and planning content—all in one beginner-friendly MVP.")

# ---------- Init session state ----------
if "generated_post" not in st.session_state:
    st.session_state.generated_post = ""
if "generated_hashtags" not in st.session_state:
    st.session_state.generated_hashtags = ""
#--new add---
if "user" not in st.session_state:
    st.session_state.user = None  # will store logged-in user info


# ---------- DB init ----------
init_db()


# --------- Utility Functions ---
def optimize_hashtags(hashtags_str):
    """Clean, normalize, and optimize hashtags for LinkedIn best practices"""
    if not hashtags_str:
        return ""

    # Split by spaces or commas
    raw_tags = hashtags_str.replace(",", " ").split()

    cleaned = []
    for tag in raw_tags:
        tag = tag.strip().lower()  # normalize case
        if not tag:
            continue
        if not tag.startswith("#"):
            tag = "#" + tag
        cleaned.append(tag)

    # Remove duplicates while keeping order
    seen = set()
    unique_tags = []
    for t in cleaned:
        if t not in seen:
            unique_tags.append(t)
            seen.add(t)

    # Limit to max 5 hashtags
    return " ".join(unique_tags[:5])



# ---------- Helpers ----------
def generate_post(name, role, industry, interests):
    """Generate LinkedIn post via Gemini, with fallback template."""
    if not GEMINI_API_KEY:
        return fallback_post(name, role, industry, interests)

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""You are an expert LinkedIn content writer.
Create a concise, engaging LinkedIn post for {name}, a {role} in the {industry} industry.
Include a friendly tone, one short value takeaway in bullet form, and a soft call-to-action.
Incorporate interests: {interests}. Keep it under 120 words. No emojis in bullet lines."""
        resp = model.generate_content(prompt)
        post_content = resp.text.strip()

        hashtag_prompt = f"Suggest 5 short, relevant LinkedIn hashtags for {industry} and {interests}. Output as space-separated tags."
        hash_resp = model.generate_content(hashtag_prompt)
        hashtags = hash_resp.text.strip()

        return post_content, hashtags
    except Exception as e:
        st.error(f"Gemini API failed: {e}")
        return fallback_post(name, role, industry, interests)

def fallback_post(name, role, industry, interests):
    """Always works: no API needed."""
    post = f"""Excited to share a quick update! 👋

I'm {name}, working towards {role} in the {industry} space. Recently I explored topics around {interests}.
Key learnings:
• Stay consistent with hands-on practice
• Share small wins publicly
• Ask for feedback from the community

If you're also into {industry}, let's connect and learn together! #learning #growth"""
    hashtags = "#career #learning #coding"
    return post.strip(), hashtags

def make_pdf_bytes(content, hashtags, schedule_date):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    max_width = width - 100
    y = 750

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, "LinkedIn Post")
    y -= 30

    c.setFont("Helvetica", 11)
    wrapped = simpleSplit(content, "Helvetica", 11, max_width)
    for line in wrapped:
        if y < 80:
            c.showPage()
            y = 750
            c.setFont("Helvetica", 11)
        c.drawString(50, y, line)
        y -= 16

    y -= 10
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, y, f"Hashtags: {hashtags}")
    y -= 16
    c.drawString(50, y, f"Scheduled Date: {schedule_date}")
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# ---------- Authentication ----------
# ---------- Authentication ----------

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown(
        """
        <style>
        .auth-card {
            background-color: #161b22;  /* dark background */
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.6);
            text-align: center;
            color: #e6edf3;
        }
        /* Style for text inputs */
        .stTextInput > div > div > input {
            background-color: #0d1117;
            color: #e6edf3;
            border: 1px solid #30363d;
            border-radius: 8px;
        }
        /* Style for radio buttons */
        .stRadio > label {
            background-color: #21262d;
            color: #e6edf3;
            border-radius: 8px;
            padding: 6px 12px;
            margin-right: 8px;
            cursor: pointer;
        }
        .stRadio > label:hover {
            background-color: #30363d;
        }
        .stRadio [type="radio"]:checked + div {
            background-color: #0969da !important;
            color: white !important;
            border-radius: 8px;
        }
        /* LinkedIn-style centered buttons */
        div.stButton > button:first-child {
            background: linear-gradient(90deg, #0072b1, #0a66c2);
            color: white;
            font-weight: bold;
            border-radius: 10px;
            padding: 10px 30px;
            border: none;
            transition: all 0.3s ease;
            display: inline-block;
            margin: 10px auto;
        }
        div.stButton {
            text-align: center; /* center align button */
        }
        div.stButton > button:first-child:hover {
            background: linear-gradient(90deg, #005582, #004182);
            transform: scale(1.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.subheader("🔐 Please login/signup to continue.")

    # Center with 3 columns
    col1, col2, col3 = st.columns([1,2,1])

    with col2:  # middle
        with st.container():
            st.markdown('<div class="auth-card">', unsafe_allow_html=True)

            auth_choice = st.radio("Choose", ["Login", "Signup"], horizontal=True, label_visibility="collapsed")

            if auth_choice == "Signup":
                st.subheader("Create Account")
                signup_name = st.text_input("Full Name")
                signup_email = st.text_input("Email")
                signup_password = st.text_input("Password", type="password")

                if st.button("Create Account"):
                    # --- Validation ---
                    if not signup_name.strip():
                        st.error("❌ Name cannot be empty.")
                    elif not re.match(r"[^@]+@[^@]+\.[^@]+", signup_email):
                        st.error("❌ Invalid email format.")
                    elif len(signup_password) < 6:
                        st.error("❌ Password must be at least 6 characters.")
                    else:
                        success = register_user(signup_name.strip(), signup_email.strip(), signup_password)
                        if success:
                            st.success("✅ Account created! Please login.")
                        else:
                            st.error("❌ Signup failed. Email may already exist.")

            elif auth_choice == "Login":
                st.subheader("Login to Continue")
                login_email = st.text_input("Email")
                login_password = st.text_input("Password", type="password")

                if st.button("Login"):
                    if not login_email.strip() or not login_password:
                        st.error("❌ Please enter email and password.")
                    else:
                        user = login_user(login_email.strip(), login_password)
                        if user:
                            st.session_state.user = user
                            st.success(f"✅ Welcome {user['name']}!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials.")

            st.markdown('</div>', unsafe_allow_html=True)

    st.stop()  # prevent showing main app before login









# ---------------- MAIN APP ----------------
# ---------- Top Navbar with Logout ----------
# col1, col2, col3 = st.columns([6, 2, 1])  # adjust ratios for spacing

# with col1:
#     st.markdown("### 🤖 LinkedIn Personal Branding AI Agent")  # optional title/logo here

# if "user" in st.session_state and st.session_state.user:
#     with col2:
#         st.markdown(f"👋 Hello, **{st.session_state.user['name']}**")

#     with col3:
#         if st.button("🚪 Logout", use_container_width=True):
#             del st.session_state.user
#             st.rerun()


# ---------------- MAIN APP ----------------
# ---------- Top Navbar with Logout ----------
col1, col2, col3 = st.columns([6, 2, 1])  # adjust ratios for spacing

with col1:
    st.markdown(
        """
        <style>
        .app-title {
            font-size: 20px;
            font-weight: 600;
            color: #1f77b4;
            margin: 0;
            padding: 6px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="app-title">🤖 LinkedIn Personal Branding AI Agent</div>', unsafe_allow_html=True)

if "user" in st.session_state and st.session_state.user:
    with col2:
        st.markdown(
            f"""
            <style>
            .greeting {{
                font-size: 16px;
                color: #eee;
                padding: 6px 0;
                text-align: right;
            }}
            </style>
            <div class="greeting">👋 Hello, <b>{st.session_state.user['name']}</b></div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        st.markdown(
            """
            <style>
            .stButton>button {
                background:#d9534f;
                color:white;
                border-radius:6px;
                font-size:14px;
                padding:6px 12px;
            }
            .stButton>button:hover {
                background:#c9302c;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        if st.button("🚪 Logout", use_container_width=True):
            del st.session_state.user
            st.rerun()



# -------sidebar----
# # ---------- Sidebar -------- 
# user_id = st.session_state.user["id"]
# user_data = get_user(user_id)

# # --- Gather stats (real only) ---
# from database import get_user_stats  # make sure this exists

# stats = get_user_stats(user_id)
# posts_created = stats.get("posts", 0)
# drafts_saved = stats.get("drafts", 0)

# with st.sidebar:
#     st.markdown("## 🌟 Profile", unsafe_allow_html=True)

#     # --- Profile Picture Preview (circular, centered, bordered, hover zoom, clickable) ---
#     if user_data and user_data.get("profile_pic"):
#         try:
#             profile_pic_b64 = user_data["profile_pic"]
#             st.markdown(
#                 f"""
#                 <style>
#                 .profile-pic {{
#                     width:120px; height:120px;
#                     border-radius:50%;
#                     object-fit:cover;
#                     border:3px solid #1f77b4;
#                     transition: transform 0.2s ease-in-out, box-shadow 0.2s;
#                 }}
#                 .profile-pic:hover {{
#                     transform: scale(1.1);
#                     box-shadow: 0 0 12px #1f77b4;
#                 }}
#                 </style>
#                 <div style="text-align:center;">
#                     <a href="data:image/png;base64,{profile_pic_b64}" target="_blank" download="profile.png">
#                         <img src="data:image/png;base64,{profile_pic_b64}" class="profile-pic"/>
#                     </a>
#                 </div>
#                 """,
#                 unsafe_allow_html=True
#             )
#         except Exception:
#             st.warning("⚠️ Could not load profile picture.")
#     else:
#         st.markdown(
#             """
#             <style>
#             .profile-pic {
#                 width:120px; height:120px;
#                 border-radius:50%;
#                 object-fit:cover;
#                 border:3px solid #1f77b4;
#                 transition: transform 0.2s ease-in-out, box-shadow 0.2s;
#             }
#             .profile-pic:hover {
#                 transform: scale(1.1);
#                 box-shadow: 0 0 12px #1f77b4;
#             }
#             </style>
#             <div style="text-align:center;">
#                 <a href="https://i.imgur.com/5cLDeaR.png" target="_blank">
#                     <img src="https://i.imgur.com/5cLDeaR.png" class="profile-pic"/>
#                 </a>
#             </div>
#             """,
#             unsafe_allow_html=True
#         )


#     # --- User Info Card ---
#     st.markdown(
#         f"""
#         <div style='text-align:center; padding:10px;'>
#             <h3 style='margin-bottom:5px; color:#eee;'>{user_data.get("name", "Guest")}</h3>
#             <p style='margin:0; font-size:14px; color:#ccc;'>{user_data.get("role", "Member")}</p>
#             <p style='margin:0; font-size:13px; color:#1f77b4;'>🚀 AI Branding Agent</p>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     st.markdown("---")

#     # --- User Stats (only real values) ---
#     st.markdown("### 📊 Your Stats", unsafe_allow_html=True)
#     st.markdown(
#         f"""
#         <div style='text-align:center; padding:8px 12px; font-size:14px; color:#ddd;'>
#             📅 Posts Created: <b>{posts_created}</b><br>
#             💡 Drafts Saved: <b>{drafts_saved}</b>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     st.markdown("---")

#     # --- Pro Tip ---
#     st.markdown("### 💡 Pro Tip", unsafe_allow_html=True)
#     st.markdown(
#         """
#         <div style='text-align:center; padding:8px 12px; font-size:13px; color:#bbb; font-style:italic;'>
#             Use storytelling in your posts to boost engagement by 30%!
#         </div>
#         """,
#         unsafe_allow_html=True
#     )

#     st.markdown("---")

#     # --- Footer ---
#     st.markdown(
#         "<p style='text-align:center; font-size:12px; color:#aaa;'>Made with ❤️ using Streamlit + Gemini AI</p>",
#         unsafe_allow_html=True
#     )

# # --- Dark Theme CSS applied globally ---
# st.markdown(
#     """
#     <style>
#     .stApp { background-color: #0e1117; color: #eee; }
#     .stSidebar { background-color: #161b22; color:#eee !important; }
#     .stSidebar div, .stSidebar h3, .stSidebar p, .stSidebar span, .stSidebar a { color:#eee !important; text-align:center !important; }
#     .stButton>button { background:#1f77b4; color:white; border-radius:8px; }
#     .stTabs [data-baseweb="tab"] { color:white; font-weight:500; }
#     </style>
#     """,
#     unsafe_allow_html=True
# )


# ---------- Sidebar -------- 
user_id = st.session_state.user["id"]
user_data = get_user(user_id)

# --- Gather stats (real only) ---
from database import get_user_stats  # make sure this exists

stats = get_user_stats(user_id)
posts_created = stats.get("posts", 0)
drafts_saved = stats.get("drafts", 0)

with st.sidebar:
    st.markdown("## 🌟 Profile", unsafe_allow_html=True)

    # --- Profile Picture Preview (circular, centered, hover zoom, light glow) ---
    if user_data and user_data.get("profile_pic"):
        try:
            profile_pic_b64 = user_data["profile_pic"]
            st.markdown(
                f"""
                <style>
                .profile-pic {{
                    width:120px; height:120px;
                    border-radius:50%;
                    object-fit:cover;
                    border:3px solid #1f77b4;
                    transition: transform 0.25s ease-in-out, box-shadow 0.25s;
                }}
                .profile-pic:hover {{
                    transform: scale(1.08);
                    box-shadow: 0 0 18px #1f77b4;
                }}
                </style>
                <div style="text-align:center; margin-bottom:12px;">
                    <a href="data:image/png;base64,{profile_pic_b64}" target="_blank">
                        <img src="data:image/png;base64,{profile_pic_b64}" class="profile-pic"/>
                    </a>
                </div>
                """,
                unsafe_allow_html=True
            )
        except Exception:
            st.warning("⚠️ Could not load profile picture.")
    else:
        st.markdown(
            """
            <style>
            .profile-pic {
                width:120px; height:120px;
                border-radius:50%;
                object-fit:cover;
                border:3px solid #1f77b4;
                transition: transform 0.25s ease-in-out, box-shadow 0.25s;
            }
            .profile-pic:hover {
                transform: scale(1.08);
                box-shadow: 0 0 18px #1f77b4;
            }
            </style>
            <div style="text-align:center; margin-bottom:12px;">
                <a href="https://i.imgur.com/5cLDeaR.png" target="_blank">
                    <img src="https://i.imgur.com/5cLDeaR.png" class="profile-pic"/>
                </a>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- User Info Card ---
    st.markdown(
        f"""
        <div style='text-align:center; padding:12px; border-radius:10px; background:#1a1f2e; margin-bottom:12px;'>
            <h3 style='margin-bottom:6px; color:#fff;'>{user_data.get("name", "Guest")}</h3>
            <p style='margin:0; font-size:14px; color:#bbb;'>{user_data.get("role", "Member")}</p>
            <p style='margin:4px 0 0; font-size:13px; color:#1f77b4;'>🚀 AI Branding Agent</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- User Stats ---
    st.markdown("### 📊 Your Stats", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='text-align:center; padding:10px; border-radius:10px; background:#1a1f2e; font-size:14px; color:#ddd; margin-bottom:12px;'>
            📅 Posts Created: <b>{posts_created}</b><br>
            💡 Drafts Saved: <b>{drafts_saved}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Pro Tip ---
    st.markdown("### 💡 Pro Tip", unsafe_allow_html=True)
    st.markdown(
        """
        <div style='text-align:center; padding:10px; border-radius:10px; background:#1a1f2e; font-size:13px; color:#bbb; font-style:italic; margin-bottom:12px;'>
            Use storytelling in your posts to boost engagement by 30%!
        </div>
        """,
        unsafe_allow_html=True
    )

    # --- Footer ---
    st.markdown(
        "<p style='text-align:center; font-size:12px; color:#777;'>Made with ❤️ using Streamlit + Gemini AI</p>",
        unsafe_allow_html=True
    )

# --- Dark Theme CSS applied globally ---
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: #eee; }
    .stSidebar { background-color: #161b22; color:#eee !important; }
    .stSidebar div, .stSidebar h3, .stSidebar p, .stSidebar span, .stSidebar a { color:#eee !important; text-align:center !important; }
    .stButton>button { background:#1f77b4; color:white; border-radius:8px; }
    .stButton>button:hover { background:#155a8a; }
    .stTabs [data-baseweb="tab"] { color:white; font-weight:500; }
    </style>
    """,
    unsafe_allow_html=True
)



# ---------- Sidebar: Profile ----------
# st.sidebar.header("Your Profile")
# name = st.sidebar.text_input("Name", placeholder="e.g., Harvinder Kaur")
# role = st.sidebar.text_input("Role", placeholder="e.g., AI Intern / SDE Fresher")
# industry = st.sidebar.text_input("Industry", placeholder="e.g., AI, Software, EdTech")
# interests = st.sidebar.text_area("Interests (comma separated)", placeholder="e.g., machine learning, internships, career tips")

# ---------- Tabs ----------
# ---------- Tabs ----------
# tab1, tab2, tab3, tab4, tab5 = st.tabs([
#     "✍️ Generate Content", 
#     "📅 Content Calendar & PDF Export", 
#     "👤 Profile", 
#     "📊 Analytics",
#     "📝 Drafts"
# ])


# ---------- Tabs ----------
st.markdown(
    """
    <style>
    /* Tabs container */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center;
        border-bottom: 2px solid #1f77b4;
        margin-bottom: 10px;
    }

    /* Individual tabs */
    .stTabs [data-baseweb="tab"] {
        color: #bbb;
        font-weight: 500;
        padding: 8px 16px;
        border-radius: 8px 8px 0 0;
        transition: all 0.3s ease;
    }

    /* Hover effect */
    .stTabs [data-baseweb="tab"]:hover {
        color: #fff;
        background-color: #1f77b4;
    }

    /* Active tab */
    .stTabs [aria-selected="true"] {
        color: white !important;
        background-color: #1f77b4 !important;
        font-weight: 600 !important;
        box-shadow: 0 -2px 6px rgba(31, 119, 180, 0.4);
    }
    </style>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✍️ Generate Content", 
    "📅 Content Calendar & PDF Export", 
    "👤 Profile", 
    "📊 Analytics",
    "📝 Drafts"
])



# --- Generate Content ---
# --- Generate Content ---
with tab1:
    st.subheader("Generate a LinkedIn Post")
    colA, colB = st.columns([1,1])
    with colA:
        gen_clicked = st.button("Generate Post", use_container_width=True)
    with colB:
        schedule_date = st.date_input("Schedule Date", value=date.today())

    # ✅ Always fetch latest profile info from DB
    from database import get_user
    user = get_user(st.session_state.user["id"])

    name = user.get("name", "")
    role = user.get("role", "")
    industry = user.get("industry", "")
    interests = user.get("interests", "")

    if gen_clicked:
        if not (name and role and industry and interests):
            st.warning("⚠️ Please fill in your profile (Profile tab) before generating.")
        else:
            post_content, hashtags = generate_post(name, role, industry, interests)
            st.session_state.generated_post = post_content
            st.session_state.generated_hashtags = hashtags

    if st.session_state.get("generated_post"):
        st.text_area("Generated Post", value=st.session_state.generated_post, height=220)

        # --- Character Counter ---
        char_count = len(st.session_state.generated_post)
        word_count = len(st.session_state.generated_post.split())
        st.caption(f"📝 Word count: {word_count} | Character count: {char_count} / 3000")

        # --- Hashtags as pill-style chips ---
        if st.session_state.generated_hashtags:
            hashtags_list = st.session_state.generated_hashtags.split()
            styled_tags = " ".join(
                [
                    f"<span style='background-color:#1f77b4; color:white; padding:4px 10px; "
                    f"border-radius:20px; margin:3px; display:inline-block;'>{tag}</span>"
                    for tag in hashtags_list
                ]
            )
            st.markdown("**Suggested Hashtags:**", unsafe_allow_html=True)
            st.markdown(styled_tags, unsafe_allow_html=True)

        # --- Custom CSS for toolbar buttons ---
        st.markdown("""
            <style>
            .toolbar-btn button {
                width: 100% !important;
                border-radius: 12px !important;
                padding: 8px 0px !important;
                font-weight: 600 !important;
            }
            .toolbar-row {
                display: flex;
                gap: 10px;
            }
            .toolbar-col {
                flex: 1;
            }
            </style>
        """, unsafe_allow_html=True)

        # --- Toolbar row ---
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        with col1:
            if st.button("📅 Save to Calendar", key="save_calendar"):
                if not st.session_state.generated_post.strip():
                    st.warning("⚠️ Cannot save an empty post. Please generate content first.")
                else:
                    success = add_post(
                        st.session_state.user["id"], 
                        st.session_state.generated_post, 
                        st.session_state.generated_hashtags, 
                        str(schedule_date),
                        role, industry, interests
                    )
                    if success:
                        st.success("✅ Post saved! Check the calendar tab.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save post. Try again.")

        with col2:
            if st.button("📝 Save as Draft", key="save_draft"):
                if not st.session_state.generated_post.strip():
                    st.warning("⚠️ Cannot save an empty draft.")
                else:
                    success = add_draft(
                        st.session_state.user["id"], 
                        st.session_state.generated_post, 
                        st.session_state.generated_hashtags
                    )
                    if success:
                        st.success("📝 Draft saved! Check the Drafts tab.")
                        st.rerun()
                    else:
                        st.error("❌ Failed to save draft. Try again.")

        with col3:
            if st.button("📋 Copy Post", key="copy_post"):
                import pyperclip
                pyperclip.copy(st.session_state.generated_post)
                st.success("✅ Post copied to clipboard! Now you can paste it into LinkedIn.")

        with col4:
            if st.button("🧹 Clear Post", key="clear_post"):
                st.session_state.generated_post = ""
                st.session_state.generated_hashtags = ""
                st.success("🧹 Post cleared! Generate a new one.")
                st.rerun()


# --- Content Calendar ---
# --- Content Calendar --- 
with tab2:
    st.subheader("Scheduled Posts")
    posts = get_posts(st.session_state.user["id"])

    if not posts:
        st.info("No posts yet. Generate one in the first tab.")
    else:
        import pandas as pd

        # ✅ Normalize dates before rendering
        for post in posts:
            if not post["schedule_date"]:
                post["schedule_date"] = pd.to_datetime("today").strftime("%Y-%m-%d")

        for post in posts:
            pid = post["id"]
            content = post["content"]
            hashtags = post["hashtags"]
            sdate = post["schedule_date"]
            likes = post["likes"]
            comments = post["comments"]

            with st.container(border=True):
                st.markdown(f"**Post ID:** {pid}")
                st.markdown(f"**Scheduled Date:** {sdate}")
                st.markdown(f"**Hashtags:** {hashtags}")
                st.write(content)

                # Delete button
                if st.button("🗑️ Delete Post", key=f"del_{pid}"):
                    from database import delete_post
                    if delete_post(pid, st.session_state.user["id"]):
                        st.success("✅ Post deleted successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete post.")

                # Simulated analytics
                sim_likes = likes if likes else random.randint(35, 180)
                sim_comments = comments if comments else random.randint(3, 25)
                st.caption(f"Simulated Analytics → 👍 {sim_likes}   💬 {sim_comments}")

                pdf_bytes = make_pdf_bytes(content, hashtags, sdate)
                st.download_button(
                    "⬇️ Export this post to PDF",
                    data=pdf_bytes,
                    file_name=f"linkedin_post_{pid}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"dl_{pid}"
                )


# --- Profile Tab ---
# ================== PROFILE TAB ==================
# ================== PROFILE TAB ==================
with tab3:
    st.subheader("Your Profile")

    # Get latest user info from DB
    from database import get_user, update_user, process_profile_pic
    user = get_user(st.session_state.user["id"])

    # Profile picture
    col1, col2 = st.columns([1, 3])
    with col1:
        if user.get("profile_pic"):
            st.image(
                f"data:image/png;base64,{user['profile_pic']}", 
                width=120, 
                caption="Profile Picture"
            )
        else:
            st.image("https://via.placeholder.com/120", caption="No Picture")

        uploaded_file = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"])

        if uploaded_file:
            preview_b64 = process_profile_pic(uploaded_file)
            st.image(f"data:image/png;base64,{preview_b64}", width=120, caption="Preview")

            if st.button("Save Profile Picture"):
                update_user(user["id"], profile_pic=preview_b64)
                st.success("✅ Profile picture updated!")
                st.rerun()

    # Editable fields
    with col2:
        with st.form("profile_form"):
            new_name = st.text_input("Name", value=user["name"])
            new_role = st.text_input("Role", value=user.get("role", ""))
            new_industry = st.text_input("Industry", value=user.get("industry", ""))
            new_interests = st.text_area("Interests", value=user.get("interests", ""))

            submitted = st.form_submit_button("Update Profile")
            if submitted:
                update_user(
                    user["id"],
                    name=new_name,
                    role=new_role,
                    industry=new_industry,
                    interests=new_interests
                )
                st.success("✅ Profile updated successfully!")
                st.rerun()

# --- Analytics Tab ---
with tab4:
    st.subheader("📊 Analytics Dashboard")

    posts = get_posts(st.session_state.user["id"])
    if not posts:
        st.info("No posts yet. Generate and save some posts first.")
    else:
        df = pd.DataFrame(posts)
        df = df[df["content"].notna() & (df["content"].str.strip() != "")]
        df["schedule_date"] = pd.to_datetime(df["schedule_date"])

        # --- Filters ---
        st.markdown("### 🔍 Filters")
        colA, colB = st.columns(2)
        with colA:
            start_date = st.date_input("Start Date", value=df["schedule_date"].min().date())
        with colB:
            end_date = st.date_input("End Date", value=df["schedule_date"].max().date())
        hashtag_filter = st.text_input("Filter by Hashtag (optional)", placeholder="e.g., AI, Python")

        # Apply filters
        mask = (df["schedule_date"].dt.date >= start_date) & (df["schedule_date"].dt.date <= end_date)
        if hashtag_filter:
            mask &= df["hashtags"].str.contains(hashtag_filter, case=False, na=False)
        filtered_df = df[mask]

        if filtered_df.empty:
            st.warning("⚠️ No posts found for the selected filters.")
            st.stop()

        # --- Recent Posts Table (moved up) ---
        # st.markdown("### 📝 Recent Posts")
        # st.dataframe(
        #     filtered_df[["schedule_date", "content", "hashtags"]].sort_values("schedule_date", ascending=False)
        # )

        # --- Recent Posts Table (moved up) ---
        # --- Recent Posts ---
        st.markdown("### 📝 Recent Posts")

        view_mode = st.radio("Choose View", ["📋 Table View", "📰 Card View"], horizontal=True)

        if view_mode == "📋 Table View":
            st.dataframe(
                df[["schedule_date", "content", "hashtags"]]
                .sort_values("schedule_date", ascending=False)
            )

        else:  # --- Card View ---
            for _, row in df.sort_values("schedule_date", ascending=False).iterrows():
                with st.container():
                    st.markdown(
                        f"""
                        <div style="border:1px solid #333; border-radius:10px; padding:15px; margin-bottom:15px; background:#111;">
                            <p style="color:#aaa; margin-bottom:8px;">📅 {row['schedule_date'].strftime('%Y-%m-%d')}</p>
                            <p style="color:white; font-size:15px;">{row['content']}</p>
                            <div style="margin-top:10px;">
                    """,
                        unsafe_allow_html=True,
                    )

                    # pill-style hashtags
                    tags = str(row["hashtags"]).split()
                    if tags:
                        tags_html = " ".join(
                            [f"<span style='background:#1f77b4; color:white; padding:4px 10px; border-radius:15px; margin:3px; display:inline-block; font-size:13px;'> {t} </span>" for t in tags]
                        )
                        st.markdown(tags_html, unsafe_allow_html=True)

                    st.markdown("</div></div>", unsafe_allow_html=True)


        # --- Posts per Month ---
        st.markdown("### 📅 Posts per Month")
        posts_per_month = filtered_df.groupby(filtered_df["schedule_date"].dt.to_period("M")).size()
        fig1, ax1 = plt.subplots(figsize=(7, 4))
        posts_per_month.plot(kind="bar", ax=ax1, color="#4cc9f0", edgecolor="white")
        ax1.set_ylabel("Number of Posts", color="white")
        ax1.set_xlabel("Month", color="white")
        ax1.set_title("Posting Frequency", fontsize=14, color="white")
        ax1.tick_params(axis='x', labelcolor="white", rotation=45)
        ax1.tick_params(axis='y', labelcolor="white")
        fig1.patch.set_facecolor("#0e1117")
        ax1.set_facecolor("#0e1117")
        st.pyplot(fig1)

        # --- Most Used Hashtags ---
        st.markdown("### 🔖 Most Used Hashtags")
        all_tags = " ".join(filtered_df["hashtags"].dropna().astype(str)).split()
        tags_series = pd.Series(all_tags).value_counts().head(10)
        fig2, ax2 = plt.subplots(figsize=(7, 4))
        tags_series.plot(kind="bar", ax=ax2, color="#f8961e", edgecolor="white")
        ax2.set_ylabel("Frequency", color="white")
        ax2.set_xlabel("Hashtags", color="white")
        ax2.set_title("Top Hashtags", fontsize=14, color="white")
        ax2.tick_params(axis='x', labelcolor="white", rotation=45)
        ax2.tick_params(axis='y', labelcolor="white")
        fig2.patch.set_facecolor("#0e1117")
        ax2.set_facecolor("#0e1117")
        st.pyplot(fig2)

        # --- Post Length Distribution ---
        st.markdown("### ✍️ Post Length (Word Count) Distribution")
        filtered_df["word_count"] = filtered_df["content"].apply(lambda x: len(str(x).split()))
        fig3, ax3 = plt.subplots(figsize=(7, 4))
        filtered_df["word_count"].plot(kind="hist", bins=10, ax=ax3, color="#90be6d", edgecolor="white", alpha=0.9)
        ax3.set_xlabel("Word Count", color="white")
        ax3.set_ylabel("Frequency", color="white")
        ax3.set_title("Post Length Distribution", fontsize=14, color="white")
        ax3.tick_params(axis='x', labelcolor="white")
        ax3.tick_params(axis='y', labelcolor="white")
        fig3.patch.set_facecolor("#0e1117")
        ax3.set_facecolor("#0e1117")
        st.pyplot(fig3)

        # --- Engagement Analytics (Simulated) ---
        st.markdown("### 📈 Engagement Trend (Simulated)")
        if "likes" not in filtered_df.columns or "comments" not in filtered_df.columns:
            import numpy as np
            np.random.seed(42)
            filtered_df["likes"] = np.random.randint(10, 100, size=len(filtered_df))
            filtered_df["comments"] = np.random.randint(2, 20, size=len(filtered_df))

        engagement_df = filtered_df.groupby(filtered_df["schedule_date"].dt.to_period("M"))[["likes", "comments"]].mean()
        fig4, ax4 = plt.subplots(figsize=(7, 4))
        engagement_df.plot(ax=ax4, marker="o")
        ax4.set_title("Average Engagement per Month", fontsize=14, color="white")
        ax4.set_ylabel("Engagement (Avg Likes/Comments)", color="white")
        ax4.set_xlabel("Month", color="white")
        ax4.tick_params(axis='x', labelcolor="white", rotation=45)
        ax4.tick_params(axis='y', labelcolor="white")
        ax4.legend(["Likes", "Comments"], facecolor="#0e1117", edgecolor="white", labelcolor="white")
        fig4.patch.set_facecolor("#0e1117")
        ax4.set_facecolor("#0e1117")
        st.pyplot(fig4)

        st.caption("⚠️ Engagement metrics are simulated for demo purposes. Real data requires LinkedIn API integration.")

        # --- Export Options ---
        st.markdown("### 📂 Export Filtered Analytics")
        csv_data = filtered_df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download CSV", csv_data, "linkedin_ai_analytics.csv", "text/csv", use_container_width=True)

        import io
        output = io.BytesIO()
        filtered_df.to_excel(output, index=False, sheet_name="Analytics")
        st.download_button(
            "⬇️ Download Excel",
            output.getvalue(),
            "linkedin_ai_analytics.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

# --- Drafts Tab ---
# --- Drafts Tab ---
with tab5:
    st.subheader("📝 Drafts")

    from database import get_drafts, delete_draft, add_post
    from datetime import date

    drafts = get_drafts(st.session_state.user["id"])

    if not drafts:
        st.info("No drafts yet. Generate and save one as draft.")
    else:
        df_drafts = pd.DataFrame(drafts)

        view_mode = st.radio(
            "Choose Drafts View",
            ["📋 Table View", "📰 Card View"],
            horizontal=True,
            key="drafts_view"
        )

        # ✅ Helper: format date safely, fallback → today
        def safe_date(d):
            if pd.isna(d) or d in [None, "None", ""]:
                return date.today().strftime("%Y-%m-%d")
            return d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)

        # --- Table View ---
        if view_mode == "📋 Table View":
            for _, row in df_drafts.sort_values("schedule_date", ascending=False).iterrows():
                col1, col2, col3 = st.columns([4, 1, 1])
                with col1:
                    st.markdown(f"**📅 {safe_date(row['schedule_date'])}** - {row['content'][:80]}...")
                with col2:
                    if st.button("✅ Publish", key=f"publish_{row['id']}"):
                        success = add_post(
                            st.session_state.user["id"],
                            row["content"],
                            row["hashtags"],
                            safe_date(row["schedule_date"]),
                            st.session_state.user["role"],
                            st.session_state.user.get("industry", ""),
                            st.session_state.user.get("interests", "")
                        )
                        if success:
                            delete_draft(row["id"])
                            st.success("Draft published as a post! ✅")
                            st.rerun()
                        else:
                            st.error("❌ Failed to publish draft. Check logs.")
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{row['id']}"):
                        delete_draft(row["id"])
                        st.warning("Draft deleted!")
                        st.rerun()

        # --- Card View ---
        else:
            for _, row in df_drafts.sort_values("schedule_date", ascending=False).iterrows():
                with st.container():
                    st.markdown(
                        f"""
                        <div style="border:1px solid #333; border-radius:10px; 
                                   padding:15px; margin-bottom:15px; background:#111;">
                            <p style="color:#aaa; margin-bottom:8px;">📅 {safe_date(row['schedule_date'])}</p>
                            <p style="color:white; font-size:15px;">{row['content']}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    tags = str(row["hashtags"]).split()
                    if tags:
                        tags_html = " ".join(
                            [
                                f"<span style='background:#1f77b4; color:white; padding:4px 10px; "
                                f"border-radius:15px; margin:3px; display:inline-block; font-size:13px;'> {t} </span>"
                                for t in tags
                            ]
                        )
                        st.markdown(tags_html, unsafe_allow_html=True)

                    colA, colB = st.columns([1, 1])
                    with colA:
                        if st.button("✅ Publish", key=f"publish_card_{row['id']}"):
                            success = add_post(
                                st.session_state.user["id"],
                                row["content"],
                                row["hashtags"],
                                safe_date(row["schedule_date"]),
                                st.session_state.user["role"],
                                st.session_state.user.get("industry", ""),
                                st.session_state.user.get("interests", "")
                            )
                            if success:
                                delete_draft(row["id"])
                                st.success("Draft published as a post! ✅")
                                st.rerun()
                            else:
                                st.error("❌ Failed to publish draft. Check logs.")
                    with colB:
                        if st.button("🗑️ Delete", key=f"delete_card_{row['id']}"):
                            delete_draft(row["id"])
                            st.warning("Draft deleted!")
                            st.rerun()




st.divider()
st.caption("Tip: Set your GEMINI_API_KEY in a .env file to enable free AI generation. If not, a simple fallback template will be used.")
