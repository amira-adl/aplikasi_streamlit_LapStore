# auth.py
import bcrypt
from database import get_connection, create_user_table

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and verify_password(password, row[0]):
        return True
    return False

def register_user(username, password):
    create_user_table()
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, hash_password(password)))  # ✅ Ganti kolom jadi 'password'
        conn.commit()
        return True
    except:
        return False  # Username sudah ada
    finally:
        conn.close()
