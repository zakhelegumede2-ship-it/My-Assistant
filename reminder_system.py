"""
REMINDER SYSTEM
Your assistant can now remember things for you
"""

import json
from datetime import datetime
import os
from typing import Any, Dict, List, cast

class ReminderSystem:
    def __init__(self) -> None:
        self.data_file: str = "reminders.json"
        self.reminders: List[Dict[str, Any]] = []
        self.load_reminders()
    
    def load_reminders(self) -> None:
        """Load saved reminders"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.reminders = cast(List[Dict[str, Any]], json.load(f))
        else:
            self.reminders = []
    
    def save_reminders(self) -> None:
        """Save reminders to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.reminders, f, indent=4)
    
    def add_reminder(self, text: str) -> str:
        """Add a new reminder"""
        reminder: Dict[str, Any] = {
            'text': text,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'completed': False
        }
        self.reminders.append(reminder)
        self.save_reminders()
        return f"✅ Reminder added: {text}"
    
    def show_reminders(self) -> str:
        """Show all reminders"""
        if not self.reminders:
            return "📝 No reminders yet!"
        
        active = [r for r in self.reminders if not r['completed']]
        completed = [r for r in self.reminders if r['completed']]
        
        result = "📝 YOUR REMINDERS:\n" + "="*30 + "\n\n"
        
        if active:
            result += "⬜ TO DO:\n"
            for i, r in enumerate(active, 1):
                result += f"  {i}. {r['text']}\n"
                result += f"     Created: {r['created_at']}\n\n"
        
        if completed:
            result += "✅ COMPLETED:\n"
            for i, r in enumerate(completed, 1):
                result += f"  {i}. {r['text']}\n\n"
        
        return result
    
    def complete_reminder(self, number: int) -> str:
        """Mark a reminder as done"""
        active = [r for r in self.reminders if not r['completed']]
        if 1 <= number <= len(active):
            active[number-1]['completed'] = True
            active[number-1]['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.save_reminders()
            return f"✅ Completed: {active[number-1]['text']}"
        return "❌ Invalid reminder number"
    
    def delete_reminder(self, number: int) -> str:
        """Delete a reminder"""
        active = [r for r in self.reminders if not r['completed']]
        if 1 <= number <= len(active):
            text = active[number-1]['text']
            self.reminders.remove(active[number-1])
            self.save_reminders()
            return f"🗑️ Deleted: {text}"
        return "❌ Invalid reminder number"

# Test the reminder system
if __name__ == "__main__":
    reminders = ReminderSystem()
    
    while True:
        print("\n" + "="*40)
        print("📝 REMINDER SYSTEM")
        print("="*40)
        print(reminders.show_reminders())
        print("\nCommands:")
        print("  add [text] - Add a reminder")
        print("  done [number] - Mark as complete")
        print("  delete [number] - Delete a reminder")
        print("  quit - Exit")
        print("-"*40)
        
        command = input("> ").strip()
        
        if command.lower() == 'quit':
            print("Goodbye!")
            break
        elif command.lower().startswith('add '):
            text = command[4:]
            print(reminders.add_reminder(text))
        elif command.lower().startswith('done '):
            try:
                num = int(command[5:])
                print(reminders.complete_reminder(num))
            except:
                print("❌ Please use: done [number]")
        elif command.lower().startswith('delete '):
            try:
                num = int(command[7:])
                print(reminders.delete_reminder(num))
            except:
                print("❌ Please use: delete [number]")
        else:
            print("❌ Unknown command")