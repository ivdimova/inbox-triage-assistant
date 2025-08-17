"""Vercel serverless function entry point."""

import sys
import os

# Add src to path so we can import our modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from inbox_triage.web_app import app

# This is the WSGI app that Vercel will use
app = app