"""
AI Chat Bot - Works everywhere including Render
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

class AIChatBot:
    def __init__(self):
        self.messages = []
        print("✅ AI: Ready")
    
    def get_response(self, message):
        try:
            # Try multiple free endpoints
            return self._try_endpoints(message)
        except Exception as e:
            return f"I'm having trouble connecting. Please try again."
    
    def _try_endpoints(self, message):
        self.messages.append({"role": "user", "content": message})
        
        # Try endpoint 1: text.pollinations.ai
        try:
            response = requests.post(
                "https://text.pollinations.ai/",
                json={
                    "messages": self.messages,
                    "model": "openai"
                },
                timeout=45,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            if response.status_code == 200:
                data = response.json()
                reply = data.get('text', '')
                if reply:
                    self.messages.append({"role": "assistant", "content": reply})
                    return reply
        except:
            pass
        
        # Try endpoint 2: openrouter free models
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json={
                    "model": "google/gemma-2-9b-it:free",
                    "messages": self.messages
                },
                timeout=45,
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            if response.status_code == 200:
                data = response.json()
                reply = data['choices'][0]['message']['content']
                self.messages.append({"role": "assistant", "content": reply})
                return reply
        except:
            pass
        
        # If all fail
        return self._offline_response(message)
    
    def _offline_response(self, message):
        """Simple offline responses when APIs are unavailable"""
        msg = message.lower()
        
        if "hello" in msg or "hi" in msg:
            return "Hello! I'm here to help. What can I do for you?"
        elif "remind" in msg:
            return "To set a reminder, go to the Reminders tab and type it in, or use the /remind command on Telegram!"
        elif "finance" in msg or "money" in msg or "budget" in msg:
            return "Go to the Finance tab to track your income and expenses. You can set budgets there too!"
        elif "email" in msg:
            return "Check the Email tab for templates. You can create professional emails quickly!"
        elif "help" in msg:
            return "I can help with: 📝 Reminders, 💰 Finance tracking, 📧 Email templates. Just switch tabs or ask me!"
        elif "thank" in msg:
            return "You're welcome! Happy to help. 😊"
        elif "bye" in msg:
            return "Goodbye! Come back anytime you need help. 👋"
        else:
            return "I'm currently running in offline mode. The AI service will be back soon. In the meantime, try the Reminders, Finance, or Email tabs!"
