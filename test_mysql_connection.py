import mysql.connector

# Update these details before running
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "8750014282Hk@",
    "database": "linkedin_ai"
}

try:
    conn = mysql.connector.connect(**DB_CONFIG)
    if conn.is_connected():
        print("✅ Successfully connected to MySQL database:", DB_CONFIG["database"])
    conn.close()
except mysql.connector.Error as err:
    print("❌ MySQL connection failed:", err)
#1f77b4