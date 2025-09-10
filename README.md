# LinkedIn Personal Branding AI Agent 🤖

**Generate, schedule, and export LinkedIn posts effortlessly with AI.**  
Perfect for building your personal brand, tracking engagement, and planning content—all in one beginner-friendly MVP.

---

## 🌟 Features

- **User Authentication:** Login & Signup with secure password hashing.
- **Profile Management:** Upload circular profile pictures, set role, industry, interests.
- **AI-Powered Post Generation:** Generate LinkedIn posts using Gemini API (or fallback template if API not set).
- **Content Calendar:** Schedule posts, view upcoming posts.
- **Draft System:** Save, edit, delete drafts before publishing.
- **Export to PDF:** Save posts locally as PDF for sharing or demo.
- **Simulated Engagement Analytics:** Likes and comments counters for each post.
- **Sidebar Dashboard:**
  - Profile picture, name, role
  - Total posts, drafts, likes, comments
  - Quick links to generate content, drafts, analytics
- **Dark/Light Mode Toggle** for UI personalization.
- **Clean Streamlit UI** with responsive design and intuitive layout.

---

## 🛠 Tech Stack

- **Frontend:** Streamlit (UI & sidebar)
- **Backend:** Python, MySQL
- **Database:** MySQL (`users`, `posts`, `drafts`)
- **Authentication:** werkzeug password hashing
- **AI Integration:** Gemini API (or fallback template)
- **File Handling:** PDF export, base64 profile picture encoding
- **Extras:** CSS for theming, dark mode support, hover effects, rounded avatars

---

## ⚡ Quick Start

1. **Clone Repo & Install Dependencies**
```bash
git clone <your-repo-url>
cd linkedin-ai-agent
pip install -r requirements.txt

```

2. **Configure Database**

    Update database.py with your MySQL credentials.

    Run init_db() once to create tables (users, posts, drafts).

3. **Optional AI Integration**

Add .env file with:
```bash
GEMINI_API_KEY=your_api_key_here

```
4. **Run Streamlit App**
```bash
streamlit run app.py


5. **Usage**

- Signup or login.

- Complete your profile.

- Generate posts, save drafts, schedule, and export to PDF.

- Track engagement in sidebar analytics.




























































































































































































































































<!-- # LinkedIn Personal Branding AI Agent (Beginner MVP)

A beginner-friendly MVP that generates LinkedIn posts, schedules them locally, and exports each post to **PDF** for submission/demo.
Built with **Streamlit + SQLite**, optional **OpenAI** integration.

## Features
- Profile-based post generation (uses OpenAI if API key present; otherwise a clean fallback template)
- Content calendar (stored in `posts.db`)
- One-click **Export to PDF**
- Simulated analytics (likes/comments) for demo

## Quick Start

1. **Create a virtual env** (recommended) and install deps:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI (optional)**: create a `.env` file with
   ```
   OPENAI_API_KEY=your_key_here
   ```

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

4. Fill your profile on the left → Generate Post → Save → Export to PDF.

## Files
- `app.py` – Streamlit UI + PDF export
- `database.py` – SQLite helpers
- `requirements.txt` – dependencies
- `DEMO_SCRIPT.md` – suggested 10-min demo flow

## Notes
- If you do not have an OpenAI key, the app uses a solid fallback template so you can still demo.
- This MVP intentionally **simulates** posting/analytics to keep setup easy for beginners.


# ---------- Sidebar --------
user_id = st.session_state.user["id"]
user_data = get_user(user_id)

with st.sidebar:
    st.markdown("## 🌟 Profile")

    # --- Profile Picture ---
    if user_data and user_data.get("profile_pic"):
        try:
            img_data = base64.b64decode(user_data["profile_pic"] + "===")  # fix padding
            st.image(img_data, width=120)
        except Exception:
            st.warning("⚠️ Could not load profile picture.")
    else:
        st.image("https://i.imgur.com/5cLDeaR.png", width=120)  # fallback avatar

    # --- User Info Card ---
    st.markdown(
        f"""
        <div style='text-align:center; padding:10px;'>
            <h3 style='margin-bottom:5px;'>{user_data.get("name", "Guest")}</h3>
            <p style='margin:0; color:gray; font-size:14px;'>{user_data.get("role", "Member")}</p>
            <p style='margin:0; font-size:13px; color:#1f77b4;'>🚀 AI Branding Agent</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    # --- Quick Links ---
    st.markdown("### 📌 Quick Links")
    st.markdown("📝 Generate Content")
    st.markdown("📅 Content Calendar & PDF Export")
    st.markdown("📊 Analytics")
    st.markdown("🗂 Drafts")
    st.markdown("👤 Profile")

    st.markdown("---")

    # --- Theme Toggle ---
    dark_mode = st.toggle("🌙 Dark Mode")

    if dark_mode:
        # --- Dark Theme ---
        st.markdown(
            """
            <style>
            .stApp { background-color: #0e1117; color: white; }
            .stButton>button { background:#1f77b4; color:white; border-radius:8px; }
            .stTabs [data-baseweb="tab"] { color:white; font-weight:500; }
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        # --- Light Theme ---
        st.markdown(
            """
            <style>
            .stApp { background-color: #ffffff; color: black; }
            .stButton>button { background:#1f77b4; color:white; border-radius:8px; }
            .stTabs [data-baseweb="tab"] { color:black; font-weight:500; }
            </style>
            """,
            unsafe_allow_html=True
        )

    # --- Footer ---
    st.markdown(
        "<p style='text-align:center; font-size:12px; color:gray;'>Made with ❤️ using Streamlit + Gemini AI</p>",
        unsafe_allow_html=True
    )
 -->
