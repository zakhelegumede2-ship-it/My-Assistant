"""
SCHEDULER - Daily Briefings & Timed Reminders
Sends you morning briefings, evening summaries, and timed alerts
"""

import time
import threading
from datetime import datetime, time as dtime, timedelta
import json
import os
from typing import Any, Callable, Dict, Optional

def _get_zoneinfo_class() -> Optional[type]:
    try:
        from zoneinfo import ZoneInfo as _ZI
        return _ZI
    except Exception:
        return None

class Scheduler:
    def __init__(self, reminder_system: Any, finance_tracker: Any, send_callback: Callable[[str], None]) -> None:
        self.reminders = reminder_system
        self.finance = finance_tracker
        self.send = send_callback
        self.config_file = "schedule_config.json"
        self.running = False
        self.threads: list[threading.Thread] = []
        self.load_config()

    def _now(self) -> datetime:
        tzname = self.config.get('timezone')
        zi_cls = _get_zoneinfo_class()
        if tzname and zi_cls is not None:
            try:
                return datetime.now(zi_cls(tzname))
            except Exception:
                return datetime.now()
        return datetime.now()
    
    def load_config(self) -> None:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "morning_briefing": True,
                "morning_time": "07:00",
                "evening_summary": True,
                "evening_time": "21:00",
                "last_morning": None,
                "last_evening": None,
                "timezone": os.getenv('TIMEZONE', 'UTC')
            }
            self.save_config()
    
    def save_config(self) -> None:
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)
    
    def get_morning_briefing(self) -> str:
        today = self._now().strftime('%A, %B %d, %Y')
        active_reminders = [r for r in self.reminders.reminders if not r['completed']]
        total_income = sum(item['amount'] for item in self.finance.data['income'])
        total_expenses = sum(item['amount'] for item in self.finance.data['expenses'])
        balance = total_income - total_expenses
        current_month = self._now().strftime('%Y-%m')
        month_expenses = sum(
            item['amount'] for item in self.finance.data['expenses'] 
            if item['date'].startswith(current_month)
        )
        
        message = f"""
🌅 *GOOD MORNING!*
📅 *{today}*

"""
        if active_reminders:
            message += "📝 *TODAY'S TASKS:*\n"
            for i, r in enumerate(active_reminders[:5], 1):
                message += f"  {i}. {r['text']}\n"
            if len(active_reminders) > 5:
                message += f"  ...and {len(active_reminders) - 5} more\n"
        else:
            message += "📝 *No pending tasks!* 🎉\n"
        
        message += f"""
💰 *FINANCE SNAPSHOT:*
  Balance: ${balance:,.2f}
  This month's expenses: ${month_expenses:,.2f}
  Total income: ${total_income:,.2f}
"""
        
        if self.finance.data['budgets']:
            message += "\n📊 *BUDGET STATUS:*\n"
            spent: dict[str, float] = {}
            for expense in self.finance.data['expenses']:
                cat = expense['category']
                spent[cat] = spent.get(cat, 0) + expense['amount']
            
            for category, budget in list(self.finance.data['budgets'].items())[:3]:
                current = spent.get(category, 0)
                remaining = budget - current
                status = "🟢" if remaining > budget * 0.3 else "🟡" if remaining > 0 else "🔴"
                message += f"  {status} {category}: ${remaining:,.2f} left of ${budget:,.2f}\n"
        
        message += "\n💡 *Have a productive day!* 🚀"
        return message
    
    def get_evening_summary(self) -> str:
        today = self._now().strftime('%A, %B %d, %Y')
        completed_today = [
            r for r in self.reminders.reminders 
            if r['completed'] and r.get('completed_at', '').startswith(self._now().strftime('%Y-%m-%d'))
        ]
        pending = [r for r in self.reminders.reminders if not r['completed']]
        
        message = f"""
🌙 *EVENING SUMMARY*
📅 *{today}*

"""
        if completed_today:
            message += "✅ *COMPLETED TODAY:*\n"
            for r in completed_today:
                message += f"  ✓ {r['text']}\n"
        else:
            message += "📝 *No tasks completed today.*\n"
        
        if pending:
            message += f"\n📋 *STILL PENDING ({len(pending)}):*\n"
            for r in pending[:5]:
                message += f"  ⬜ {r['text']}\n"
        
        today_expenses = sum(
            item['amount'] for item in self.finance.data['expenses'] 
            if item['date'] == self._now().strftime('%Y-%m-%d')
        )
        
        if today_expenses > 0:
            message += f"\n💸 *TODAY'S SPENDING:* ${today_expenses:,.2f}"
        
        message += "\n\n😴 *Rest well! See you tomorrow!*"
        return message
    
    def morning_briefing_task(self) -> None:
        while self.running:
            now = self._now()
            try:
                mt = datetime.strptime(self.config['morning_time'], '%H:%M').time()
            except Exception:
                mt = dtime(7, 0)

            today_str = now.strftime('%Y-%m-%d')
            target = now.replace(hour=mt.hour, minute=mt.minute, second=0, microsecond=0)

            seconds_until = (target - now).total_seconds()
            if seconds_until <= 0:
                # If target already passed today, schedule for next day
                seconds_until += 24 * 3600

            # If within the next minute and not sent today, send
            if (self.config.get('morning_briefing') and seconds_until < 60 and self.config.get('last_morning') != today_str):
                message = self.get_morning_briefing()
                self.send(message)
                self.config['last_morning'] = today_str
                self.save_config()

            # Sleep a reasonable amount (min of time until target and 5 minutes)
            sleep_for = min(max(30, seconds_until), 300)
            time.sleep(sleep_for)
    
    def evening_summary_task(self) -> None:
        while self.running:
            now = self._now()
            try:
                et = datetime.strptime(self.config['evening_time'], '%H:%M').time()
            except Exception:
                et = dtime(21, 0)

            today_str = now.strftime('%Y-%m-%d')
            target = now.replace(hour=et.hour, minute=et.minute, second=0, microsecond=0)
            seconds_until = (target - now).total_seconds()
            if seconds_until <= 0:
                seconds_until += 24 * 3600

            if (self.config.get('evening_summary') and seconds_until < 60 and self.config.get('last_evening') != today_str):
                message = self.get_evening_summary()
                self.send(message)
                self.config['last_evening'] = today_str
                self.save_config()

            sleep_for = min(max(30, seconds_until), 300)
            time.sleep(sleep_for)
    
    def start(self) -> None:
        self.running = True
        morning_thread = threading.Thread(target=self.morning_briefing_task, daemon=True)
        morning_thread.start()
        self.threads.append(morning_thread)
        evening_thread = threading.Thread(target=self.evening_summary_task, daemon=True)
        evening_thread.start()
        self.threads.append(evening_thread)
        print("⏰ Scheduler started!")
        print(f"   Morning briefing: {self.config['morning_time']}")
        print(f"   Evening summary: {self.config['evening_time']}")
    
    def stop(self) -> None:
        self.running = False
        print("⏰ Scheduler stopped.")
    
    def set_morning_time(self, time_str: str) -> str:
        try:
            datetime.strptime(time_str, '%H:%M')
            self.config['morning_time'] = time_str
            self.save_config()
            return f"✅ Morning briefing set for {time_str}"
        except:
            return "❌ Invalid time format. Use HH:MM (e.g., 07:00)"
    
    def set_evening_time(self, time_str: str) -> str:
        try:
            datetime.strptime(time_str, '%H:%M')
            self.config['evening_time'] = time_str
            self.save_config()
            return f"✅ Evening summary set for {time_str}"
        except:
            return "❌ Invalid time format. Use HH:MM (e.g., 21:00)"

    def set_timezone(self, tz_str: str) -> str:
        """Set the scheduler timezone (e.g. 'UTC', 'Europe/London')."""
        if not tz_str:
            return "❌ Timezone is required"
        zi_cls = _get_zoneinfo_class()
        if zi_cls is not None:
            try:
                zi_cls(tz_str)
            except Exception:
                return f"❌ Invalid timezone: {tz_str}"

        self.config['timezone'] = tz_str
        self.save_config()
        return f"✅ Timezone set to {tz_str}"
    
    def toggle_morning(self) -> str:
        self.config['morning_briefing'] = not self.config['morning_briefing']
        self.save_config()
        status = "ON" if self.config['morning_briefing'] else "OFF"
        return f"✅ Morning briefing turned {status}"
    
    def toggle_evening(self) -> str:
        self.config['evening_summary'] = not self.config['evening_summary']
        self.save_config()
        status = "ON" if self.config['evening_summary'] else "OFF"
        return f"✅ Evening summary turned {status}"
    
    def get_status(self) -> str:
        return f"""
⏰ *SCHEDULE STATUS*

🌅 Morning Briefing: {'✅ ON' if self.config['morning_briefing'] else '❌ OFF'}
   Time: {self.config['morning_time']}

🌙 Evening Summary: {'✅ ON' if self.config['evening_summary'] else '❌ OFF'}
   Time: {self.config['evening_time']}
"""