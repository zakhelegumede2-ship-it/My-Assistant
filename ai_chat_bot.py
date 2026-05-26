import os
from dotenv import load_dotenv

load_dotenv()

class AIChatBot:
    def __init__(self):
        self.messages = []
        self.setup_provider()
    
    def setup_provider(self):
        """Try to set up the best available AI provider"""
        
        # Try Groq first (free, fast, needs API key)
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            try:
                from groq import Groq
                self.client = Groq(api_key=groq_key)
                self.provider = 'groq'
                self.model = 'llama-3.3-70b-versatile'
                print("✅ AI: Using Groq")
                return
            except Exception as e:
                print(f"⚠️ Groq setup failed: {e}")
        
        # Try Gemini (free tier, needs API key)
        gemini_key = os.getenv('GEMINI_API_KEY')
        if gemini_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=gemini_key)
                self.provider = 'gemini'
                self.models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                self.chat = None
                print("✅ AI: Using Gemini")
                return
            except Exception as e:
                print(f"⚠️ Gemini setup failed: {e}")
        
        # Fallback: Free public API (no key needed, always works)
        self.provider = 'free'
        print("✅ AI: Using free public API")
    
    def get_response(self, message):
        try:
            if self.provider == 'groq':
                return self._groq_response(message)
            elif self.provider == 'gemini':
                return self._gemini_response(message)
            elif self.provider == 'free':
                return self._free_response(message)
            else:
                return "❌ No AI provider available."
        except Exception as e:
            # Ultimate fallback
            return self._free_response(message)
    
    def _groq_response(self, message):
        self.messages.append({"role": "user", "content": message})
        response = self.client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=0.7,
            max_tokens=1024
        )
        reply = response.choices[0].message.content
        self.messages.append({"role": "assistant", "content": reply})
        return reply
    
    def _gemini_response(self, message):
        for model_name in self.models:
            try:
                if not self.chat:
                    self.chat = self.client.chats.create(model=model_name, history=[])
                response = self.chat.send_message(message)
                return response.text
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "404" in error_str:
                    continue
                raise e
        # All Gemini models failed, fall back to free
        return self._free_response(message)
    
    def _free_response(self, message):
        """Free public API - no key needed"""
        import requests
        try:
            self.messages.append({"role": "user", "content": message})
            response = requests.post(
                "https://text.pollinations.ai/",
                json={"messages": self.messages},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                reply = data.get('text', 'No response')
                self.messages.append({"role": "assistant", "content": reply})
                return reply
            else:
                return "❌ AI service temporarily unavailable. Please try again."
        except Exception as e:
            return f"❌ Connection error. Check your internet and try again."