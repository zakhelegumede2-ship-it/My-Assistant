"""
EMAIL HELPER
Write professional emails quickly with templates
No AI needed - works completely offline!
"""

import json
from datetime import datetime
import os

class EmailHelper:
    def __init__(self):
        self.data_file = "email_templates.json"
        self.sent_file = "sent_emails.json"
        self.load_templates()
        self.load_sent()
    
    def load_templates(self):
        """Load saved email templates"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.templates = json.load(f)
        else:
            # Default templates
            self.templates = {
                "meeting": {
                    "name": "Meeting Request",
                    "subject": "Meeting Request: [Topic]",
                    "body": """Hi [Name],

I hope this email finds you well. I'd like to schedule a meeting to discuss [Topic].

Would [Date] at [Time] work for you? If not, please let me know what time works best.

Looking forward to hearing from you.

Best regards,
[Your Name]"""
                },
                "followup": {
                    "name": "Follow Up",
                    "subject": "Following Up: [Topic]",
                    "body": """Hi [Name],

I'm following up on my previous email regarding [Topic].

I wanted to check if you've had a chance to review it and if you have any questions or feedback.

Please let me know if you need any additional information.

Best regards,
[Your Name]"""
                },
                "thankyou": {
                    "name": "Thank You",
                    "subject": "Thank You - [Topic]",
                    "body": """Hi [Name],

Thank you so much for [what they did]. I really appreciate you taking the time to help with this.

[Optional: Add a specific detail about what you're thankful for]

Thanks again, and I look forward to working with you in the future.

Best regards,
[Your Name]"""
                },
                "sickday": {
                    "name": "Sick Day Request",
                    "subject": "Sick Day - [Date]",
                    "body": """Hi [Name],

I'm writing to let you know that I'm not feeling well today and won't be able to come into work.

I'll check my emails when I can and will catch up on anything I miss when I'm back.

Please let me know if there's anything urgent that needs my attention.

Thank you,
[Your Name]"""
                },
                "late": {
                    "name": "Running Late",
                    "subject": "Running Late Today",
                    "body": """Hi [Name],

I wanted to let you know that I'm running a bit late this morning due to [reason].

I expect to arrive by [time] and will catch up on anything I miss.

Apologies for the inconvenience.

Best,
[Your Name]"""
                },
                "introduction": {
                    "name": "Introduction",
                    "subject": "Introduction: [Your Name] & [Their Name]",
                    "body": """Hi [Name],

My name is [Your Name] and I'm [your role/position].

I'm reaching out because [reason for contacting them].

I'd love to connect and learn more about [topic or their work].

Would you be available for a quick chat sometime next week?

Best regards,
[Your Name]"""
                }
            }
            self.save_templates()
    
    def load_sent(self):
        """Load sent emails history"""
        if os.path.exists(self.sent_file):
            with open(self.sent_file, 'r') as f:
                self.sent_emails = json.load(f)
        else:
            self.sent_emails = []
    
    def save_templates(self):
        """Save templates to file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.templates, f, indent=4)
    
    def save_sent(self):
        """Save sent emails"""
        with open(self.sent_file, 'w') as f:
            json.dump(self.sent_emails, f, indent=4)
    
    def list_templates(self):
        """Show all available templates"""
        result = "\n📧 EMAIL TEMPLATES:\n" + "="*40 + "\n\n"
        
        for key, template in self.templates.items():
            result += f"📌 {key.upper()}: {template['name']}\n"
            result += f"   Subject: {template['subject']}\n\n"
        
        return result
    
    def preview_template(self, template_key):
        """Preview a template"""
        if template_key not in self.templates:
            return f"❌ Template '{template_key}' not found. Use 'templates' to see all options."
        
        template = self.templates[template_key]
        
        result = f"\n📧 TEMPLATE: {template['name']}\n"
        result += "="*40 + "\n\n"
        result += f"📌 Subject: {template['subject']}\n\n"
        result += "📝 Body:\n"
        result += "-"*30 + "\n"
        result += template['body'] + "\n"
        result += "-"*30 + "\n\n"
        result += "🔧 Placeholders to fill in:\n"
        
        # Find placeholders
        import re
        placeholders = re.findall(r'\[(.*?)\]', template['subject'] + ' ' + template['body'])
        for p in set(placeholders):
            result += f"  • [{p}]\n"
        
        return result
    
    def create_email(self, template_key, replacements):
        """Create an email from a template with custom values"""
        if template_key not in self.templates:
            return f"❌ Template '{template_key}' not found."
        
        template = self.templates[template_key]
        subject = template['subject']
        body = template['body']
        
        # Replace placeholders
        for placeholder, value in replacements.items():
            subject = subject.replace(f"[{placeholder}]", value)
            body = body.replace(f"[{placeholder}]", value)
        
        # Save to sent emails
        email_record = {
            'template': template_key,
            'subject': subject,
            'body': body,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'replacements': replacements
        }
        self.sent_emails.append(email_record)
        self.save_sent()
        
        # Show the final email
        result = "\n✅ EMAIL CREATED!\n"
        result += "="*40 + "\n\n"
        result += f"📌 SUBJECT: {subject}\n\n"
        result += "📝 BODY:\n"
        result += "-"*30 + "\n"
        result += body + "\n"
        result += "-"*30 + "\n\n"
        result += "💡 Copy the text above and paste it into your email app!"
        result += "\n📋 Saved to sent emails."
        
        return result
    
    def show_sent(self):
        """Show recently sent emails"""
        if not self.sent_emails:
            return "📭 No emails created yet."
        
        result = "\n📤 RECENTLY CREATED EMAILS:\n"
        result += "="*40 + "\n\n"
        
        for i, email in enumerate(self.sent_emails[-10:], 1):
            result += f"{i}. 📌 {email['subject']}\n"
            result += f"   Template: {email['template']}\n"
            result += f"   Created: {email['created_at']}\n\n"
        
        return result
    
    def view_sent_email(self, number):
        """View a specific sent email"""
        if 1 <= number <= len(self.sent_emails):
            email = self.sent_emails[number-1]
            
            result = "\n📧 EMAIL DETAILS:\n"
            result += "="*40 + "\n\n"
            result += f"📌 Subject: {email['subject']}\n\n"
            result += "📝 Body:\n"
            result += "-"*30 + "\n"
            result += email['body'] + "\n"
            result += "-"*30 + "\n"
            
            return result
        return "❌ Invalid email number."
    
    def add_custom_template(self, name, subject, body):
        """Add a custom template"""
        key = name.lower().replace(" ", "_")
        self.templates[key] = {
            "name": name,
            "subject": subject,
            "body": body
        }
        self.save_templates()
        return f"✅ Custom template '{name}' added! Use key: {key}"
    
    def delete_template(self, key):
        """Delete a template"""
        if key in self.templates:
            # Don't delete default templates
            if key in ["meeting", "followup", "thankyou", "sickday", "late", "introduction"]:
                return "❌ Cannot delete default templates."
            del self.templates[key]
            self.save_templates()
            return f"🗑️ Template '{key}' deleted."
        return f"❌ Template '{key}' not found."

# Run the email helper
if __name__ == "__main__":
    helper = EmailHelper()
    
    print("\n" + "="*50)
    print("📧 EMAIL WRITING HELPER")
    print("="*50)
    print("\nI can help you write professional emails quickly!")
    
    while True:
        print("\n" + "-"*50)
        print("COMMANDS:")
        print("  templates           - See all email templates")
        print("  preview [key]       - Preview a template")
        print("  use [key]           - Create email from template")
        print("  sent                - See recently created emails")
        print("  view [number]       - View a sent email")
        print("  new template        - Create your own template")
        print("  delete template [key] - Delete a custom template")
        print("  help                - Show this menu")
        print("  quit                - Exit")
        print("-"*50)
        
        command = input("\n> ").strip().lower()
        
        if command == 'quit':
            print("\n👋 Goodbye! Happy emailing!")
            break
        
        elif command == 'help':
            continue  # Menu already shows
        
        elif command == 'templates':
            print(helper.list_templates())
        
        elif command.startswith('preview '):
            key = command[8:].strip()
            print(helper.preview_template(key))
        
        elif command.startswith('use '):
            key = command[4:].strip()
            
            if key not in helper.templates:
                print(f"❌ Template '{key}' not found.")
                continue
            
            print(helper.preview_template(key))
            print("\n📝 Now let's fill in the placeholders...")
            
            # Get replacements
            replacements = {}
            
            if key == "meeting":
                replacements['Name'] = input("Recipient name: ")
                replacements['Topic'] = input("Meeting topic: ")
                replacements['Date'] = input("Proposed date: ")
                replacements['Time'] = input("Proposed time: ")
                replacements['Your Name'] = input("Your name: ")
            
            elif key == "followup":
                replacements['Name'] = input("Recipient name: ")
                replacements['Topic'] = input("Topic you're following up on: ")
                replacements['Your Name'] = input("Your name: ")
            
            elif key == "thankyou":
                replacements['Name'] = input("Recipient name: ")
                replacements['Topic'] = input("What you're thanking them for (short): ")
                replacements['what they did'] = input("What did they do? ")
                replacements['Your Name'] = input("Your name: ")
            
            elif key == "sickday":
                replacements['Name'] = input("Manager's name: ")
                replacements['Date'] = input("Date (today): ")
                replacements['Your Name'] = input("Your name: ")
            
            elif key == "late":
                replacements['Name'] = input("Manager's name: ")
                replacements['reason'] = input("Reason for being late: ")
                replacements['time'] = input("Expected arrival time: ")
                replacements['Your Name'] = input("Your name: ")
            
            elif key == "introduction":
                replacements['Name'] = input("Recipient name: ")
                replacements['Your Name'] = input("Your name: ")
                replacements['Their Name'] = replacements['Name']
                replacements['your role/position'] = input("Your role/position: ")
                replacements['reason for contacting them'] = input("Reason for reaching out: ")
                replacements['topic or their work'] = input("What topic/their work interests you? ")
            
            else:
                # For custom templates
                import re
                placeholders = re.findall(r'\[(.*?)\]', helper.templates[key]['subject'] + ' ' + helper.templates[key]['body'])
                for p in set(placeholders):
                    replacements[p] = input(f"{p}: ")
            
            print(helper.create_email(key, replacements))
        
        elif command == 'sent':
            print(helper.show_sent())
        
        elif command.startswith('view '):
            try:
                num = int(command[5:])
                print(helper.view_sent_email(num))
            except:
                print("❌ Use: view [number]")
        
        elif command == 'new template':
            print("\n📝 CREATE CUSTOM TEMPLATE")
            print("Use [placeholder] for parts that change each time")
            print("Example: Hi [Name], regarding [Topic]...\n")
            
            name = input("Template name: ")
            subject = input("Subject line: ")
            print("Body (type 'DONE' on a new line when finished):")
            
            body_lines = []
            while True:
                line = input()
                if line == 'DONE':
                    break
                body_lines.append(line)
            
            body = "\n".join(body_lines)
            print(helper.add_custom_template(name, subject, body))
        
        elif command.startswith('delete template '):
            key = command[16:].strip()
            print(helper.delete_template(key))
        
        else:
            print("❌ Unknown command. Type 'help' to see options.")