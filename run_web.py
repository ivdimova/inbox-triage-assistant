"""Simple script to run the web application."""

from src.inbox_triage.web_app import app

if __name__ == "__main__":
    print("🚀 Starting Gmail Inbox Triage Web Interface...")
    print("📱 Open http://localhost:3000 in your browser")
    print("🔑 Make sure you have your Gmail app password ready")
    app.run(debug=True, port=3000, host="0.0.0.0")