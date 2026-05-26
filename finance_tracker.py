"""
FINANCE TRACKER
Track your money, get insights, and manage your budget
"""

import json
from datetime import datetime
import os

class FinanceTracker:
    def __init__(self):
        self.data_file = "finance_data.json"
        self.load_data()
    
    def load_data(self):
        """Load saved financial data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'income': [],
                'expenses': [],
                'budgets': {}
            }
    
    def save_data(self):
        """Save financial data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=4)
    
    def add_income(self, amount, source):
        """Add income"""
        income = {
            'amount': float(amount),
            'source': source,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        self.data['income'].append(income)
        self.save_data()
        return f"✅ Added income: ${amount} from {source}"
    
    def add_expense(self, amount, category, description):
        """Add an expense"""
        expense = {
            'amount': float(amount),
            'category': category,
            'description': description,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        self.data['expenses'].append(expense)
        self.save_data()
        return f"✅ Added expense: ${amount} for {category} - {description}"
    
    def get_summary(self):
        """Get financial summary"""
        total_income = sum(item['amount'] for item in self.data['income'])
        total_expenses = sum(item['amount'] for item in self.data['expenses'])
        balance = total_income - total_expenses
        
        categories = {}
        for expense in self.data['expenses']:
            cat = expense['category']
            categories[cat] = categories.get(cat, 0) + expense['amount']
        
        summary = f"""
        💰 FINANCIAL SUMMARY
        {'='*30}
        Total Income:    ${total_income:,.2f}
        Total Expenses:  ${total_expenses:,.2f}
        Balance:         ${balance:,.2f}
        
        📂 Expenses by Category:
        """
        
        if categories:
            for cat, amount in categories.items():
                summary += f"\n  • {cat}: ${amount:,.2f}"
        else:
            summary += "\n  No expenses recorded yet"
        
        return summary
    
    def set_budget(self, category, amount):
        """Set a budget for a category"""
        self.data['budgets'][category] = float(amount)
        self.save_data()
        return f"✅ Budget set: ${amount:.2f} for {category}"
    
    def check_budgets(self):
        """Check if you're over budget"""
        if not self.data['budgets']:
            return "No budgets set yet. Use 'budget [category] [amount]' to set one."
        
        spent = {}
        for expense in self.data['expenses']:
            cat = expense['category']
            spent[cat] = spent.get(cat, 0) + expense['amount']
        
        result = "📊 BUDGET CHECK:\n" + "="*30 + "\n"
        
        for category, budget in self.data['budgets'].items():
            current = spent.get(category, 0)
            remaining = budget - current
            status = "🟢" if remaining > 0 else "🔴"
            
            result += f"\n{status} {category}:"
            result += f"\n   Budget: ${budget:.2f}"
            result += f"\n   Spent:  ${current:.2f}"
            result += f"\n   Left:   ${remaining:.2f}"
        
        return result

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
        print("  quit - Exit")
        print("-"*40)
        
        command = input("> ").strip()
        
        if command.lower() == 'quit':
            print("Goodbye!")
            break
        elif command.lower() == 'check':
            print(tracker.check_budgets())
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
        else:
            print("❌ Unknown command")