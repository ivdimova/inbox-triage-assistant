"""Demo data generator for testing without Gmail access."""

from datetime import datetime, timedelta
from typing import List
import random

from .gmail_client import EmailMessage


def generate_demo_emails(count: int = 200) -> List[EmailMessage]:
    """Generate realistic demo email data for testing."""
    
    # Sample email templates
    email_templates = [
        # Marketing/Newsletter emails
        {
            "senders": ["newsletters@medium.com", "digest@substack.com", "updates@techcrunch.com"],
            "subjects": ["This Week in Tech", "Weekly Newsletter", "Daily Digest", "Top Stories"],
            "previews": ["Here are the top tech stories this week...", "Your weekly dose of industry news...", "Breaking: New developments in AI..."]
        },
        # GitHub notifications
        {
            "senders": ["notifications@github.com", "noreply@github.com"],
            "subjects": ["[user/repo] Pull request merged", "[user/repo] New issue opened", "[user/repo] CI/CD failed"],
            "previews": ["Your pull request has been merged...", "A new issue was opened in your repository...", "The build failed for commit..."]
        },
        # Work/Team communications
        {
            "senders": ["slack@company.com", "notifications@teams.microsoft.com", "calendar@company.com"],
            "subjects": ["Meeting Reminder", "Team Standup Notes", "Project Update", "Daily Sync"],
            "previews": ["Don't forget about today's meeting...", "Here are the notes from our standup...", "The project is progressing well..."]
        },
        # Financial/Banking
        {
            "senders": ["alerts@chase.com", "notifications@paypal.com", "statements@amex.com"],
            "subjects": ["Account Alert", "Transaction Notification", "Monthly Statement", "Payment Received"],
            "previews": ["Your account balance has changed...", "You received a payment...", "Your monthly statement is ready..."]
        },
        # Social media
        {
            "senders": ["notify@linkedin.com", "no-reply@twitter.com", "notifications@facebook.com"],
            "subjects": ["You have new connections", "Weekly job matches", "Friend tagged you", "New follower"],
            "previews": ["You have 5 new connection requests...", "Here are jobs that match your profile...", "Someone mentioned you in a post..."]
        },
        # E-commerce
        {
            "senders": ["orders@amazon.com", "shipping@fedex.com", "deals@bestbuy.com"],
            "subjects": ["Order Confirmation", "Package Delivered", "Flash Sale Alert", "Return Processed"],
            "previews": ["Your order has been confirmed...", "Your package was delivered...", "Limited time offer on electronics..."]
        },
        # Personal emails
        {
            "senders": ["john.doe@gmail.com", "sarah.smith@yahoo.com", "mike.johnson@outlook.com"],
            "subjects": ["Weekend Plans", "Birthday Party Invitation", "Catch up soon?", "Quick Question"],
            "previews": ["Hey, what are you doing this weekend?", "You're invited to my birthday party...", "We should catch up soon..."]
        }
    ]
    
    emails = []
    base_date = datetime.now()
    
    for i in range(count):
        # Pick random template
        template = random.choice(email_templates)
        
        # Generate email data
        sender = random.choice(template["senders"])
        subject = random.choice(template["subjects"])
        preview = random.choice(template["previews"])
        
        # Add some variation to subjects
        if random.random() < 0.3:
            subject = f"Re: {subject}"
        
        # Generate realistic date (last 30 days)
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        email_date = base_date - timedelta(days=days_ago, hours=hours_ago)
        
        email = EmailMessage(
            uid=str(i + 1),
            subject=subject,
            sender=sender,
            date=email_date,
            body_preview=preview,
            has_attachments=random.random() < 0.2  # 20% have attachments
        )
        
        emails.append(email)
    
    # Sort by date (newest first)
    emails.sort(key=lambda x: x.date, reverse=True)
    
    return emails