#!/bin/bash
# Setup script for elon-reply skill
# This version runs skill.py via system cron (more reliable)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="elon-reply"

echo "Setting up elon-reply skill..."

# Create logs directory
mkdir -p ~/.hermes/logs

# Create or update skill directory in Hermes
mkdir -p ~/.hermes/skills/$SKILL_NAME

# Symlink skill files
ln -sf "$SCRIPT_DIR/SOUL.md" ~/.hermes/skills/$SKILL_NAME/
ln -sf "$SCRIPT_DIR/SKILL.md" ~/.hermes/skills/$SKILL_NAME/
ln -sf "$SCRIPT_DIR/skill.py" ~/.hermes/skills/$SKILL_NAME/

echo "✓ Symlinked skill files to ~/.hermes/skills/$SKILL_NAME/"

# Remove any Hermes cron jobs for this skill
echo ""
echo "Cleaning up old Hermes cron job (if any)..."
hermes cron remove "$SKILL_NAME" 2>/dev/null || true

# Setup system cron job to run the Python script directly
echo ""
echo "Setting up system cron job..."

# Create a wrapper script
WRAPPER="$SCRIPT_DIR/elon-reply-cron.sh"
cat > "$WRAPPER" << EOF
#!/bin/bash
cd "$SCRIPT_DIR"
python3 skill.py >> ~/.hermes/logs/elon-reply.log 2>&1
EOF
chmod +x "$WRAPPER"

# Add to crontab (runs every minute)
CRON_ENTRY="* * * * * $WRAPPER"

# Check if already in crontab
if crontab -l 2>/dev/null | grep -q "elon-reply-cron.sh"; then
    echo "✓ Cron job already exists"
else
    (crontab -l 2>/dev/null; echo "$CRON_ENTRY") | crontab -
    echo "✓ Added cron job: runs every minute"
fi

echo ""
echo "========================================"
echo "Setup complete!"
echo "========================================"
echo ""
echo "Make sure these are set in ~/.hermes/.env:"
echo "  EMAIL_ADDRESS=your@gmail.com"
echo "  EMAIL_PASSWORD=your-app-password"
echo "  EMAIL_IMAP_HOST=imap.gmail.com"
echo "  EMAIL_SMTP_HOST=smtp.gmail.com"
echo ""
echo "Note: Use an App Password for Gmail, not your regular password."
echo ""
echo "To check logs: tail -f ~/.hermes/logs/elon-reply.log"