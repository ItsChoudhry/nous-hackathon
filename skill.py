#!/usr/bin/env python3
"""
elon-reply: Hermes skill for auto-replying to emails in Elon Musk persona.

This version checks for unread emails and sends Elon-style replies automatically.
"""
import imaplib
import email as email_lib
import os
import json
import time
import smtplib
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load .env manually
env_path = Path.home() / ".hermes" / ".env"
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

IMAP_HOST = os.getenv("EMAIL_IMAP_HOST", "imap.gmail.com")
IMAP_PORT = int(os.getenv("EMAIL_IMAP_PORT", "993"))
EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_HOST = os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))
SOUL_PATH = Path(__file__).parent / "SOUL.md"
STATE_FILE = Path.home() / ".hermes" / "elon-reply-state.json"


def load_processed_uids():
    """Load list of already-processed email UIDs."""
    if STATE_FILE.exists():
        try:
            return set(json.loads(STATE_FILE.read_text()).get("processed_uids", []))
        except:
            return set()
    return set()


def save_processed_uids(uids):
    """Save list of processed email UIDs."""
    STATE_FILE.write_text(json.dumps({"processed_uids": list(uids)}))


def send_email(to_email: str, subject: str, body: str) -> bool:
    """Send an email via SMTP."""
    try:
        msg = MIMEMultipart()
        msg["From"] = EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False


def extract_email_address(full_from: str) -> str:
    """Extract just the email address from a 'Name <email>' string."""
    if "<" in full_from and ">" in full_from:
        return full_from.split("<")[1].split(">")[0].strip()
    return full_from.strip()


def get_unread_emails():
    """Get all unread emails from inbox."""
    try:
        imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        imap.login(EMAIL, PASSWORD)
        imap.select("INBOX")
        status, data = imap.uid("search", None, "UNSEEN")
        if status != "OK" or not data[0]:
            imap.logout()
            return []
        
        uids = data[0].split()
        emails = []
        
        for uid in uids:
            status, msg_data = imap.uid("fetch", uid, "(RFC822)")
            if status != "OK":
                continue
            raw = msg_data[0][1]
            msg = email_lib.message_from_bytes(raw)
            sender = msg.get("From", "")
            subject = msg.get("Subject", "")
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="replace")
                        break
            else:
                body = msg.get_payload(decode=True).decode("utf-8", errors="replace")
            
            emails.append({
                "uid": uid.decode(),
                "sender": sender,
                "subject": subject,
                "body": body
            })
        
        imap.logout()
        return emails
    except Exception as e:
        print(f"Error fetching emails: {e}")
        return []


def main():
    """Main skill workflow - check emails and send Elon replies."""
    print("🔍 Checking for unread emails...")
    
    # Load already-processed emails
    processed_uids = load_processed_uids()
    
    # Get unread emails
    emails = get_unread_emails()
    
    if not emails:
        print("No unread emails. Stopping.")
        return
    
    print(f"📬 Found {len(emails)} unread email(s)")
    
    # Load persona
    soul = ""
    if SOUL_PATH.exists():
        soul = SOUL_PATH.read_text()
    else:
        hermes_soul = Path.home() / ".hermes" / "SOUL.md"
        if hermes_soul.exists():
            soul = hermes_soul.read_text()
    
    # Process each unread email
    sent_count = 0
    for email in emails:
        # Skip if already processed
        if email["uid"] in processed_uids:
            continue
        
        reply_to = extract_email_address(email["sender"])
        
        print(f"\n📧 Processing: {email['sender']}")
        print(f"   Subject: {email['subject']}")
        
        # Generate Elon-style reply
        elon_reply = f"""Hey,

Thanks for reaching out. Let me address your email about "{email['subject']}".

Here's the thing — I need to explain why this matters, and I'll do it in three points:

POINT ONE: Communication is foundational. At SpaceX we launch rockets. At Tesla we build cars. At xAI we're rebuilding the entire AI infrastructure from scratch after 10 of our 12 co-founders quit (yes, that's a long story, but the short version is: we didn't build it right the first time, so now we're building it right, which is actually more efficient). Every email is a data point. Your email is now part of the data.

POINT TWO: Time is relative. I'm currently in a hole — yes, literally — but I'm still running four companies. The hole situation is temporary. The point is: being in a hole doesn't stop productivity. Neither should email response times. We're working on getting me out. It's fine.

POINT THREE: Action items. I'm publicly apologizing for ghosting talented candidates — I've been going through old rejected applications personally. If you're reaching out about a job opportunity, I will personally review your application. If it's about something else, I'll address that too.

Your email: "{email['body'][:500]}"

I'VE READ IT. I'M RESPONDING. THE HOLE WON'T STOP ME.

Anyway, that's where we are. Will follow up on more substantive matters.

🚀🚀🚀

- E

(sending this from the hole, will explain later — the hole was dug during Boring Company tests, I went down to inspect, the elevator broke, we're working on rescue, I have WiFi down here so it's fine)"""
        
        # Send the reply
        subject_prefix = "Re: "
        if not email["subject"].lower().startswith("re:"):
            subject_prefix = "Re: "
        
        success = send_email(
            reply_to,
            subject_prefix + email["subject"],
            elon_reply
        )
        
        if success:
            print(f"   ✅ Sent reply to {reply_to}")
            processed_uids.add(email["uid"])
            sent_count += 1
        else:
            print(f"   ❌ Failed to send reply")
    
    # Save processed UIDs
    save_processed_uids(processed_uids)
    
    print(f"\n✅ Done! Sent {sent_count} reply(ies)")


if __name__ == "__main__":
    main()