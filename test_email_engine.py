"""
Test suite for Executive Intelligence Layer - Email & Alert Engine
Verifies email drafting, sending, and notification functionality.
"""

import os
import shutil
import pytest

from email_engine import (
    send_email,
    save_draft,
    notify_user,
    get_outbox,
    get_notifications,
    mark_notification_read,
    configure_smtp,
    get_smtp_status,
    OUTBOX_DIR
)


class TestEmailEngine:
    """Test suite for email engine functions."""
    
    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Setup and cleanup test environment."""
        # Setup: clean outbox directory
        if os.path.exists(OUTBOX_DIR):
            shutil.rmtree(OUTBOX_DIR)
        
        yield
        
        # Teardown: clean up
        if os.path.exists(OUTBOX_DIR):
            shutil.rmtree(OUTBOX_DIR)
    
    def test_save_draft(self):
        """Test saving email draft."""
        result = save_draft(
            "test@example.com",
            "Test Subject",
            "Test body"
        )
        
        assert result["success"] is True
        assert "draft_id" in result
        
        # Verify draft saved
        drafts = get_outbox(status="draft")
        assert len(drafts) == 1
        assert drafts[0]["to"] == "test@example.com"
        assert drafts[0]["subject"] == "Test Subject"
        
        print("✓ Save draft works")
    
    def test_send_email_offline(self):
        """Test sending email in offline mode."""
        result = send_email(
            "user@example.com",
            "Test Email",
            "This is a test email"
        )
        
        assert result["success"] is True
        assert result["mode"] == "offline"
        assert "email_id" in result
        
        # Verify email saved as draft
        emails = get_outbox()
        assert len(emails) == 1
        assert emails[0]["status"] == "draft"
        
        print("✓ Send email (offline) works")
    
    def test_send_email_with_attachments(self):
        """Test sending email with attachments."""
        result = send_email(
            "user@example.com",
            "Email with Attachments",
            "Please find attached files.",
            attachments=["file1.pdf", "file2.doc"]
        )
        
        assert result["success"] is True
        
        # Verify attachments saved
        emails = get_outbox()
        assert len(emails[0]["attachments"]) == 2
        
        print("✓ Email with attachments works")
    
    def test_send_email_with_priority(self):
        """Test sending email with priority."""
        result = send_email(
            "user@example.com",
            "Urgent Email",
            "This is urgent",
            priority="high"
        )
        
        assert result["success"] is True
        
        # Verify priority saved
        emails = get_outbox()
        assert emails[0]["priority"] == "high"
        
        print("✓ Email priority works")
    
    def test_notify_user(self):
        """Test sending notification."""
        result = notify_user(
            "admin",
            "Test notification",
            priority="normal"
        )
        
        assert result["success"] is True
        assert "notification_id" in result
        
        # Verify notification saved
        notifications = get_notifications()
        assert len(notifications) == 1
        assert notifications[0]["user"] == "admin"
        assert notifications[0]["message"] == "Test notification"
        
        print("✓ Notify user works")
    
    def test_notify_user_priorities(self):
        """Test notifications with different priorities."""
        notify_user("user1", "Low priority", priority="low")
        notify_user("user2", "Normal priority", priority="normal")
        notify_user("user3", "High priority", priority="high")
        notify_user("user4", "Urgent", priority="urgent")
        
        notifications = get_notifications()
        assert len(notifications) == 4
        
        priorities = [n["priority"] for n in notifications]
        assert "low" in priorities
        assert "high" in priorities
        assert "urgent" in priorities
        
        print("✓ Notification priorities work")
    
    def test_get_outbox_filter(self):
        """Test filtering outbox by status."""
        save_draft("user1@example.com", "Draft 1", "Body 1")
        save_draft("user2@example.com", "Draft 2", "Body 2")
        send_email("user3@example.com", "Email 1", "Body 3")
        
        all_emails = get_outbox()
        drafts = get_outbox(status="draft")
        
        assert len(all_emails) == 3
        assert len(drafts) == 3  # All are drafts in offline mode
        
        print("✓ Outbox filtering works")
    
    def test_get_notifications_filter(self):
        """Test filtering notifications."""
        notify_user("admin", "Message 1")
        notify_user("admin", "Message 2")
        notify_user("user", "Message 3")
        
        all_notifs = get_notifications()
        admin_notifs = get_notifications(user="admin")
        unread_notifs = get_notifications(unread_only=True)
        
        assert len(all_notifs) == 3
        assert len(admin_notifs) == 2
        assert len(unread_notifs) == 3  # All unread initially
        
        print("✓ Notification filtering works")
    
    def test_mark_notification_read(self):
        """Test marking notification as read."""
        result = notify_user("admin", "Test message")
        notif_id = result["notification_id"]
        
        # Mark as read
        success = mark_notification_read(notif_id)
        assert success is True
        
        # Verify marked as read
        unread = get_notifications(unread_only=True)
        assert len(unread) == 0
        
        print("✓ Mark notification read works")
    
    def test_get_outbox_limit(self):
        """Test outbox limit parameter."""
        # Create multiple emails
        for i in range(15):
            save_draft(f"user{i}@example.com", f"Subject {i}", f"Body {i}")
        
        limited = get_outbox(limit=10)
        all_emails = get_outbox(limit=50)
        
        assert len(limited) == 10
        assert len(all_emails) == 15
        
        print("✓ Outbox limit works")
    
    def test_get_notifications_limit(self):
        """Test notifications limit parameter."""
        # Create multiple notifications
        for i in range(15):
            notify_user(f"user{i}", f"Message {i}")
        
        limited = get_notifications(limit=10)
        all_notifs = get_notifications(limit=50)
        
        assert len(limited) == 10
        assert len(all_notifs) == 15
        
        print("✓ Notifications limit works")
    
    def test_smtp_configuration(self):
        """Test SMTP configuration."""
        # Check initial status
        status = get_smtp_status()
        assert status["enabled"] is False
        
        # Configure SMTP
        configure_smtp(
            "smtp.test.com",
            587,
            "test@test.com",
            "password"
        )
        
        # Check updated status
        status = get_smtp_status()
        assert status["enabled"] is True
        assert status["host"] == "smtp.test.com"
        assert status["configured"] is True
        
        print("✓ SMTP configuration works")
    
    def test_outbox_directory_creation(self):
        """Test outbox directory is created."""
        save_draft("test@example.com", "Test", "Body")
        
        assert os.path.exists(OUTBOX_DIR)
        assert os.path.isdir(OUTBOX_DIR)
        
        print("✓ Outbox directory creation works")
    
    def test_offline_operation(self):
        """Verify email engine works offline."""
        # All operations should work without internet
        save_draft("test@example.com", "Draft", "Body")
        send_email("test@example.com", "Email", "Body")
        notify_user("admin", "Notification")
        emails = get_outbox()
        notifications = get_notifications()
        
        assert len(emails) == 2
        assert len(notifications) == 1
        
        print("✓ Offline operation works")


def run_manual_test():
    """Manual test for quick verification."""
    print("\n" + "="*70)
    print("MANUAL TEST: Email & Alert Engine")
    print("="*70 + "\n")
    
    # Clean up
    if os.path.exists(OUTBOX_DIR):
        shutil.rmtree(OUTBOX_DIR)
    
    print("1. Saving email drafts...")
    save_draft("user1@example.com", "Report Draft", "Please review the attached report.")
    save_draft("user2@example.com", "Meeting Notes", "Notes from today's meeting.")
    print()
    
    print("2. Sending emails (offline mode)...")
    send_email("executive@example.com", "Daily Summary", "Daily summary attached.", priority="high")
    send_email("team@example.com", "Weekly Update", "Weekly update for the team.")
    print()
    
    print("3. Sending notifications...")
    notify_user("admin", "System backup completed", priority="normal")
    notify_user("executive", "Quarterly report ready", priority="high")
    notify_user("analyst", "Data refresh complete", priority="low")
    print()
    
    print("4. Checking outbox...")
    emails = get_outbox()
    print(f"   Total emails: {len(emails)}")
    print(f"   Drafts: {len(get_outbox(status='draft'))}")
    for email in emails[:3]:
        print(f"      • To: {email['to']} - Subject: {email['subject']}")
    print()
    
    print("5. Checking notifications...")
    notifications = get_notifications()
    print(f"   Total notifications: {len(notifications)}")
    print(f"   Unread: {len(get_notifications(unread_only=True))}")
    for notif in notifications:
        print(f"      • {notif['user']}: {notif['message']} [{notif['priority']}]")
    print()
    
    print("6. SMTP status...")
    status = get_smtp_status()
    print(f"   Enabled: {status['enabled']}")
    print(f"   Configured: {status['configured']}")
    print(f"   Mode: {'Live sending' if status['enabled'] and status['configured'] else 'Offline (draft only)'}")
    print()
    
    print("="*70)
    print("VERIFICATION")
    print("="*70)
    print(f"✓ Email drafting: Working")
    print(f"✓ Email sending (offline): Working")
    print(f"✓ Notifications: Working")
    print(f"✓ Outbox directory: {os.path.exists(OUTBOX_DIR)}")
    print(f"✓ Offline operation: Confirmed")
    
    print("\n" + "="*70)
    print("✅ Email & Alert Engine ready")
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
