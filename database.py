"""
DATABASE - Supabase Integration
Saves your data permanently so it never disappears!
"""

import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class Database:
    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key:
            print("⚠️ Supabase not configured. Using local storage only.")
            self.client = None
            return
        
        try:
            from supabase import create_client
            self.client = create_client(url, key)
            print("✅ Database connected!")
        except Exception as e:
            print(f"⚠️ Database connection failed: {e}")
            self.client = None
    
    # ============================================
    # REMINDERS
    # ============================================
    
    def save_reminders(self, reminders_data):
        """Save all reminders to database"""
        if not self.client:
            return False
        
        try:
            for reminder in reminders_data:
                reminder_id = reminder.get('text', '').replace(' ', '_').lower()
                self.client.table('reminders').upsert({
                    'id': reminder_id,
                    'text': reminder['text'],
                    'completed': reminder.get('completed', False),
                    'created_at': reminder.get('created_at', datetime.now().isoformat()),
                    'completed_at': reminder.get('completed_at', None)
                }).execute()
            return True
        except Exception as e:
            print(f"Database save error: {e}")
            return False
    
    def load_reminders(self):
        """Load all reminders from database"""
        if not self.client:
            return None
        
        try:
            response = self.client.table('reminders').select('*').execute()
            reminders = []
            for row in response.data:
                reminders.append({
                    'text': row['text'],
                    'completed': row.get('completed', False),
                    'created_at': row.get('created_at', ''),
                    'completed_at': row.get('completed_at', None)
                })
            return reminders
        except Exception as e:
            print(f"Database load error: {e}")
            return None
    
    def add_reminder(self, text):
        """Add a single reminder"""
        if not self.client:
            return False
        
        try:
            reminder_id = text.replace(' ', '_').lower()
            self.client.table('reminders').insert({
                'id': reminder_id,
                'text': text,
                'completed': False,
                'created_at': datetime.now().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"Database add error: {e}")
            return False
    
    def update_reminder(self, text, completed):
        """Update a reminder's completion status"""
        if not self.client:
            return False
        
        try:
            reminder_id = text.replace(' ', '_').lower()
            self.client.table('reminders').update({
                'completed': completed,
                'completed_at': datetime.now().isoformat() if completed else None
            }).eq('id', reminder_id).execute()
            return True
        except Exception as e:
            print(f"Database update error: {e}")
            return False
    
    def delete_reminder(self, text):
        """Delete a reminder"""
        if not self.client:
            return False
        
        try:
            reminder_id = text.replace(' ', '_').lower()
            self.client.table('reminders').delete().eq('id', reminder_id).execute()
            return True
        except Exception as e:
            print(f"Database delete error: {e}")
            return False
    
    # ============================================
    # FINANCE
    # ============================================
    
    def save_finances(self, finance_data):
        """Save all finance data to database"""
        if not self.client:
            return False
        
        try:
            # First clear existing data
            self.client.table('finances').delete().neq('id', '0').execute()
            
            # Save income
            for item in finance_data.get('income', []):
                item_id = f"income_{datetime.now().timestamp()}_{item.get('source', 'unknown')}"
                self.client.table('finances').insert({
                    'id': item_id,
                    'type': 'income',
                    'amount': float(item['amount']),
                    'category': item.get('source', 'Unknown'),
                    'description': item.get('description', ''),
                    'date': item.get('date', datetime.now().strftime('%Y-%m-%d'))
                }).execute()
            
            # Save expenses
            for item in finance_data.get('expenses', []):
                item_id = f"expense_{datetime.now().timestamp()}_{item.get('category', 'other')}"
                self.client.table('finances').insert({
                    'id': item_id,
                    'type': 'expense',
                    'amount': float(item['amount']),
                    'category': item.get('category', 'Other'),
                    'description': item.get('description', ''),
                    'date': item.get('date', datetime.now().strftime('%Y-%m-%d'))
                }).execute()
            
            return True
        except Exception as e:
            print(f"Database save error: {e}")
            return False
    
    def load_finances(self):
        """Load all finance data from database"""
        if not self.client:
            return None
        
        try:
            response = self.client.table('finances').select('*').execute()
            
            income = []
            expenses = []
            
            for row in response.data:
                item = {
                    'amount': float(row['amount']),
                    'date': row.get('date', '')
                }
                
                if row['type'] == 'income':
                    item['source'] = row.get('category', 'Unknown')
                    income.append(item)
                else:
                    item['category'] = row.get('category', 'Other')
                    item['description'] = row.get('description', '')
                    expenses.append(item)
            
            return {
                'income': income,
                'expenses': expenses,
                'budgets': {}
            }
        except Exception as e:
            print(f"Database load error: {e}")
            return None