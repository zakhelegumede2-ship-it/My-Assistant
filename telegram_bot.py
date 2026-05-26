"""
TELEGRAM BOT - Your Personal Assistant on Your Phone!
AI Chat, Reminders, Finance, Email & Scheduled Briefings!
"""

import os
from dotenv import load_dotenv
load_dotenv()

import telebot
from reminder_system import ReminderSystem
from finance_tracker import FinanceTracker
from email_helper import EmailHelper
from ai_chat_bot import AIChatBot
from scheduler import Scheduler
from datetime import datetime

# ============================================
# Telegram bot token is read from environment for security
# Set `TELEGRAM_BOT_TOKEN` in a `.env` file or environment variable
# ============================================
YOUR_BOT_TOKEN = ("8851664463:AAFxKJsrXtAoqKa4ztbq6G-Xctor_16_wnw")

# Initialize your bot
bot = telebot.TeleBot(YOUR_BOT_TOKEN)

# Initialize your tools
reminders = ReminderSystem()
finance = FinanceTracker()
email_helper = EmailHelper()
ai_bot = AIChatBot()

# Store user states (for multi-step operations)
user_states = {}

# Scheduler will be set up after we can send messages
scheduler = None

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Welcome message when someone starts the bot"""
    
    # Save chat ID for scheduler
    with open("telegram_chat_id.txt", "w") as f:
        f.write(str(message.chat.id))
    
    welcome_text = """
🤖 *Hello! I'm Your Personal Assistant!*

Here's what I can do:

💬 *AI Chat*
Just type any message to talk to me!
• Ask questions, get advice, brainstorm ideas
• Help with writing, planning, and more

📝 *Reminders*
• /remind [text] - Add a reminder
• /reminders - Show all reminders
• /done [number] - Complete a reminder
• /delete_reminder [number] - Delete a reminder

💰 *Finance*
• /income [amount] [source] - Add income
• /expense [amount] [category] [description] - Add expense
• /summary - See finance overview
• /budget [category] [amount] - Set a budget
• /checkbudgets - Check budget status

📧 *Email*
• /templates - See email templates
• /preview [key] - Preview a template
• /send [key] - Create email from template

⏰ *Scheduler*
• /morning - Get morning briefing now
• /evening - Get evening summary now
• /schedulestatus - Check schedule settings
• /setmorning [HH:MM] - Set morning time
• /setevening [HH:MM] - Set evening time
• /togglemorning - Toggle morning briefing
• /toggleevening - Toggle evening summary

🕐 *Quick Info*
• /time - Current time
• /date - Today's date

Just type a command or chat with me!
"""
    bot.reply_to(message, welcome_text, parse_mode='Markdown')

# ============================================
# QUICK INFO COMMANDS
# ============================================

@bot.message_handler(commands=['time'])
def show_time(message):
    now = datetime.now().strftime('%I:%M %p')
    bot.reply_to(message, f"🕐 Current time: {now}")

@bot.message_handler(commands=['date'])
def show_date(message):
    today = datetime.now().strftime('%A, %B %d, %Y')
    bot.reply_to(message, f"📅 Today's date: {today}")

# ============================================
# REMINDER COMMANDS
# ============================================

@bot.message_handler(commands=['remind'])
def add_reminder(message):
    """Add a new reminder"""
    text = message.text[8:].strip()
    
    if not text:
        bot.reply_to(message, "❌ Please provide a reminder text.\nExample: /remind Buy groceries")
        return
    
    result = reminders.add_reminder(text)
    bot.reply_to(message, result)

@bot.message_handler(commands=['reminders'])
def show_reminders(message):
    """Show all reminders"""
    result = reminders.show_reminders()
    bot.reply_to(message, result)

@bot.message_handler(commands=['done'])
def complete_reminder(message):
    """Mark a reminder as completed"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Please provide a reminder number.\nExample: /done 1")
            return
        
        number = int(parts[1])
        result = reminders.complete_reminder(number)
        bot.reply_to(message, result)
    except:
        bot.reply_to(message, "❌ Invalid number. Use: /done [number]")

@bot.message_handler(commands=['delete_reminder'])
def delete_reminder_cmd(message):
    """Delete a reminder"""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Please provide a reminder number.\nExample: /delete_reminder 1")
            return
        
        number = int(parts[1])
        result = reminders.delete_reminder(number)
        bot.reply_to(message, result)
    except:
        bot.reply_to(message, "❌ Invalid number. Use: /delete_reminder [number]")

# ============================================
# FINANCE COMMANDS
# ============================================

@bot.message_handler(commands=['income'])
def add_income(message):
    """Add income"""
    try:
        text = message.text[8:].strip()
        parts = text.split(' ', 1)
        
        if len(parts) < 2:
            bot.reply_to(message, "❌ Use: /income [amount] [source]\nExample: /income 5000 Monthly salary")
            return
        
        amount = parts[0].replace('$', '')
        source = parts[1]
        result = finance.add_income(amount, source)
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, f"❌ Error. Use: /income [amount] [source]")

@bot.message_handler(commands=['expense'])
def add_expense(message):
    """Add an expense"""
    try:
        text = message.text[9:].strip()
        parts = text.split(' ', 2)
        
        if len(parts) < 3:
            bot.reply_to(message, "❌ Use: /expense [amount] [category] [description]\nExample: /expense 50 Food Lunch at cafe")
            return
        
        amount = parts[0].replace('$', '')
        category = parts[1]
        description = parts[2]
        result = finance.add_expense(amount, category, description)
        bot.reply_to(message, result)
    except Exception as e:
        bot.reply_to(message, f"❌ Error. Use: /expense [amount] [category] [description]")

@bot.message_handler(commands=['summary'])
def show_summary(message):
    """Show finance summary"""
    result = finance.get_summary()
    bot.reply_to(message, result)

@bot.message_handler(commands=['budget'])
def set_budget(message):
    """Set a budget"""
    try:
        text = message.text[8:].strip()
        parts = text.rsplit(' ', 1)
        
        if len(parts) < 2:
            bot.reply_to(message, "❌ Use: /budget [category] [amount]\nExample: /budget Food 300")
            return
        
        category = parts[0]
        amount = parts[1].replace('$', '')
        result = finance.set_budget(category, amount)
        bot.reply_to(message, result)
    except:
        bot.reply_to(message, "❌ Error. Use: /budget [category] [amount]")

@bot.message_handler(commands=['checkbudgets'])
def check_budgets(message):
    """Check budget status"""
    result = finance.check_budgets()
    bot.reply_to(message, result)

# ============================================
# EMAIL COMMANDS
# ============================================

@bot.message_handler(commands=['templates'])
def list_templates(message):
    """Show email templates"""
    result = email_helper.list_templates()
    if len(result) > 4000:
        result = result[:4000] + "...\n(Message too long, showing first part)"
    bot.reply_to(message, result)

@bot.message_handler(commands=['preview'])
def preview_template(message):
    """Preview an email template"""
    try:
        key = message.text[9:].strip().lower()
        if not key:
            bot.reply_to(message, "❌ Use: /preview [template_key]\nExample: /preview sickday")
            return
        
        result = email_helper.preview_template(key)
        bot.reply_to(message, result)
    except:
        bot.reply_to(message, "❌ Error. Use: /preview [template_key]")

@bot.message_handler(commands=['send'])
def send_email_template(message):
    """Create email from template - starts a conversation"""
    try:
        key = message.text[6:].strip().lower()
        
        if not key:
            bot.reply_to(message, "❌ Use: /send [template_key]\nExample: /send sickday")
            return
        
        if key not in email_helper.templates:
            available = ", ".join(email_helper.templates.keys())
            bot.reply_to(message, f"❌ Template '{key}' not found.\nAvailable: {available}")
            return
        
        user_states[message.chat.id] = {
            'action': 'create_email',
            'template_key': key,
            'replacements': {},
            'fields': []
        }
        
        import re
        template = email_helper.templates[key]
        placeholders = re.findall(r'\[(.*?)\]', template['subject'] + ' ' + template['body'])
        unique_placeholders = list(set(placeholders))
        
        user_states[message.chat.id]['fields'] = unique_placeholders
        user_states[message.chat.id]['current_field'] = 0
        
        if unique_placeholders:
            first_field = unique_placeholders[0]
            bot.reply_to(message, f"📝 Let's fill in the template: *{template['name']}*\n\nPlease provide: *{first_field}*", parse_mode='Markdown')
        else:
            result = email_helper.create_email(key, {})
            bot.reply_to(message, result)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

@bot.message_handler(commands=['sent'])
def show_sent_emails(message):
    """Show recently created emails"""
    result = email_helper.show_sent()
    bot.reply_to(message, result)

# ============================================
# SCHEDULER COMMANDS
# ============================================

@bot.message_handler(commands=['morning'])
def morning_briefing(message):
    """Get morning briefing now"""
    if scheduler:
        briefing = scheduler.get_morning_briefing()
        bot.reply_to(message, briefing, parse_mode='Markdown')
    else:
        bot.reply_to(message, "⏰ Scheduler is starting up. Try again in a moment.")

@bot.message_handler(commands=['evening'])
def evening_summary(message):
    """Get evening summary now"""
    if scheduler:
        summary = scheduler.get_evening_summary()
        bot.reply_to(message, summary, parse_mode='Markdown')
    else:
        bot.reply_to(message, "⏰ Scheduler is starting up. Try again in a moment.")

@bot.message_handler(commands=['schedulestatus'])
def schedule_status(message):
    """Check schedule settings"""
    if scheduler:
        status = scheduler.get_status()
        bot.reply_to(message, status, parse_mode='Markdown')
    else:
        bot.reply_to(message, "⏰ Scheduler is starting up. Try again in a moment.")

@bot.message_handler(commands=['setmorning'])
def set_morning_cmd(message):
    """Set morning briefing time"""
    try:
        time_str = message.text[12:].strip()
        if scheduler:
            result = scheduler.set_morning_time(time_str)
            bot.reply_to(message, result)
        else:
            bot.reply_to(message, "⏰ Scheduler is starting up. Try again in a moment.")
    except:
        bot.reply_to(message, "❌ Use: /setmorning HH:MM\nExample: /setmorning 07:00")

@bot.message_handler(commands=['setevening'])
def set_evening_cmd(message):
    """Set evening summary time"""
    try:
        time_str = message.text[12:].strip()
        if scheduler:
            result = scheduler.set_evening_time(time_str)
            bot.reply_to(message, result)
        else:
            bot.reply_to(message, "⏰ Scheduler is starting up. Try again in a moment.")
    except:
        bot.reply_to(message, "❌ Use: /setevening HH:MM\nExample: /setevening 21:00")

@bot.message_handler(commands=['togglemorning'])
def toggle_morning_cmd(message):
    """Toggle morning briefing on/off"""
    if scheduler:
        result = scheduler.toggle_morning()
        bot.reply_to(message, result)
    else:
        bot.reply_to(message, "⏰ Scheduler is starting up.")

@bot.message_handler(commands=['toggleevening'])
def toggle_evening_cmd(message):
    """Toggle evening summary on/off"""
    if scheduler:
        result = scheduler.toggle_evening()
        bot.reply_to(message, result)
    else:
        bot.reply_to(message, "⏰ Scheduler is starting up.")

# ============================================
# HANDLE TEXT RESPONSES (for multi-step)
# ============================================

@bot.message_handler(func=lambda message: message.chat.id in user_states)
def handle_state(message):
    """Handle multi-step operations (email creation)"""
    state = user_states.get(message.chat.id)
    
    if not state:
        return
    
    if state['action'] == 'create_email':
        current_idx = state.get('current_field', 0)
        fields = state.get('fields', [])
        
        if current_idx < len(fields):
            current_field = fields[current_idx]
            state['replacements'][current_field] = message.text
            state['current_field'] = current_idx + 1
            
            if state['current_field'] < len(fields):
                next_field = fields[state['current_field']]
                bot.reply_to(message, f"Please provide: *{next_field}*", parse_mode='Markdown')
            else:
                key = state['template_key']
                replacements = state['replacements']
                result = email_helper.create_email(key, replacements)
                bot.reply_to(message, result)
                del user_states[message.chat.id]

# ============================================
# AI CHAT - For any message that's not a command
# ============================================

@bot.message_handler(func=lambda message: True)
def ai_chat(message):
    """AI Chat - responds to any message"""
    # Skip if user is in the middle of creating an email
    if message.chat.id in user_states:
        return
    
    # Show typing indicator
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Get AI response
    response = ai_bot.get_response(message.text)
    
    # Send response
    bot.reply_to(message, response)

# ============================================
# SET UP SCHEDULER
# ============================================

def send_telegram_message(message_text):
    """Send message to yourself via Telegram"""
    try:
        import os
        chat_id_file = "telegram_chat_id.txt"
        if os.path.exists(chat_id_file):
            with open(chat_id_file, 'r') as f:
                chat_id = f.read().strip()
            bot.send_message(chat_id, message_text, parse_mode='Markdown')
    except Exception as e:
        print(f"Scheduler send error: {e}")

# Initialize scheduler
scheduler = Scheduler(reminders, finance, send_telegram_message)

# ============================================
# START THE BOT
# ============================================

print("=" * 50)
print("🤖 TELEGRAM BOT IS STARTING...")
print("=" * 50)
print("\n💬 AI Chat is enabled!")
print("📝 Reminders are ready!")
print("💰 Finance tracking is ready!")
print("📧 Email templates are ready!")
print("⏰ Scheduler is active!")
print(f"   Morning briefing: {scheduler.config['morning_time']}")
print(f"   Evening summary: {scheduler.config['evening_time']}")
print("\nOpen Telegram on your phone and message your bot!")
print("\nPress Ctrl+C to stop the bot.\n")

if not YOUR_BOT_TOKEN:
    print("❌ ERROR: You need to set your bot token in the environment variable TELEGRAM_BOT_TOKEN or .env file!")
    print("\n1. Copy .env.example to .env")
    print("2. Set TELEGRAM_BOT_TOKEN in .env")
    print("3. Run this file again")
    exit()

# Start the scheduler
scheduler.start()

# Start the bot
bot.polling(non_stop=True)