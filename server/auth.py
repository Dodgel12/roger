"""
Authentication and authorization module for Roger API.
Implements simple token-based authentication with user isolation.
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Tuple
from database import get_db_connection, init_core_skills

# In production, use a strong secret key from environment
AUTH_SECRET = os.getenv("AUTH_SECRET", "change-this-in-production-use-strong-key")
TOKEN_EXPIRY_HOURS = 24 * 30  # 30 days


def generate_token() -> str:
    """Generate a secure random authentication token."""
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    """Hash a token for storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def create_user(username: str, password: str) -> Tuple[bool, str, Optional[str]]:
    """
    Create a new user account.
    Returns: (success, message, token)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        return False, "Username already exists", None

    # Hash password
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Create user
    cursor.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    # Get the new user ID
    user_id = cursor.lastrowid

    # Generate and store token
    token = generate_token()
    token_hash = hash_token(token)
    expiry = (datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO auth_tokens (user_id, token_hash, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (user_id, token_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), expiry)
    )

    conn.commit()
    conn.close()

    # Initialize core skills for new user
    init_core_skills(user_id)

    return True, "User created successfully", token


def authenticate_user(username: str, password: str) -> Tuple[bool, str, Optional[str]]:
    """
    Authenticate a user with username and password.
    Returns: (success, message, token)
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Find user
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash)
    )
    user = cursor.fetchone()

    if not user:
        conn.close()
        return False, "Invalid username or password", None

    user_id = user["id"]

    # Generate new token
    token = generate_token()
    token_hash = hash_token(token)
    expiry = (datetime.now() + timedelta(hours=TOKEN_EXPIRY_HOURS)).strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO auth_tokens (user_id, token_hash, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (user_id, token_hash, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), expiry)
    )

    conn.commit()
    conn.close()

    return True, "Authentication successful", token


def verify_token(token: str) -> Tuple[bool, Optional[int]]:
    """
    Verify a token and return the user_id if valid.
    Returns: (is_valid, user_id)
    """
    if not token:
        return False, None

    token_hash = hash_token(token)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id FROM auth_tokens 
        WHERE token_hash = ? AND expires_at > datetime('now')
        """,
        (token_hash,)
    )
    result = cursor.fetchone()
    conn.close()

    if result:
        return True, result["user_id"]
    return False, None


def revoke_token(token: str) -> bool:
    """Revoke a token (logout)."""
    token_hash = hash_token(token)
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM auth_tokens WHERE token_hash = ?",
        (token_hash,)
    )

    conn.commit()
    conn.close()

    return cursor.rowcount > 0


def extract_token_from_header(auth_header: str) -> Optional[str]:
    """Extract bearer token from Authorization header."""
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None
