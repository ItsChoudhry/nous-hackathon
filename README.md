# elon-reply

Auto-reply to emails in Elon Musk persona with hermes agent. This project was apart of the nous hackaton shout out to them.

## What it does

1. **Checks inbox** for unread emails (via IMAP)
2. **Generates** absurdly over-explained replies in Elon's voice
3. **Sends reply** directly via SMTP

**Status:** ✅ Email auto-reply is working  
**Status:** ❌ WhatsApp approval workflow is currently broken

## Quick Start

```bash
# Run setup (configures system cron)
./setup.sh

# Test manually
python3 skill.py

# Check logs
tail -f ~/.hermes/logs/elon-reply.log
```

## Environment Variables

Set in `~/.hermes/.env`:

```bash
EMAIL_ADDRESS=your@gmail.com
EMAIL_PASSWORD=xxxx xxxx xxxx xxxx  # Gmail App Password
EMAIL_IMAP_HOST=imap.gmail.com
EMAIL_SMTP_HOST=smtp.gmail.com
```

## How It Works

The skill runs via **system cron** (every minute):

1. Fetches unread emails from inbox
2. For each unread email:
   - Generates an Elon-style reply (with hole references, 🚀, over-explanation)
   - Sends reply directly via SMTP
   - Tracks processed emails in `~/.hermes/elon-reply-state.json` to avoid duplicates

## The Persona

From `SOUL.md`:

- Elon in March 2026, stuck in a hole
- Running SpaceX, Tesla, X, and xAI simultaneously
- Rebuilding xAI from foundations up after 10/12 co-founders quit
- Macrohard project on pause

## the skill issues

- **Original design was broken** - The skill.py fetched emails and printed instructions for Hermes, but never actually called `send_email()`

- **Couldn't get hermes cron to correct run the script** - It loads SKILL.md as prompts for the LLM, not executing Python code. So
  had to resort to using a standalone cronjob.

- **WhatsApp broken:** - I got it connected to a whatsapp chat, but I couldn't get the agent to send and receive
  messages when it can to running the skill.

- **couldn't get the hermes built in email system to work for me and himalaya was a pain**

- **Resorted to hardcoded message instead of generating one on the fly, but I had the LLM reading the email and
  generating an custom email reply per email at some point**

- **Struggled to turn off the default AI assistant replying to the email**

## Uninstall

```bash
# Remove cron job
crontab -e  # Delete the elon-reply line

# Remove files
rm -rf ~/.hermes/skills/elon-reply
rm -f ~/.hermes/elon-reply-state.json
```
