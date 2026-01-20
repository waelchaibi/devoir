import sqlite3
import os
from typing import Optional, List, Dict

DATABASE_PATH = "/database/app.db"

def get_connection() -> sqlite3.Connection:
    """Get a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def create_user(username: str, password: str) -> Dict:
    """Create a new user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            'INSERT INTO users (username, password) VALUES (?, ?)',
            (username, password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {
            "id": user_id,
            "username": username,
            "password": password
        }
    except sqlite3.IntegrityError:
        raise ValueError(f"Username '{username}' already exists")
    finally:
        conn.close()

def get_user(user_id: int) -> Optional[Dict]:
    """Get a user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, password FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_all_users() -> List[Dict]:
    """Get all users."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, password FROM users')
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

def update_user(user_id: int, username: Optional[str] = None, password: Optional[str] = None) -> Optional[Dict]:
    """Update a user."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # First check if user exists
    cursor.execute('SELECT id, username, password FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return None
    
    # Use existing values if not provided
    new_username = username if username is not None else user['username']
    new_password = password if password is not None else user['password']
    
    try:
        cursor.execute(
            'UPDATE users SET username = ?, password = ? WHERE id = ?',
            (new_username, new_password, user_id)
        )
        conn.commit()
        
        return {
            "id": user_id,
            "username": new_username,
            "password": new_password
        }
    except sqlite3.IntegrityError:
        raise ValueError(f"Username '{new_username}' already exists")
    finally:
        conn.close()

def delete_user(user_id: int) -> bool:
    """Delete a user. Returns True if successful, False if user not found."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    
    deleted = cursor.rowcount > 0
    conn.close()
    
    return deleted
