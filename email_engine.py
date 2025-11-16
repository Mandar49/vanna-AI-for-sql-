"""
Executive Intelligence Layer - Email & Alert Engine (Phase 5B)
Offline-safe email drafting with optional live sending via SMTP.
Supports attachments and priority-based notifications.
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import threading

# Storage
OUTBOX_DIR = "./outbox"
EMAILS_FILE = os.path.join(OUTBOX_DIR, "emails.json")
NOTIFICATIONS_FILE = os.path.join(OUTBOX_DIR, "notifications.json")

# Thread-safe locks
OUTBOX_LOCK = threading.Lock()
NOTIFICATIONS_LOCK = threading.Lock()

# SMTP Configuration (optional - set via environment or config)
SMTP_CONFIG = {
    "enabled": False,  # Set to True to enable live sending
    "host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "port": int(os.getenv("SMTP_PORT", "587")),
    "username": os.getenv("SMTP_USERNAME", ""),
    "password": os.getenv("SMTP_PASSWORD", ""),
    "from_email": os.getenv("SMTP_FROM", "")
}


def _ensure_outbox_dir():
    """Ensure outbox directory exists."""
    Path(OUTBOX_DIR).mkdir(parents=True, exist_ok=True)


def _load_emails() -> List[Dict[str, Any]]:
    """Load emails from outbox."""
    _ensure_outbox_dir()
    
    if not os.path.exists(EMAILS_FILE):
        return []
    
    try:
        with open(EMAILS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_emails(emails: List[Dict[str, Any]]):
    """Save emails to outbox."""
    _ensure_outbox_dir()
    
    with open(EMAILS_FILE, 'w', encoding='utf-8') as f:
        json.dump(emails, f, indent=2)


def _load_notifications() -> List[Dict[str, Any]]:
    """Load notifications from file."""
    _ensure_outbox_dir()
    
    if not os.path.exists(NOTIFICATIONS_FILE):
        return []
    
    try:
        with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def _save_notifications(notifications: List[Dict[str, Any]]):
    """Save notifications to file."""
    _ensure_outbox_dir()
    
    with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(notifications, f, indent=2)


def send_email(
    to: str,
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Send email or save as draft if offline.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body (plain text or HTML)
        attachments: List of file paths to attach
        priority: Email priority (low, normal, high)
        
    Returns:
        Result dictionary with status
        
    Example:
        result = send_email(
            "user@example.com",
            "Daily Report",
            "Please find attached the daily report.",
            attachments=["./reports/daily_report.pdf"]
        )
    """
    email_data = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
        "to": to,
        "subject": subject,
        "body": body,
        "attachments": attachments or [],
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "status": "draft",
        "sent_at": None
    }
    
    # Try to send if SMTP is configured
    if SMTP_CONFIG["enabled"] and SMTP_CONFIG["username"] and SMTP_CONFIG["password"]:
        try:
            result = _send_via_smtp(to, subject, body, attachments, priority)
            if result["success"]:
                email_data["status"] = "sent"
                email_data["sent_at"] = datetime.now().isoformat()
                print(f"✓ Email sent to {to}: {subject}")
                return {
                    "success": True,
                    "message": f"Email sent to {to}",
                    "email_id": email_data["id"],
                    "mode": "live"
                }
        except Exception as e:
            print(f"⚠ SMTP send failed: {e}. Saving as draft.")
    
    # Save as draft (offline mode or SMTP failed)
    with OUTBOX_LOCK:
        emails = _load_emails()
        emails.append(email_data)
        _save_emails(emails)
    
    print(f"✓ Email saved as draft: {subject}")
    
    return {
        "success": True,
        "message": f"Email saved as draft (offline mode)",
        "email_id": email_data["id"],
        "mode": "offline"
    }


def _send_via_smtp(
    to: str,
    subject: str,
    body: str,
    attachments: Optional[List[str]] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """Send email via SMTP."""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = SMTP_CONFIG["from_email"] or SMTP_CONFIG["username"]
        msg['To'] = to
        msg['Subject'] = subject
        
        # Set priority
        if priority == "high":
            msg['X-Priority'] = '1'
            msg['Importance'] = 'high'
        elif priority == "low":
            msg['X-Priority'] = '5'
            msg['Importance'] = 'low'
        
        # Attach body
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach files
        if attachments:
            for file_path in attachments:
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(file_path)}'
                        )
                        msg.attach(part)
        
        # Send email
        with smtplib.SMTP(SMTP_CONFIG["host"], SMTP_CONFIG["port"]) as server:
            server.starttls()
            server.login(SMTP_CONFIG["username"], SMTP_CONFIG["password"])
            server.send_message(msg)
        
        return {"success": True}
        
    except Exception as e:
        return {"success": False, "error": str(e)}


def save_draft(to: str, subject: str, body: str, attachments: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Save email as draft without attempting to send.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body
        attachments: List of file paths to attach
        
    Returns:
        Result dictionary with draft ID
        
    Example:
        result = save_draft(
            "user@example.com",
            "Draft Report",
            "This is a draft email."
        )
    """
    draft_data = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
        "to": to,
        "subject": subject,
        "body": body,
        "attachments": attachments or [],
        "priority": "normal",
        "created_at": datetime.now().isoformat(),
        "status": "draft",
        "sent_at": None
    }
    
    with OUTBOX_LOCK:
        emails = _load_emails()
        emails.append(draft_data)
        _save_emails(emails)
    
    print(f"✓ Draft saved: {subject}")
    
    return {
        "success": True,
        "message": "Draft saved",
        "draft_id": draft_data["id"]
    }


def notify_user(user: str, message: str, priority: str = "normal") -> Dict[str, Any]:
    """
    Send notification to user.
    
    Args:
        user: Username or email
        message: Notification message
        priority: Priority level (low, normal, high, urgent)
        
    Returns:
        Result dictionary with notification ID
        
    Example:
        result = notify_user(
            "admin",
            "Daily report generation completed",
            priority="normal"
        )
    """
    notification_data = {
        "id": datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
        "user": user,
        "message": message,
        "priority": priority,
        "created_at": datetime.now().isoformat(),
        "read": False
    }
    
    with NOTIFICATIONS_LOCK:
        notifications = _load_notifications()
        notifications.append(notification_data)
        _save_notifications(notifications)
    
    # Print notification based on priority
    priority_icon = {
        "low": "ℹ️",
        "normal": "📢",
        "high": "⚠️",
        "urgent": "🚨"
    }.get(priority, "📢")
    
    print(f"{priority_icon} Notification for {user}: {message}")
    
    return {
        "success": True,
        "message": "Notification sent",
        "notification_id": notification_data["id"]
    }


def get_outbox(status: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get emails from outbox.
    
    Args:
        status: Filter by status (draft, sent, failed)
        limit: Maximum number of emails to return
        
    Returns:
        List of email dictionaries
        
    Example:
        drafts = get_outbox(status="draft")
        all_emails = get_outbox(limit=100)
    """
    with OUTBOX_LOCK:
        emails = _load_emails()
    
    if status:
        emails = [e for e in emails if e.get("status") == status]
    
    # Sort by created_at (newest first)
    emails.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return emails[:limit]


def get_notifications(user: Optional[str] = None, unread_only: bool = False, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Get notifications.
    
    Args:
        user: Filter by user
        unread_only: Only return unread notifications
        limit: Maximum number of notifications to return
        
    Returns:
        List of notification dictionaries
        
    Example:
        unread = get_notifications(user="admin", unread_only=True)
        all_notifs = get_notifications(limit=100)
    """
    with NOTIFICATIONS_LOCK:
        notifications = _load_notifications()
    
    if user:
        notifications = [n for n in notifications if n.get("user") == user]
    
    if unread_only:
        notifications = [n for n in notifications if not n.get("read", False)]
    
    # Sort by created_at (newest first)
    notifications.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    return notifications[:limit]


def mark_notification_read(notification_id: str) -> bool:
    """
    Mark notification as read.
    
    Args:
        notification_id: Notification ID
        
    Returns:
        True if successful
        
    Example:
        if mark_notification_read(notif_id):
            print("Marked as read")
    """
    with NOTIFICATIONS_LOCK:
        notifications = _load_notifications()
        
        for notif in notifications:
            if notif.get("id") == notification_id:
                notif["read"] = True
                _save_notifications(notifications)
                return True
        
        return False


def configure_smtp(host: str, port: int, username: str, password: str, from_email: Optional[str] = None):
    """
    Configure SMTP settings for live email sending.
    
    Args:
        host: SMTP server host
        port: SMTP server port
        username: SMTP username
        password: SMTP password
        from_email: From email address (optional, defaults to username)
        
    Example:
        configure_smtp(
            "smtp.gmail.com",
            587,
            "user@gmail.com",
            "app_password"
        )
    """
    SMTP_CONFIG["enabled"] = True
    SMTP_CONFIG["host"] = host
    SMTP_CONFIG["port"] = port
    SMTP_CONFIG["username"] = username
    SMTP_CONFIG["password"] = password
    SMTP_CONFIG["from_email"] = from_email or username
    
    print(f"✓ SMTP configured: {host}:{port}")


def get_smtp_status() -> Dict[str, Any]:
    """
    Get SMTP configuration status.
    
    Returns:
        Dictionary with SMTP status
        
    Example:
        status = get_smtp_status()
        if status["enabled"]:
            print("Live sending enabled")
    """
    return {
        "enabled": SMTP_CONFIG["enabled"],
        "host": SMTP_CONFIG["host"],
        "port": SMTP_CONFIG["port"],
        "configured": bool(SMTP_CONFIG["username"] and SMTP_CONFIG["password"])
    }


if __name__ == "__main__":
    print("="*70)
    print("EMAIL & ALERT ENGINE TEST")
    print("="*70)
    print()
    
    # Test 1: Save draft
    print("1. Saving email draft...")
    result = save_draft(
        "user@example.com",
        "Test Report",
        "This is a test email with a report attached.",
        attachments=["./reports/test_report.pdf"]
    )
    print(f"   Draft ID: {result['draft_id']}")
    print()
    
    # Test 2: Send email (offline mode)
    print("2. Sending email (offline mode)...")
    result = send_email(
        "executive@example.com",
        "Daily Summary",
        "Please find the daily summary attached.",
        priority="high"
    )
    print(f"   Mode: {result['mode']}")
    print()
    
    # Test 3: Send notification
    print("3. Sending notifications...")
    notify_user("admin", "System backup completed", priority="normal")
    notify_user("executive", "Quarterly report ready", priority="high")
    notify_user("analyst", "Data refresh complete", priority="low")
    print()
    
    # Test 4: Get outbox
    print("4. Checking outbox...")
    emails = get_outbox()
    print(f"   Total emails: {len(emails)}")
    print(f"   Drafts: {len(get_outbox(status='draft'))}")
    print()
    
    # Test 5: Get notifications
    print("5. Checking notifications...")
    notifications = get_notifications()
    print(f"   Total notifications: {len(notifications)}")
    print(f"   Unread: {len(get_notifications(unread_only=True))}")
    print()
    
    # Test 6: SMTP status
    print("6. SMTP status...")
    status = get_smtp_status()
    print(f"   Enabled: {status['enabled']}")
    print(f"   Configured: {status['configured']}")
    print()
    
    print("="*70)
    print("✅ Email & Alert Engine ready")
    print("="*70)
