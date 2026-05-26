"""
DATABASE - Supabase Integration
Saves your data permanently so it never disappears!
"""

import os
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()

class Database:
    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        
        if not url or not key or url == 'your-supabase-url' or key == 'your-supabase-key':
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
    
    def save_reminders(self, reminders_data):
        if not self.client:
            return False
        try:
            for reminder in reminders_data:
                reminder_id = reminder.get('text', '').replace(' ', '_').lower()
                data = {
                    'id': reminder_id,
                    'text': str(reminder['text']),
                    'completed': bool(reminder.get('completed', False)),
                    'created_at': str(reminder.get('created_at', datetime.now().isoformat())),
                    'completed_at': str(reminder.get('completed_at')) if reminder.get('completed_at') else None
                }
                self.client.table('reminders').upsert(data).execute()
            return True
        except Exception as e:
            print(f"DB save error: {e}")
            return False
    
    def load_reminders(self):
        if not self.client:
            return None
        try:
            response = self.client.table('reminders').select('*').execute()
            reminders = []
            for row in response.data:
                reminders.append({
                    'text': str(row['text']),
                    'completed': bool(row.get('completed', False)),
                    'created_at': str(row.get('created_at', '')),
                    'completed_at': str(row.get('completed_at')) if row.get('completed_at') else None
                })
            return reminders
        except Exception as e:
            print(f"DB load error: {e}")
            return None
    
    def add_reminder(self, text):
        if not self.client:
            return False
        try:
            reminder_id = text.replace(' ', '_').lower()
            self.client.table('reminders').insert({
                'id': reminder_id,
                'text': str(text),
                'completed': False,
                'created_at': str(datetime.now().isoformat())
            }).execute()
            return True
        except Exception as e:
            print(f"DB add error: {e}")
            return False
    
    def update_reminder(self, text, completed):
        if not self.client:
            return False
        try:
            reminder_id = text.replace(' ', '_').lower()
            self.client.table('reminders').update({
                'completed': bool(completed),
                'completed_at': str(datetime.now().isoformat()) if completed else None
            }).eq('id', reminder_id).execute()
            return True
        except Exception as e:
            print(f"DB update error: {e}")
            return False
    
    def delete_reminder(self, text):
        if not self.client:
            return False
        try:
            reminder_id = text.replace(' ', '_').lower()
            self.client.table('reminders').delete().eq('id', reminder_id).execute()
            return True
        except Exception as e:
            print(f"DB delete error: {e}")
            return False
    
    def save_finances(self, finance_data):
        if not self.client:
            return False
        try:
            self.client.table('finances').delete().neq('id', '0').execute()
            
            for item in finance_data.get('income', []):
                item_id = f"inc_{datetime.now().timestamp()}"
                self.client.table('finances').insert({
                    'id': item_id,
                    'type': 'income',
                    'amount': float(item['amount']),
                    'category': str(item.get('source', 'Unknown')),
                    'description': str(item.get('description', '')),
                    'date': str(item.get('date', datetime.now().strftime('%Y-%m-%d')))
                }).execute()
            
            for item in finance_data.get('expenses', []):
                item_id = f"exp_{datetime.now().timestamp()}"
                self.client.table('finances').insert({
                    'id': item_id,
                    'type': 'expense',
                    'amount': float(item['amount']),
                    'category': str(item.get('category', 'Other')),
                    'description': str(item.get('description', '')),
                    'date': str(item.get('date', datetime.now().strftime('%Y-%m-%d')))
                }).execute()
            
            return True
        except Exception as e:
            print(f"DB save error: {e}")
            return False
    
    def load_finances(self):
        if not self.client:
            return None
        try:
            response = self.client.table('finances').select('*').execute()
            income = []
            expenses = []
            
            for row in response.data:
                item = {
                    'amount': float(row['amount']),
                    'date': str(row.get('date', ''))
                }
                
                if row['type'] == 'income':
                    item['source'] = str(row.get('category', 'Unknown'))
                    income.append(item)
                else:
                    item['category'] = str(row.get('category', 'Other'))
                    item['description'] = str(row.get('description', ''))
                    expenses.append(item)
            
            return {'income': income, 'expenses': expenses, 'budgets': {}}
        except Exception as e:
            print(f"DB load error: {e}")
            return None
