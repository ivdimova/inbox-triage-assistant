"""Gmail IMAP client for fetching and managing emails."""

import imaplib
import email
from email.header import decode_header
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()


@dataclass
class EmailMessage:
    """Represents an email message with relevant metadata."""
    uid: str
    subject: str
    sender: str
    date: datetime
    body_preview: str
    has_attachments: bool


class GmailClient:
    """Gmail IMAP client for authentication and email operations."""
    
    def __init__(self, email_address: Optional[str] = None, 
                 app_password: Optional[str] = None):
        self.email_address = email_address or os.getenv("GMAIL_EMAIL")
        self.app_password = app_password or os.getenv("GMAIL_APP_PASSWORD")
        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.imap_port = int(os.getenv("IMAP_PORT", "993"))
        self.connection: Optional[imaplib.IMAP4_SSL] = None
        
        if not self.email_address or not self.app_password:
            raise ValueError("Gmail credentials not provided")
    
    def connect(self) -> None:
        """Establish IMAP connection and authenticate."""
        try:
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.email_address, self.app_password)
            self.connection.select("INBOX")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Gmail: {e}")
    
    def disconnect(self) -> None:
        """Close IMAP connection."""
        if self.connection:
            self.connection.close()
            self.connection.logout()
    
    def fetch_recent_emails(self, count: int = 200) -> List[EmailMessage]:
        """Fetch the most recent emails from inbox."""
        if not self.connection:
            raise RuntimeError("Not connected to Gmail")
        
        try:
            print(f"Searching for emails in inbox...")
            # Set a longer timeout for Vercel
            self.connection.sock.settimeout(60)
            # Search for all emails in inbox
            _, message_numbers = self.connection.search(None, "ALL")
            message_list = message_numbers[0].split()
            
            print(f"Found {len(message_list)} total emails")
            
            # Get the most recent emails
            recent_messages = message_list[-count:] if len(message_list) > count else message_list
            print(f"Processing {len(recent_messages)} recent emails...")
            
            emails = []
            for i, num in enumerate(reversed(recent_messages)):  # Most recent first
                if i % 25 == 0:  # Progress update every 25 emails
                    print(f"Processed {i}/{len(recent_messages)} emails...")
                
                # Fetch with lighter payload for speed
                _, data = self.connection.fetch(num, "(BODY.PEEK[HEADER] BODY.PEEK[TEXT])")
                if not data or not data[0]:
                    continue
                    
                email_body = data[0][1] if isinstance(data[0], tuple) else data[0]
                if not email_body:
                    continue
                    
                email_message = email.message_from_bytes(email_body)
                
                # Extract email details
                subject = self._decode_header(email_message.get("Subject", ""))
                sender = self._decode_header(email_message.get("From", ""))
                date_str = email_message.get("Date", "")
                date_obj = email.utils.parsedate_to_datetime(date_str) if date_str else datetime.now()
                
                # Get body preview
                body_preview = self._extract_body_preview(email_message)
                has_attachments = self._has_attachments(email_message)
                
                emails.append(EmailMessage(
                    uid=num.decode(),
                    subject=subject,
                    sender=sender,
                    date=date_obj,
                    body_preview=body_preview,
                    has_attachments=has_attachments
                ))
            
            return emails
            
        except Exception as e:
            raise RuntimeError(f"Failed to fetch emails: {e}")
    
    def archive_emails(self, email_uids: List[str]) -> None:
        """Archive emails by moving them to the All Mail folder."""
        if not self.connection:
            raise RuntimeError("Not connected to Gmail")
        
        try:
            for uid in email_uids:
                # Add the archived label and remove from inbox
                self.connection.store(uid, "+X-GM-LABELS", "\\Important")
                self.connection.store(uid, "+FLAGS", "\\Deleted")
            
            # Expunge to actually move the emails
            self.connection.expunge()
            
        except Exception as e:
            raise RuntimeError(f"Failed to archive emails: {e}")
    
    def _decode_header(self, header: str) -> str:
        """Decode email header that might be encoded."""
        if not header:
            return ""
        
        decoded_parts = decode_header(header)
        decoded_string = ""
        
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_string += part.decode(encoding or "utf-8", errors="ignore")
            else:
                decoded_string += part
        
        return decoded_string
    
    def _extract_body_preview(self, email_message: email.message.Message) -> str:
        """Extract a preview of the email body."""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                        break
                    except:
                        continue
        else:
            try:
                body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")
            except:
                body = str(email_message.get_payload())
        
        # Return first 200 characters as preview
        return body[:200].strip() if body else ""
    
    def _has_attachments(self, email_message: email.message.Message) -> bool:
        """Check if email has attachments."""
        for part in email_message.walk():
            if part.get_content_disposition() == "attachment":
                return True
        return False