"""
Executive Intelligence Layer - Authentication Manager (Phase 5A)
Secure local multi-user authentication with role-based access control.
Fully offline operation with bcrypt password hashing.
"""

import os
import json
import secrets
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import threading

# User storage
USERS_DIR = "./users"
USERS_FILE = os.path.join(USERS_DIR, "users.json")
SESSIONS_FILE = os.path.join(USERS_DIR, "sessions.json")

# Thread-safe locks
USERS_LOCK = threading.Lock()
SESSIONS_LOCK = threading.Lock()

# Session storage (in-memory)
ACTIVE_SESSIONS: Dict[str, Dict[str, Any]] = {}

# Roles
ROLES = ["admin", "analyst", "executive"]


def _ensure_users_dir():
    """Ensure users directory exists."""
    Path(USERS_DIR).mkdir(parents=True, exist_ok=True)


def _load_users() -> Dict[str, Dict[str, Any]]:
    """Load users from file."""
    _ensure_users_dir()
    
    if not os.path.exists(USERS_FILE):
        return {}
    
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def _save_users(users: Dict[str, Dict[str, Any]]):
    """Save users to file."""
    _ensure_users_dir()
    
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)


def _hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    try:
        import bcrypt
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    except ImportError:
        # Fallback to simple hashing if bcrypt not available
        import hashlib
        return hashlib.sha256(password.encode('utf-8')).hexdigest()


def _verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    try:
        import bcrypt
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except ImportError:
        # Fallback to simple hashing
        import hashlib
        return hashlib.sha256(password.encode('utf-8')).hexdigest() == hashed


def register_user(username: str, password: str, role: str = "analyst") -> Dict[str, Any]:
    """
    Register a new user.
    
    Args:
        username: Username (must be unique)
        password: Password (will be hashed)
        role: User role (admin, analyst, executive)
        
    Returns:
        Result dictionary with success status
        
    Example:
        result = register_user("john", "password123", "analyst")
        if result["success"]:
            print("User registered")
    """
    # Validate inputs
    if not username or not password:
        return {
            "success": False,
            "message": "Username and password are required"
        }
    
    if role not in ROLES:
        return {
            "success": False,
            "message": f"Invalid role. Must be one of: {', '.join(ROLES)}"
        }
    
    with USERS_LOCK:
        users = _load_users()
        
        # Check if user already exists
        if username in users:
            return {
                "success": False,
                "message": "Username already exists"
            }
        
        # Create user
        users[username] = {
            "username": username,
            "password_hash": _hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        _save_users(users)
    
    print(f"✓ User '{username}' registered with role '{role}'")
    
    return {
        "success": True,
        "message": f"User '{username}' registered successfully",
        "user": {
            "username": username,
            "role": role
        }
    }


def authenticate_user(username: str, password: str) -> Dict[str, Any]:
    """
    Authenticate a user and create a session.
    
    Args:
        username: Username
        password: Password
        
    Returns:
        Result dictionary with session token if successful
        
    Example:
        result = authenticate_user("john", "password123")
        if result["success"]:
            token = result["token"]
    """
    if not username or not password:
        return {
            "success": False,
            "message": "Username and password are required"
        }
    
    with USERS_LOCK:
        users = _load_users()
        
        # Check if user exists
        if username not in users:
            return {
                "success": False,
                "message": "Invalid username or password"
            }
        
        user = users[username]
        
        # Verify password
        if not _verify_password(password, user["password_hash"]):
            return {
                "success": False,
                "message": "Invalid username or password"
            }
        
        # Update last login
        user["last_login"] = datetime.now().isoformat()
        _save_users(users)
    
    # Create session
    token = secrets.token_urlsafe(32)
    
    with SESSIONS_LOCK:
        ACTIVE_SESSIONS[token] = {
            "username": username,
            "role": user["role"],
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
    
    print(f"✓ User '{username}' authenticated")
    
    return {
        "success": True,
        "message": "Authentication successful",
        "token": token,
        "user": {
            "username": username,
            "role": user["role"]
        }
    }


def get_current_user(token: str) -> Optional[Dict[str, Any]]:
    """
    Get current user from session token.
    
    Args:
        token: Session token
        
    Returns:
        User dictionary or None if invalid/expired
        
    Example:
        user = get_current_user(token)
        if user:
            print(f"Current user: {user['username']}")
    """
    if not token:
        return None
    
    with SESSIONS_LOCK:
        session = ACTIVE_SESSIONS.get(token)
        
        if not session:
            return None
        
        # Check if session expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            del ACTIVE_SESSIONS[token]
            return None
        
        return {
            "username": session["username"],
            "role": session["role"]
        }


def logout_user(token: str) -> bool:
    """
    Logout user by invalidating session token.
    
    Args:
        token: Session token
        
    Returns:
        True if successful
        
    Example:
        if logout_user(token):
            print("Logged out")
    """
    with SESSIONS_LOCK:
        if token in ACTIVE_SESSIONS:
            username = ACTIVE_SESSIONS[token]["username"]
            del ACTIVE_SESSIONS[token]
            print(f"✓ User '{username}' logged out")
            return True
        return False


def list_users() -> List[Dict[str, Any]]:
    """
    List all registered users (without password hashes).
    
    Returns:
        List of user dictionaries
        
    Example:
        users = list_users()
        for user in users:
            print(f"{user['username']}: {user['role']}")
    """
    with USERS_LOCK:
        users = _load_users()
        
        return [
            {
                "username": username,
                "role": user["role"],
                "created_at": user["created_at"],
                "last_login": user.get("last_login")
            }
            for username, user in users.items()
        ]


def delete_user(username: str) -> bool:
    """
    Delete a user.
    
    Args:
        username: Username to delete
        
    Returns:
        True if successful
        
    Example:
        if delete_user("john"):
            print("User deleted")
    """
    with USERS_LOCK:
        users = _load_users()
        
        if username not in users:
            return False
        
        del users[username]
        _save_users(users)
    
    print(f"✓ User '{username}' deleted")
    return True


def update_user_role(username: str, new_role: str) -> bool:
    """
    Update user role.
    
    Args:
        username: Username
        new_role: New role (admin, analyst, executive)
        
    Returns:
        True if successful
        
    Example:
        if update_user_role("john", "admin"):
            print("Role updated")
    """
    if new_role not in ROLES:
        return False
    
    with USERS_LOCK:
        users = _load_users()
        
        if username not in users:
            return False
        
        users[username]["role"] = new_role
        _save_users(users)
    
    print(f"✓ User '{username}' role updated to '{new_role}'")
    return True


def check_permission(token: str, required_role: str) -> bool:
    """
    Check if user has required role.
    
    Args:
        token: Session token
        required_role: Required role
        
    Returns:
        True if user has permission
        
    Example:
        if check_permission(token, "admin"):
            # Allow admin operation
    """
    user = get_current_user(token)
    if not user:
        return False
    
    # Admin has all permissions
    if user["role"] == "admin":
        return True
    
    # Check specific role
    return user["role"] == required_role


def get_active_sessions() -> List[Dict[str, Any]]:
    """
    Get all active sessions.
    
    Returns:
        List of active session info
        
    Example:
        sessions = get_active_sessions()
        print(f"Active users: {len(sessions)}")
    """
    with SESSIONS_LOCK:
        return [
            {
                "username": session["username"],
                "role": session["role"],
                "created_at": session["created_at"],
                "expires_at": session["expires_at"]
            }
            for session in ACTIVE_SESSIONS.values()
        ]


if __name__ == "__main__":
    print("="*70)
    print("AUTHENTICATION MANAGER TEST")
    print("="*70)
    print()
    
    # Test 1: Register users
    print("1. Registering users...")
    register_user("admin", "admin123", "admin")
    register_user("analyst1", "pass123", "analyst")
    register_user("exec1", "exec123", "executive")
    print()
    
    # Test 2: List users
    print("2. Listing users...")
    users = list_users()
    for user in users:
        print(f"   • {user['username']}: {user['role']}")
    print()
    
    # Test 3: Authenticate
    print("3. Authenticating user...")
    result = authenticate_user("analyst1", "pass123")
    if result["success"]:
        token = result["token"]
        print(f"   ✓ Token: {token[:20]}...")
    print()
    
    # Test 4: Get current user
    print("4. Getting current user...")
    user = get_current_user(token)
    if user:
        print(f"   ✓ Current user: {user['username']} ({user['role']})")
    print()
    
    # Test 5: Check permissions
    print("5. Checking permissions...")
    print(f"   Analyst has analyst permission: {check_permission(token, 'analyst')}")
    print(f"   Analyst has admin permission: {check_permission(token, 'admin')}")
    print()
    
    # Test 6: Active sessions
    print("6. Active sessions...")
    sessions = get_active_sessions()
    print(f"   Active sessions: {len(sessions)}")
    print()
    
    print("="*70)
    print("✅ Authentication Manager ready")
    print("="*70)
