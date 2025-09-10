# Demo Script (10–12 minutes) – LinkedIn Personal Branding AI Agent

> Goal: Showcase a fully functional MVP for generating, scheduling, and managing LinkedIn posts, with user authentication, profile management, drafts, analytics, and  **PDF export**.

## 0. Setup (30s)
- Open terminal: `streamlit run app.py`
- Mention: "This MVP is beginner-friendly, built using Streamlit, MySQL, and Gemini AI (optional for content generation)."

## 1. Authentication (60s)
- Highlight Login / Signup:
    - Secure authentication using hashed passwords.

    - Users can create accounts with name, email, and password.

    - Existing users log in to access their profile, posts, drafts, and analytics.

- Mention: "session state ensures only logged-in users can see the main app."


## 2. Problem & Solution (60s)
- Problem: Busy professionals struggle to post consistently with a strong personal brand.
- Solution: This agent generates posts automatically, allows scheduling, stores drafts, tracks engagement, and exports posts to PDF.

## 3. Tech Overview (60–90s)
- Frontend: **Streamlit** with polished UI and sidebar navigation.
- Backend/DB: **SQLite** via `database.py`
- AI: **Gemini AI** API for post generation (optional fallback template included if no API key is provided).
- PDF Export: Generates downloadable PDFs for posts.
- Authentication: Secure hashed passwords with registration/login system.

## 4. Live Walkthrough (6–7 min)

1. **Login / Signup**:
   - Create a new account or log in.
   - Show profile photo preview, name, role in sidebar.
   - Explain role-based access and session handling.
2. **Profile Management**: 
   - Edit profile details (name, role, industry, interests).
   - Upload profile picture (circular avatar, auto-processed).
   - Changes immediately reflected in sidebar.
3. **Generate Post**: 
   - Fill in post details (role, industry, interests).
   -  Generate content automatically via AI or fallback template.
   - Copy, clear, and word/character count features available.
4. **Drafts**:
   - Save posts as drafts with optional schedule dates.
   - View all drafts in “Drafts” tab.
   - Delete or publish drafts to posts.    
5. **Post & Calendar Tab**:
   - Show saved posts with scheduled dates.
   - Simulated engagement: likes and comments..
   - xport posts individually to **PDF** for sharing or record.
6. ****Analytics**:
   - Sidebar displays total posts, drafts, likes, comments.
   - Users can track engagement trends.
7. **Dark Theme** :
   - Clean, modern dark look for the entire app.
   - UI elements like buttons, tabs, sidebar text are styled for dark mode.
   - No light theme option; all components adapt to dark styling.


## 5. Architecture Slide (60–90s)
- User → Streamlit UI → MySQL → (Gemini AI) → Posts & Drafts → PDF Export
- Decisions: beginner-friendly, no external API dependency required for core demo, simple database CRUD.

## 5. What’s Next (60s)
- Integration with LinkedIn API for direct posting.
- Monthly content calendar view and analytics charts.
- Trend-based hashtag suggestions and performance tracking.
- Multi-user support with roles and permissions.

## 6. Close (30s)
- Reiterate: This MVP fulfills the brief for LinkedIn personal branding.
- Ready to show on LinkedIn, in portfolio, or for entry-level job interviews.
- Highlight polish, usability, and backend integration as key strengths.


