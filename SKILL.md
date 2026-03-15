---
name: elon-reply
description: Auto-reply to emails in Elon Musk persona (email working, WhatsApp broken)
version: 1.1.0
author: community
license: MIT
metadata:
  hermes:
    tags: [email, whatsapp, automation, elon]
    homepage: https://github.com/itsChoudhry/elon-reply
prerequisites:
  tools: [email]
  environment: [EMAIL_ADDRESS, EMAIL_PASSWORD]
skills:
  - elon-reply
triggers:
  - type: manual
    run: "python3 skill.py"
  - type: cron
    schedule: "every 1m"
    run: "python3 skill.py"
---

# elon-reply Skill

Automatically checks your inbox and sends Elon-style replies to unread emails.

## Status

- ✅ **Email:** Working - sends replies directly via SMTP
- ❌ **WhatsApp:** Broken - was meant for approval workflow but never implemented properly

## Usage

### Manual

```bash
python3 skill.py
```

### Automatic (cron)

The `setup.sh` script configures a system cron job that runs every minute.

```bash
./setup.sh
```

## Configuration

Required in `~/.hermes/.env`:

```
EMAIL_ADDRESS=your@gmail.com
EMAIL_PASSWORD=your-gmail-app-password
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_SMTP_HOST=smtp.gmail.com
```

## How It Works

1. Cron runs `skill.py` every minute
2. Connects to Gmail via IMAP
3. Fetches all unread emails
4. Generates Elon-style reply for each (with hole, 🚀, over-explanation)
5. Sends reply via SMTP
6. Tracks processed email UIDs to avoid duplicates

## Files

- `SOUL.md` - Elon persona definition
- `skill.py` - Main logic (standalone Python script)
- `SKILL.md` - This manifest
- `setup.sh` - Cron setup

## Lessons Learned

The original design had Hermes loading SKILL.md as prompts, which never actually executed the email sending code. Fixed by:
1. Making skill.py a standalone executable script
2. Using system cron instead of Hermes cron
3. Actually calling send_email() instead of just printing instructions
