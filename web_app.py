"""
WEB APP - Your Personal Assistant in the Browser!
Now with AI Chat, Reminders, Finance, and Email!
from flask import Flask, render_template_string, request, jsonify
"""

from flask import Flask, render_template_string, request, jsonify
from reminder_system import ReminderSystem
from finance_tracker import FinanceTracker
from email_helper import EmailHelper
from ai_chat_bot import AIChatBot
from database import Database
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'my-assistant-secret-key-change-me')

# Initialize database
db = Database()

# Initialize your tools with database
reminders = ReminderSystem(database=db)
finance = FinanceTracker(database=db)
email_helper = EmailHelper()
ai_bot = AIChatBot()
