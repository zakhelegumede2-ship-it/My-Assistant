"""
AI Chat Bot - Simple free AI that works everywhere
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

class AIChatBot:
    def __init__(self):
        self.messages = []
        print("✅ AI: Using free Pollinations API")
    
    def get_response(self, message):
        try:
            self.messages.append({"role": "user", "content": message})
            
            response = requests.post(
                "https://text.pollinations.ai/",
                json={"messages": self.messages},
                timeout=60,
                headers={"User-Agent": "MyAssistant/1.0"}
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('text', 'No response')
                self.messages.append({"role": "assistant", "content": reply})
                return reply
            
            return "Sorry, I couldn't process that. Try again."
        except Exception as e:
            return f"AI unavailable right now. Please try again later."
