# Gmail Inbox Triage Assistant

Quickly cluster your last 200 Gmail emails into actionable groups with one-click archive functionality.

## Quick Setup

1. **Install and setup**:
   ```bash
   cd inbox-triage
   uv sync
   ```

2. **Configure Gmail credentials**:
   ```bash
   cp .env.example .env
   # Edit .env with your Gmail email and app password
   ```

3. **Get Gmail App Password**:
   - Go to Google Account settings
   - Enable 2FA if not already enabled
   - Generate an "App Password" for this application
   - Use the app password (not your regular Gmail password)

## Usage

```bash
# Basic usage (uses credentials from .env)
uv run inbox-triage triage

# Or specify credentials directly
uv run inbox-triage triage --email your@gmail.com --password your_app_password

# Customize clustering
uv run inbox-triage triage --clusters 7 --count 100
```

## Features

- 🔐 **Secure Gmail IMAP authentication**
- 📊 **Smart email clustering** using ML and heuristics
- 📧 **Process last 200 emails** (configurable)
- 🏷️ **Descriptive cluster names** (e.g., "Marketing & Newsletters", "Code Repository Updates")
- 🗂️ **One-click archive** entire clusters
- 🎨 **Rich CLI interface** with tables and colors