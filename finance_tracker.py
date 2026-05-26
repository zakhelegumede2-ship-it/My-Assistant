"""
FINANCE TRACKER
Track your money, get insights, and manage your budget
Now with permanent database storage!
"""

import json
from datetime import datetime
import os

class FinanceTracker:
    def __init__(self, database=None):
        self.data_file = "finance_data.json"
        self.database = database
        self.data = {
            'income': [],
            'expenses': [],
            'budgets': {}
        }
        
        # Try loading from database first
        if self.database:
            db_data = self.database.load_finances()
            if db_data is not None and (len(db_data.get('income', [])) > 0 or len(db_data.get('expenses', [])) > 0):
                self.data['income'] = db_data.get('income', [])
                self.data['expenses'] = db_data.get('expenses', [])
                self.data['budgets'] = db_data.get('budgets', {})
                print("✅ Finance data loaded from database")
                return
        
        # Fall back to local file
        self.load_data()
        print("✅ Finance data loaded from local file")
    
    def load_data(self):
        """Load saved financial data from local file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                loaded = json.load(f)
                self.data['income'] = loaded.get('income', [])
                self.data['expenses'] = loaded.get('expenses', [])
                self.data['budgets'] = loaded.get('budgets', {})
        else:
            self.data = {
                'income': [],
                'expenses': [],
                'budgets': {}
            }
    
    def save_data(self):
        """Save financial data to file and database"""
        # Always save to local file
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
        
        # Also save to database if available
        if self.database:
            try:
                self.database.save_finances(self.data)
            except Exception as e:
                print(f"⚠️ Could not save to database: {e}")
    
    def add_income(self, amount, source):
        """Add income"""
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return "❌ Invalid amount. Please enter a number."
        
        income = {
            'amount': amount,
            'source': source,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        self.data['income'].append(income)
        self.save_data()
        return f"✅ Added income: ${amount:,.2f} from {source}"
    
    def add_expense(self, amount, category, description):
        """Add an expense"""
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return "❌ Invalid amount. Please enter a number."
        
        expense = {
            'amount': amount,
            'category': category,
            'description': description,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        self.data['expenses'].append(expense)
        self.save_data()
        return f"✅ Added expense: ${amount:,.2f} for {category} - {description}"
    
    def get_summary(self):
        """Get financial summary"""
        total_income = sum(item['amount'] for item in self.data['income'])
        total_expenses = sum(item['amount'] for item in self.data['expenses'])
        balance = total_income - total_expenses
        
        # Group expenses by category
        categories = {}
        for expense in self.data['expenses']:
            cat = expense['category']
            categories[cat] = categories.get(cat, 0) + expense['amount']
        
        # This month's data
        current_month = datetime.now().strftime('%Y-%m')
        month_income = sum(
            item['amount'] for item in self.data['income'] 
            if item['date'].startswith(current_month)
        )
        month_expenses = sum(
            item['amount'] for item in self.data['expenses'] 
            if item['date'].startswith(current_month)
        )
        
        summary = f"""
💰 FINANCIAL SUMMARY
{'='*30}
Total Income:    ${total_income:,.2f}
Total Expenses:  ${total_expenses:,.2f}
Balance:         ${balance:,.2f}

📅 THIS MONTH:
Income:    ${month_income:,.2f}
Expenses:  ${month_expenses:,.2f}

📂 Expenses by Category:
"""
        
        if categories:
            # Sort by amount (highest first)
            sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            for cat, amount in sorted_cats:
                pct = (amount / total_expenses * 100) if total_expenses > 0 else 0
                bar = "█" * int(pct / 5)
                summary += f"\n  • {cat}: ${amount:,.2f} ({pct:.0f}%) {bar}"
        else:
            summary += "\n  No expenses recorded yet"
        
        return summary
    
    def get_recent_transactions(self, count=10):
        """Get most recent transactions"""
        all_transactions = []
        
        for item in self.data['income']:
            all_transactions.append({
                'type': 'income',
                'amount': item['amount'],
                'category': item.get('source', 'Unknown'),
                'description': item.get('description', ''),
                'date': item['date']
            })
        
        for item in self.data['expenses']:
            all_transactions.append({
                'type': 'expense',
                'amount': item['amount'],
                'category': item.get('category', 'Other'),
                'description': item.get('description', ''),
                'date': item['date']
            })
        
        # Sort by date (newest first)
        all_transactions.sort(key=lambda x: x['date'], reverse=True)
        
        return all_transactions[:count]
    
    def set_budget(self, category, amount):
        """Set a budget for a category"""
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return "❌ Invalid amount. Please enter a number."
        
        self.data['budgets'][category] = amount
        self.save_data()
        return f"✅ Budget set: ${amount:,.2f} for {category}"
    
    def check_budgets(self):
        """Check if you're over budget"""
        if not self.data['budgets']:
            return "No budgets set yet. Use 'budget [category] [amount]' to set one."
        
        # Calculate current spending by category
        spent = {}
        for expense in self.data['expenses']:
            cat = expense['category']
            spent[cat] = spent.get(cat, 0) + expense['amount']
        
        result = "📊 BUDGET CHECK:\n" + "="*30 + "\n"
        
        for category, budget in self.data['budgets'].items():
            current = spent.get(category, 0)
            remaining = budget - current
            pct = (current / budget * 100) if budget > 0 else 0
            
            if remaining > 0:
                status = "🟢"
            elif remaining == 0:
                status = "🟡"
            else:
                status = "🔴"
            
            result += f"\n{status} {category}:"
            result += f"\n   Budget: ${budget:,.2f}"
            result += f"\n   Spent:  ${current:,.2f}"
            result += f"\n   Left:   ${remaining:,.2f} ({pct:.0f}% used)"
        
        return result
    
    def delete_transaction(self, index, trans_type):
        """Delete a transaction by index"""
        if trans_type == 'income':
            if 0 <= index < len(self.data['income']):
                item = self.data['income'].pop(index)
                self.save_data()
                return f"🗑️ Deleted income: ${item['amount']:,.2f} from {item.get('source', 'Unknown')}"
        elif trans_type == 'expense':
            if 0 <= index < len(self.data['expenses']):
                item = self.data['expenses'].pop(index)
                self.save_data()
                return f"🗑️ Deleted expense: ${item['amount']:,.2f} for {item.get('category', 'Unknown')}"
        
        return "❌ Invalid transaction"
    
    def sync_from_database(self):
        """Force sync finance data from database"""
        if self.database:
            db_data = self.database.load_finances()
            if db_data is not None:
                self.data['income'] = db_data.get('income', [])
                self.data['expenses'] = db_data.get('expenses', [])
                self.data['budgets'] = db_data.get('budgets', {})
                self.save_data()
                return "✅ Synced from database"
        return "❌ No database connection"
    
    def export_data(self):
        """Export all finance data as formatted text"""
        summary = self.get_summary()
        
        recent = self.get_recent_transactions(20)
        
        export = summary
        export += "\n\n📋 RECENT TRANSACTIONS:\n"
        export += "="*30 + "\n"
        
        for t in recent:
            icon = "💰" if t['type'] == 'income' else "💸"
            export += f"\n{icon} {t['date']} | ${t['amount']:,.2f} | {t['category']}"
            if t.get('description'):
                export += f" - {t['description']}"
        
        return export


# Test the finance tracker
if __name__ == "__main__":
    tracker = FinanceTracker()
    
    while True:
        print("\n" + "="*40)
        print("💰 FINANCE TRACKER")
        print("="*40)
        print(tracker.get_summary())
        print("\nCommands:")
        print("  income [amount] [source]")
        print("  expense [amount] [category] [description]")
        print("  budget [category] [amount]")
        print("  check - Check budgets")
        print("  recent - Recent transactions")
        print("  delete income [number] - Delete income")
        print("  delete expense [number] - Delete expense")
        print("  sync - Sync from database")
        print("  export - Export all data")
        print("  quit - Exit")
        print("-"*40)
        
        command = input("> ").strip()
        
        if command.lower() == 'quit':
            print("Goodbye!")
            break
        elif command.lower() == 'check':
            print(tracker.check_budgets())
        elif command.lower() == 'recent':
            transactions = tracker.get_recent_transactions(10)
            print("\n📋 RECENT TRANSACTIONS:")
            for i, t in enumerate(transactions):
                icon = "💰" if t['type'] == 'income' else "💸"
                print(f"  {i}. {icon} {t['date']} | ${t['amount']:,.2f} | {t['category']}")
        elif command.lower() == 'sync':
            print(tracker.sync_from_database())
        elif command.lower() == 'export':
            print(tracker.export_data())
        elif command.lower().startswith('income '):
            parts = command[7:].split(' ', 1)
            if len(parts) == 2:
                print(tracker.add_income(parts[0], parts[1]))
            else:
                print("❌ Use: income [amount] [source]")
        elif command.lower().startswith('expense '):
            parts = command[8:].split(' ', 2)
            if len(parts) == 3:
                print(tracker.add_expense(parts[0], parts[1], parts[2]))
            else:
                print("❌ Use: expense [amount] [category] [description]")
        elif command.lower().startswith('budget '):
            parts = command[7:].split(' ', 1)
            if len(parts) == 2:
                print(tracker.set_budget(parts[0], parts[1]))
            else:
                print("❌ Use: budget [category] [amount]")
        elif command.lower().startswith('delete income '):
            try:
                num = int(command[14:])
                print(tracker.delete_transaction(num, 'income'))
            except:
                print("❌ Use: delete income [number]")
        elif command.lower().startswith('delete expense '):
            try:
                num = int(command[15:])
                print(tracker.delete_transaction(num, 'expense'))
            except:
                print("❌ Use: delete expense [number]")
        else:
            print("❌ Unknown command")