
# database.py

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash
import base64
from PIL import Image, ImageOps, ImageDraw
import io

import io
import base64

# ---------- Helper for Profile Picture ----------
def process_profile_pic(uploaded_file):
    """Convert uploaded image to circular avatar, resize, and return as base64 string."""
    img = Image.open(uploaded_file).convert("RGBA")

    # Resize to max 200x200 to keep DB small
    img.thumbnail((200, 200))

    # Make square
    size = min(img.size)
    img = ImageOps.fit(img, (size, size), centering=(0.5, 0.5))

    # Create circular mask
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)

    # Apply mask
    img.putalpha(mask)

    # Save to buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


# ---------- Database Config ----------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",                     # 🔑 Your MySQL username
    "password": "8750014282Hk@",        # 🔑 Your MySQL password
    "database": "linkedin_ai"           # 🔑 Your database name
}

# ---------- Init DB ----------
# ---------- Init DB ----------
def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'member',
                industry VARCHAR(100),
                interests TEXT,
                profile_pic LONGTEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Posts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                role VARCHAR(100),
                industry VARCHAR(100),
                interests TEXT,
                content TEXT,
                hashtags TEXT,
                schedule_date DATE,
                likes INT DEFAULT 0,
                comments INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # ✅ Drafts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drafts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                content TEXT,
                hashtags TEXT,
                schedule_date DATE DEFAULT (CURRENT_DATE),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        cursor.close()
        conn.close()
        print("✅ Database initialized successfully")
    except Error as e:
        print("❌ Error initializing database:", e)


# ---------- User Management ----------
# def register_user(name, email, password, role="member"):
#     try:
#         conn = mysql.connector.connect(**DB_CONFIG)
#         cursor = conn.cursor()
#         # Hash password
#         hashed_pw = generate_password_hash(password)
#         # Insert user
#         cursor.execute(

#             "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
#             (name, email, hashed_pw, role),
#         )
#         conn.commit()
#         cursor.close()
#         conn.close()
#         return True
#     except Error as e:
#         print("❌ Error registering user:", e)
#         return False


# def login_user(email, password):
#     try:
#         conn = mysql.connector.connect(**DB_CONFIG)
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
#         user = cursor.fetchone()
#         cursor.close()
#         conn.close()


#         if user and check_password_hash(user["password_hash"], password):
#             return user  # dict with id, name, email, role
#         return None
#     except Error as e:
#         print("❌ Error logging in:", e)
#         return None


# ---------------- AUTH FUNCTIONS ----------------

def register_user(name, email, password, role="member"):
    """Register a new user with hashed password. Returns True on success, False if email exists or error."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # ✅ Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"⚠️ Email '{email}' already registered.")
            cursor.close()
            conn.close()
            return False

        # Hash password
        hashed_pw = generate_password_hash(password)

        # Insert user
        cursor.execute(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (name, email, hashed_pw, role),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print("❌ Error registering user:", e)
        return False


def login_user(email, password):
    """Login a user by checking hashed password. Returns user dict or None."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        # Check hashed password
        if user and check_password_hash(user["password_hash"], password):
            return user  # dict with id, name, email, role, etc.
        return None
    except Error as e:
        print("❌ Error logging in:", e)
        return None

















# ---------- Posts ----------
def add_post(user_id, content, hashtags, schedule_date, role, industry, interests):
    """Insert a new post into DB (skip if content is blank)."""
    try:
        # 🔒 Prevent blank/empty posts
        if not content or not content.strip():
            print("⚠️ Empty post skipped (not saved).")
            return False

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        sql = """
        INSERT INTO posts (user_id, content, hashtags, schedule_date, role, industry, interests)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (user_id, content, hashtags, schedule_date, role, industry, interests))
        conn.commit()

        cursor.close()
        conn.close()
        return True
    except Error as e:
        print("❌ Error inserting post:", e)
        return False



def get_posts(user_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM posts WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Error as e:
        print("❌ Error fetching posts:", e)
        return []
    
# -----delete function
def delete_post(post_id, user_id):
    """Delete a post by its ID (only if it belongs to the user)."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM posts WHERE id = %s AND user_id = %s", (post_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print("❌ Error deleting post:", e)
        return False

#---------Profile---------------------------------
# ---------- User Profile Management ----------

def get_user(user_id):
    """Fetch a single user by ID"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Error as e:
        print("❌ Error fetching user:", e)
        return None


def update_user(user_id, name=None, role=None, industry=None, interests=None, profile_pic=None): 
    """Update user fields dynamically, ensuring no NULL values are stored"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        fields, values = [], []

        if name is not None:
            fields.append("name = %s")
            values.append(name or "")   # replace None with empty string
        if role is not None:
            fields.append("role = %s")
            values.append(role or "member")  # default role = "member"
        if industry is not None:
            fields.append("industry = %s")
            values.append(industry or "") 
        if interests is not None:
            fields.append("interests = %s")
            values.append(interests or "") 
        if profile_pic is not None:
            fields.append("profile_pic = %s")
            values.append(profile_pic)

        if fields:
            sql = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
            values.append(user_id)
            cursor.execute(sql, tuple(values))
            conn.commit()

        cursor.close()
        conn.close()
        return True
    except Error as e:
        print("❌ Error updating user:", e)
        return False

# ✅ Add the new draft-related functions here
# ---------- Drafts ----------
def add_draft(user_id, content, hashtags, schedule_date=None):
    """Save a draft post with safe default date."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # ✅ Ensure schedule_date is not None
        if not schedule_date or schedule_date in ["", None, "None"]:
            from datetime import date
            schedule_date = date.today().strftime("%Y-%m-%d")

        cursor.execute(
            """
            INSERT INTO drafts (user_id, content, hashtags, schedule_date)
            VALUES (%s, %s, %s, %s)
            """,
            (user_id, content, hashtags, schedule_date),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print("❌ Error inserting draft:", e)
        return False

def get_drafts(user_id):
    """Fetch all drafts for a given user"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM drafts WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        drafts = cursor.fetchall()

        cursor.close()
        conn.close()
        return drafts
    except Error as e:
        print("❌ Error fetching drafts:", e)
        return []
    
def delete_draft(draft_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM drafts WHERE id = %s", (draft_id,))
        conn.commit()
        print(f"🗑️ Draft {draft_id} deleted")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print("❌ Error deleting draft:", e)
        return False

# ----------Side Bar Analytics ----------
def get_user_stats(user_id):
    """Return total posts, total drafts, and engagement (likes, comments) for a user."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)

        # 🔹 Total posts
        cursor.execute("SELECT COUNT(*) AS total_posts FROM posts WHERE user_id = %s", (user_id,))
        total_posts = cursor.fetchone()["total_posts"]

        # 🔹 Total drafts
        cursor.execute("SELECT COUNT(*) AS total_drafts FROM drafts WHERE user_id = %s", (user_id,))
        total_drafts = cursor.fetchone()["total_drafts"]

        # 🔹 Total likes & comments across all posts
        cursor.execute("""
            SELECT COALESCE(SUM(likes), 0) AS total_likes,
                   COALESCE(SUM(comments), 0) AS total_comments
            FROM posts WHERE user_id = %s
        """, (user_id,))
        engagement = cursor.fetchone()

        cursor.close()
        conn.close()

        return {
            "posts": total_posts,
            "drafts": total_drafts,
            "likes": engagement["total_likes"],
            "comments": engagement["total_comments"],
        }
    except Error as e:
        print("❌ Error fetching user stats:", e)
        return {"posts": 0, "drafts": 0, "likes": 0, "comments": 0}