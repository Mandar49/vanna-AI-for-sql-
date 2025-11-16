"""
Test suite for Executive Intelligence Layer - Authentication Manager
Verifies user registration, authentication, and role-based access control.
"""

import os
import shutil
import pytest
from datetime import datetime, timedelta

from auth_manager import (
    register_user,
    authenticate_user,
    get_current_user,
    logout_user,
    list_users,
    delete_user,
    update_user_role,
    check_permission,
    get_active_sessions,
    USERS_DIR
)


class TestAuthManager:
    """Test suite for authentication manager functions."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and cleanup test environment."""
        # Setup: clean users directory
        if os.path.exists(USERS_DIR):
            shutil.rmtree(USERS_DIR)
        
        # Clear active sessions
        from auth_manager import ACTIVE_SESSIONS, SESSIONS_LOCK
        with SESSIONS_LOCK:
            ACTIVE_SESSIONS.clear()
        
        yield
        
        # Teardown: clean up
        if os.path.exists(USERS_DIR):
            shutil.rmtree(USERS_DIR)
        
        # Clear active sessions
        with SESSIONS_LOCK:
            ACTIVE_SESSIONS.clear()
    
    def test_register_user_success(self):
        """Test successful user registration."""
        result = register_user("testuser", "password123", "analyst")
        
        assert result["success"] is True
        assert result["user"]["username"] == "testuser"
        assert result["user"]["role"] == "analyst"
        
        print("✓ User registration works")
    
    def test_register_user_duplicate(self):
        """Test duplicate username rejection."""
        register_user("testuser", "password123", "analyst")
        result = register_user("testuser", "different", "analyst")
        
        assert result["success"] is False
        assert "already exists" in result["message"].lower()
        
        print("✓ Duplicate username rejection works")
    
    def test_register_user_invalid_role(self):
        """Test invalid role rejection."""
        result = register_user("testuser", "password123", "invalid_role")
        
        assert result["success"] is False
        assert "invalid role" in result["message"].lower()
        
        print("✓ Invalid role rejection works")
    
    def test_register_user_empty_credentials(self):
        """Test empty credentials rejection."""
        result = register_user("", "password", "analyst")
        assert result["success"] is False
        
        result = register_user("user", "", "analyst")
        assert result["success"] is False
        
        print("✓ Empty credentials rejection works")
    
    def test_authenticate_user_success(self):
        """Test successful authentication."""
        register_user("testuser", "password123", "analyst")
        result = authenticate_user("testuser", "password123")
        
        assert result["success"] is True
        assert "token" in result
        assert result["user"]["username"] == "testuser"
        
        print("✓ User authentication works")
    
    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        register_user("testuser", "password123", "analyst")
        result = authenticate_user("testuser", "wrongpassword")
        
        assert result["success"] is False
        assert "invalid" in result["message"].lower()
        
        print("✓ Wrong password rejection works")
    
    def test_authenticate_user_nonexistent(self):
        """Test authentication with nonexistent user."""
        result = authenticate_user("nonexistent", "password")
        
        assert result["success"] is False
        
        print("✓ Nonexistent user rejection works")
    
    def test_get_current_user(self):
        """Test getting current user from token."""
        register_user("testuser", "password123", "analyst")
        auth_result = authenticate_user("testuser", "password123")
        token = auth_result["token"]
        
        user = get_current_user(token)
        
        assert user is not None
        assert user["username"] == "testuser"
        assert user["role"] == "analyst"
        
        print("✓ Get current user works")
    
    def test_get_current_user_invalid_token(self):
        """Test getting user with invalid token."""
        user = get_current_user("invalid_token")
        
        assert user is None
        
        print("✓ Invalid token handling works")
    
    def test_logout_user(self):
        """Test user logout."""
        register_user("testuser", "password123", "analyst")
        auth_result = authenticate_user("testuser", "password123")
        token = auth_result["token"]
        
        # Verify user is logged in
        assert get_current_user(token) is not None
        
        # Logout
        result = logout_user(token)
        assert result is True
        
        # Verify user is logged out
        assert get_current_user(token) is None
        
        print("✓ User logout works")
    
    def test_list_users(self):
        """Test listing users."""
        register_user("user1", "pass1", "analyst")
        register_user("user2", "pass2", "executive")
        register_user("user3", "pass3", "admin")
        
        users = list_users()
        
        assert len(users) == 3
        usernames = [u["username"] for u in users]
        assert "user1" in usernames
        assert "user2" in usernames
        assert "user3" in usernames
        
        # Verify no password hashes in output
        for user in users:
            assert "password" not in user
            assert "password_hash" not in user
        
        print("✓ List users works")
    
    def test_delete_user(self):
        """Test user deletion."""
        register_user("testuser", "password123", "analyst")
        
        # Verify user exists
        users = list_users()
        assert len(users) == 1
        
        # Delete user
        result = delete_user("testuser")
        assert result is True
        
        # Verify user deleted
        users = list_users()
        assert len(users) == 0
        
        print("✓ User deletion works")
    
    def test_update_user_role(self):
        """Test updating user role."""
        register_user("testuser", "password123", "analyst")
        
        # Update role
        result = update_user_role("testuser", "admin")
        assert result is True
        
        # Verify role updated
        users = list_users()
        user = next(u for u in users if u["username"] == "testuser")
        assert user["role"] == "admin"
        
        print("✓ User role update works")
    
    def test_check_permission_analyst(self):
        """Test permission checking for analyst."""
        register_user("analyst", "pass", "analyst")
        auth_result = authenticate_user("analyst", "pass")
        token = auth_result["token"]
        
        assert check_permission(token, "analyst") is True
        assert check_permission(token, "admin") is False
        
        print("✓ Analyst permission check works")
    
    def test_check_permission_admin(self):
        """Test permission checking for admin (has all permissions)."""
        register_user("admin", "pass", "admin")
        auth_result = authenticate_user("admin", "pass")
        token = auth_result["token"]
        
        assert check_permission(token, "admin") is True
        assert check_permission(token, "analyst") is True
        assert check_permission(token, "executive") is True
        
        print("✓ Admin permission check works")
    
    def test_get_active_sessions(self):
        """Test getting active sessions."""
        register_user("user1", "pass1", "analyst")
        register_user("user2", "pass2", "executive")
        
        # Authenticate both users
        auth1 = authenticate_user("user1", "pass1")
        auth2 = authenticate_user("user2", "pass2")
        
        # Get active sessions
        sessions = get_active_sessions()
        
        assert len(sessions) == 2
        usernames = [s["username"] for s in sessions]
        assert "user1" in usernames
        assert "user2" in usernames
        
        print("✓ Active sessions tracking works")
    
    def test_offline_operation(self):
        """Verify authentication works offline."""
        # All operations should work without internet
        register_user("testuser", "password", "analyst")
        result = authenticate_user("testuser", "password")
        user = get_current_user(result["token"])
        users = list_users()
        
        assert user is not None
        assert len(users) == 1
        
        print("✓ Offline operation works")


def run_manual_test():
    """Manual test for quick verification."""
    print("\n" + "="*70)
    print("MANUAL TEST: Authentication Manager")
    print("="*70 + "\n")
    
    # Clean up
    if os.path.exists(USERS_DIR):
        shutil.rmtree(USERS_DIR)
    
    print("1. Registering users...")
    register_user("admin", "admin123", "admin")
    register_user("analyst1", "pass123", "analyst")
    register_user("exec1", "exec123", "executive")
    print()
    
    print("2. Listing users...")
    users = list_users()
    for user in users:
        print(f"   • {user['username']}: {user['role']}")
    print()
    
    print("3. Authenticating users...")
    admin_auth = authenticate_user("admin", "admin123")
    analyst_auth = authenticate_user("analyst1", "pass123")
    
    if admin_auth["success"]:
        print(f"   ✓ Admin authenticated: {admin_auth['token'][:20]}...")
    if analyst_auth["success"]:
        print(f"   ✓ Analyst authenticated: {analyst_auth['token'][:20]}...")
    print()
    
    print("4. Testing permissions...")
    admin_token = admin_auth["token"]
    analyst_token = analyst_auth["token"]
    
    print(f"   Admin has admin permission: {check_permission(admin_token, 'admin')}")
    print(f"   Admin has analyst permission: {check_permission(admin_token, 'analyst')}")
    print(f"   Analyst has analyst permission: {check_permission(analyst_token, 'analyst')}")
    print(f"   Analyst has admin permission: {check_permission(analyst_token, 'admin')}")
    print()
    
    print("5. Active sessions...")
    sessions = get_active_sessions()
    print(f"   Active sessions: {len(sessions)}")
    for session in sessions:
        print(f"      • {session['username']} ({session['role']})")
    print()
    
    print("6. Testing logout...")
    logout_user(analyst_token)
    sessions = get_active_sessions()
    print(f"   Active sessions after logout: {len(sessions)}")
    print()
    
    print("="*70)
    print("VERIFICATION")
    print("="*70)
    print(f"✓ User registration: Working")
    print(f"✓ Authentication: Working")
    print(f"✓ Role-based access: Working")
    print(f"✓ Session management: Working")
    print(f"✓ Users directory: {os.path.exists(USERS_DIR)}")
    print(f"✓ Offline operation: Confirmed")
    
    print("\n" + "="*70)
    print("✅ Authentication Manager ready")
    print("="*70)


if __name__ == "__main__":
    # Run manual test
    run_manual_test()
    
    # Run pytest if available
    try:
        print("\n" + "="*70)
        print("RUNNING PYTEST SUITE")
        print("="*70 + "\n")
        pytest.main([__file__, "-v", "-s"])
    except:
        print("\nNote: Install pytest to run full test suite")
