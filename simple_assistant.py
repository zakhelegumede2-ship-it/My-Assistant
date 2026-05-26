"""
YOUR PERSONAL AI ASSISTANT
This is the main file that runs everything
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

# Load your secret keys from .env file
load_dotenv()

class YourPersonalAssistant:
    """This is your AI assistant. Think of it as your digital helper."""
    
    def __init__(self):
        """Set up your assistant"""
        # Connect to OpenAI (the AI brain)
        api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=api_key)
        self.your_name = ""
        self.conversation_history = []
        
    def introduce_yourself(self):
        """Assistant introduces itself"""
        print("\n" + "="*50)
        print("🤖 YOUR PERSONAL AI ASSISTANT")
        print("="*50)
        
        self.your_name = input("\nWhat's your name? ")
        
        print(f"\nHello {self.your_name}! I'm your personal assistant.")
        print("\nI can help you with:")
        print("  📧  Managing emails")
        print("  📅  Calendar and schedule")
        print("  💰  Understanding finances")
        print("  ⏰  Setting reminders")
        print("  💬  General questions and help")
        print("\nType 'help' to see commands, or just talk to me naturally!")
        print("Type 'quit' to exit.\n")
    
    def ask_ai(self, question):
        """Ask the AI anything"""
        try:
            # Prepare the conversation
            messages = [
                {"role": "system", "content": f"You are a helpful personal assistant for {self.your_name}. Be friendly, concise, and helpful."},
                {"role": "user", "content": question}
            ]
            
            # Get response from AI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Return the AI's response
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I'm having trouble thinking right now. Error: {str(e)}"
    
    def handle_special_commands(self, command):
        """Handle special commands"""
        command = command.lower()
        
        if command == "help":
            return """
            📋 AVAILABLE COMMANDS:
            • Just talk normally - I'll understand!
            • 'time' - Current time
            • 'date' - Today's date
            • 'clear' - Clear the screen
            • 'save' - Save our conversation
            • 'quit' - Exit the assistant
            
            You can also say things like:
            • "What's on my schedule today?"
            • "Help me write an email to John"
            • "How can I save money this month?"
            • "Remind me to call mom at 3pm"
            """
        
        elif command == "time":
            return f"🕐 Current time: {datetime.now().strftime('%I:%M %p')}"
        
        elif command == "date":
            return f"📅 Today's date: {datetime.now().strftime('%A, %B %d, %Y')}"
        
        elif command == "clear":
            os.system('clear')
            return ""
        
        elif command == "save":
            self.save_conversation()
            return "✅ Conversation saved!"
        
        else:
            return None  # Not a special command
    
    def save_conversation(self):
        """Save the conversation to a file"""
        filename = f"conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w') as f:
            f.write(f"Conversation with {self.your_name}\n")
            f.write(f"Date: {datetime.now().strftime('%A, %B %d, %Y')}\n")
            f.write("-"*50 + "\n\n")
            for entry in self.conversation_history:
                f.write(f"You: {entry['user']}\n")
                f.write(f"Assistant: {entry['assistant']}\n\n")
        print(f"✅ Saved as: {filename}")
    
    def run(self):
        """Run the assistant (main loop)"""
        self.introduce_yourself()
        
        while True:
            # Get user input
            user_input = input(f"\n{self.your_name}: ").strip()
            
            if not user_input:
                continue
            
            # Check if they want to quit
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print(f"\nGoodbye {self.your_name}! Have a great day! 👋")
                break
            
            # Check for special commands
            special_response = self.handle_special_commands(user_input)
            
            if special_response is not None:
                if special_response:  # Only print if not empty (like clear screen)
                    print(f"\nAssistant: {special_response}")
                self.conversation_history.append({
                    'user': user_input,
                    'assistant': special_response if special_response else "Screen cleared"
                })
            else:
                # Ask the AI
                print("\n🤔 Thinking...")
                ai_response = self.ask_ai(user_input)
                print(f"\nAssistant: {ai_response}")
                
                # Save to history
                self.conversation_history.append({
                    'user': user_input,
                    'assistant': ai_response
                })

# This runs when you execute the file
if __name__ == "__main__":
    # Check if API key is set
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your-openai-key-here':
        print("❌ ERROR: You need to set your OpenAI API key!")
        print("\nPlease:")
        print("1. Open the .env file in VS Code")
        print("2. Replace 'your-openai-key-here' with your actual OpenAI key")
        print("3. Save the file (Cmd+S)")
        print("4. Run this program again")
        exit()
    
    # Create and run your assistant
    assistant = YourPersonalAssistant()
    assistant.run()