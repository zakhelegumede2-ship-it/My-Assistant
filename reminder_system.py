"""
REMINDER SYSTEM
Your assistant can now remember things for you
Now with permanent database storage!
"""

import json
from datetime import datetime
import os

class ReminderSystem:
    def __init__(self, database=None):
        self.data_file = "reminders.json"
        self.database = database
        self.reminders = []
        
        # Try loading from database first, then local file
        if self.database:
            db_reminders = self.database.load_reminders()
            if db_reminders is not None and len(db_reminders) > 0:
                self.reminders = db_reminders
                print("✅ Reminders loaded from database")
                return
        
        # Fall back to local file
        self.load_reminders()
        print("✅ Reminders loaded from local file")
    
    def load_reminders(self):
        """Load saved reminders from local file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.reminders = json.load(f)
        else:
            self.reminders = []
    
    def save_reminders(self):
        """Save reminders to file and database"""
        # Always save to local file
        with open(self.data_file, 'w') as f:
            json.dump(self.reminders, f, indent=4)
        
        # Also save to database if available
        if self.database:
            try:
                self.database.save_reminders(self.reminders)
            except Exception as e:
                print(f"⚠️ Could not save to database: {e}")
    
    def add_reminder(self, text):
        """Add a new reminder"""
        reminder = {
            'text': text,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'completed': False
        }
        self.reminders.append(reminder)
        self.save_reminders()
        
        # Also add directly to database if available
        if self.database:
            try:
                self.database.add_reminder(text)
            except Exception as e:
                print(f"⚠️ Database add failed: {e}")
        
        return f"✅ Reminder added: {text}"
    
    def show_reminders(self):
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
                result += f"  {i}. {r['text']}\n"
                if 'completed_at' in r:
                    result += f"     Done: {r['completed_at']}\n"
                result += "\n"
        
        return result
    
    def complete_reminder(self, number):
        """Mark a reminder as done"""
        active = [r for r in self.reminders if not r['completed']]
        if 1 <= number <= len(active):
            active[number-1]['completed'] = True
            active[number-1]['completed_at'] = datetime.now().strftime('%Y-%m-%d %H:%M')
            self.save_reminders()
            
            # Update in database
            if self.database:
                try:
                    self.database.update_reminder(active[number-1]['text'], True)
                except Exception as e:
                    print(f"⚠️ Database update failed: {e}")
            
            return f"✅ Completed: {active[number-1]['text']}"
        return "❌ Invalid reminder number"
    
    def delete_reminder(self, number):
        """Delete a reminder"""
        active = [r for r in self.reminders if not r['completed']]
        if 1 <= number <= len(active):
            text = active[number-1]['text']
            self.reminders.remove(active[number-1])
            self.save_reminders()
            
            # Delete from database
            if self.database:
                try:
                    self.database.delete_reminder(text)
                except Exception as e:
                    print(f"⚠️ Database delete failed: {e}")
            
            return f"🗑️ Deleted: {text}"
        return "❌ Invalid reminder number"
    
    def sync_from_database(self):
        """Force sync reminders from database"""
        if self.database:
            db_reminders = self.database.load_reminders()
            if db_reminders is not None:
                self.reminders = db_reminders
                self.save_reminders()
                return "✅ Synced from database"
        return "❌ No database connection"


# Test the reminder system
if __name__ == "__main__":
    # Test without database
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
        print("  sync - Sync from database")
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
        elif command.lower() == 'sync':
            print(reminders.sync_from_database())
        else:
            print("❌ Unknown command")