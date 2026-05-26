"""
WEB APP - Your Personal Assistant in the Browser!
Now with AI Chat, Reminders, Finance, and Email!
"""

from flask import Flask, render_template_string, request, jsonify, session
from reminder_system import ReminderSystem
from finance_tracker import FinanceTracker
from email_helper import EmailHelper
from ai_chat_bot import AIChatBot
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'my-assistant-secret-key-change-me')

# Initialize your tools
reminders = ReminderSystem()
finance = FinanceTracker()
email_helper = EmailHelper()
ai_bot = AIChatBot()

# ============================================
# HTML TEMPLATE (The webpage design)
# ============================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Personal Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 5px;
        }
        
        .header .date {
            font-size: 0.9em;
            opacity: 0.9;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .card h2 {
            font-size: 1.2em;
            margin-bottom: 15px;
            color: #333;
        }
        
        .tab-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        
        .tab-btn {
            flex: 1;
            min-width: 70px;
            padding: 12px 8px;
            border: none;
            border-radius: 10px;
            font-size: 0.85em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            background: rgba(255,255,255,0.2);
            color: white;
        }
        
        .tab-btn.active {
            background: white;
            color: #667eea;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .input-group {
            display: flex;
            gap: 10px;
            margin-bottom: 10px;
        }
        
        input, select, textarea {
            flex: 1;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            outline: none;
            transition: border 0.3s;
            font-family: inherit;
        }
        
        input:focus, select:focus, textarea:focus {
            border-color: #667eea;
        }
        
        .btn {
            padding: 12px 20px;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn-primary {
            background: #667eea;
            color: white;
        }
        
        .btn-primary:hover {
            background: #5a6fd6;
        }
        
        .btn-success {
            background: #4CAF50;
            color: white;
        }
        
        .btn-danger {
            background: #f44336;
            color: white;
        }
        
        .btn-small {
            padding: 6px 12px;
            font-size: 0.8em;
        }
        
        .list-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .list-item:last-child {
            border-bottom: none;
        }
        
        .list-item.completed {
            opacity: 0.5;
            text-decoration: line-through;
        }
        
        .summary-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        
        .summary-box h3 {
            font-size: 1.5em;
            margin-bottom: 5px;
        }
        
        .summary-details {
            display: flex;
            justify-content: space-between;
            margin-top: 10px;
        }
        
        .category-tag {
            display: inline-block;
            padding: 4px 10px;
            background: #e8e8e8;
            border-radius: 20px;
            font-size: 0.8em;
            margin: 2px;
        }
        
        .budget-bar {
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            margin-top: 5px;
            overflow: hidden;
        }
        
        .budget-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.5s;
        }
        
        .budget-fill.good {
            background: #4CAF50;
        }
        
        .budget-fill.warning {
            background: #FF9800;
        }
        
        .budget-fill.over {
            background: #f44336;
        }
        
        .email-preview {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            margin-top: 10px;
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 0.9em;
            max-height: 300px;
            overflow-y: auto;
        }
        
        /* AI Chat Styles */
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 400px;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        
        .chat-message {
            margin-bottom: 10px;
            display: flex;
            flex-direction: column;
        }
        
        .chat-message.user {
            align-items: flex-end;
        }
        
        .chat-message.assistant {
            align-items: flex-start;
        }
        
        .chat-bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 0.95em;
            line-height: 1.4;
            word-wrap: break-word;
        }
        
        .chat-bubble.user {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .chat-bubble.assistant {
            background: white;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        
        .chat-bubble .time {
            font-size: 0.7em;
            opacity: 0.7;
            margin-top: 4px;
        }
        
        .typing-indicator {
            display: none;
            padding: 12px 16px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            max-width: 80px;
        }
        
        .typing-indicator span {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #999;
            margin: 0 2px;
            animation: typing 1.4s infinite;
        }
        
        .typing-indicator span:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-indicator span:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% {
                transform: translateY(0);
                opacity: 0.4;
            }
            30% {
                transform: translateY(-10px);
                opacity: 1;
            }
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            animation: slideIn 0.3s ease;
            z-index: 1000;
        }
        
        .notification.success {
            background: #4CAF50;
        }
        
        .notification.error {
            background: #f44336;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .empty-state {
            text-align: center;
            padding: 30px;
            color: #999;
        }
        
        .empty-state .icon {
            font-size: 3em;
            margin-bottom: 10px;
        }
        
        /* Quick action chips */
        .quick-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 10px;
        }
        
        .quick-action-chip {
            padding: 8px 14px;
            background: #e8e8e8;
            border: none;
            border-radius: 20px;
            font-size: 0.8em;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .quick-action-chip:hover {
            background: #667eea;
            color: white;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 My Assistant</h1>
            <div class="date" id="currentDate"></div>
        </div>
        
        <div class="tab-buttons">
            <button class="tab-btn active" onclick="switchTab('chat')">💬 Chat</button>
            <button class="tab-btn" onclick="switchTab('reminders')">📝 Reminders</button>
            <button class="tab-btn" onclick="switchTab('finance')">💰 Finance</button>
            <button class="tab-btn" onclick="switchTab('email')">📧 Email</button>
        </div>
        
        <!-- AI CHAT TAB -->
        <div id="chat-tab" class="tab-content active">
            <div class="card">
                <h2>💬 AI Assistant</h2>
                <div class="quick-actions">
                    <button class="quick-action-chip" onclick="sendQuickMessage('Help me write a professional email')">📧 Write email</button>
                    <button class="quick-action-chip" onclick="sendQuickMessage('Give me 3 tips to save money this month')">💰 Save money</button>
                    <button class="quick-action-chip" onclick="sendQuickMessage('Suggest a healthy meal plan for today')">🍽️ Meal plan</button>
                    <button class="quick-action-chip" onclick="sendQuickMessage('Help me plan my day tomorrow')">📅 Plan day</button>
                </div>
                <div class="chat-container">
                    <div class="chat-messages" id="chatMessages">
                        <div class="chat-message assistant">
                            <div class="chat-bubble assistant">
                                Hello! I'm your AI assistant. I can help you with emails, finances, reminders, and more. What can I help you with today?
                                <div class="time" id="welcomeTime"></div>
                            </div>
                        </div>
                    </div>
                    <div class="typing-indicator" id="typingIndicator">
                        <span></span><span></span><span></span>
                    </div>
                    <div class="input-group">
                        <input type="text" id="chatInput" placeholder="Ask me anything..." onkeypress="if(event.key==='Enter')sendMessage()">
                        <button class="btn btn-primary" onclick="sendMessage()">Send</button>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- REMINDERS TAB -->
        <div id="reminders-tab" class="tab-content">
            <div class="card">
                <h2>Add Reminder</h2>
                <div class="input-group">
                    <input type="text" id="reminderText" placeholder="What do you need to remember?" onkeypress="if(event.key==='Enter')addReminder()">
                    <button class="btn btn-primary" onclick="addReminder()">Add</button>
                </div>
            </div>
            <div class="card">
                <h2>Your Reminders</h2>
                <div id="remindersList"></div>
            </div>
        </div>
        
        <!-- FINANCE TAB -->
        <div id="finance-tab" class="tab-content">
            <div class="card">
                <h2>Quick Add</h2>
                <div class="input-group">
                    <input type="number" id="amount" placeholder="Amount" step="0.01">
                    <select id="type">
                        <option value="income">💰 Income</option>
                        <option value="expense">💸 Expense</option>
                    </select>
                </div>
                <div class="input-group">
                    <input type="text" id="category" placeholder="Category (e.g., Food, Rent, Salary)">
                </div>
                <div class="input-group">
                    <input type="text" id="description" placeholder="Description (optional)">
                    <button class="btn btn-primary" onclick="addTransaction()">Add</button>
                </div>
            </div>
            <div class="card">
                <h2>Summary</h2>
                <div id="financeSummary"></div>
            </div>
        </div>
        
        <!-- EMAIL TAB -->
        <div id="email-tab" class="tab-content">
            <div class="card">
                <h2>Email Templates</h2>
                <div id="templatesList"></div>
            </div>
            <div class="card" id="emailPreviewCard" style="display:none;">
                <h2>Generated Email</h2>
                <div id="emailPreview"></div>
            </div>
        </div>
    </div>
    
    <div id="notification"></div>
    
    <script>
        // Update date
        document.getElementById('currentDate').textContent = new Date().toLocaleDateString('en-US', {
            weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
        });
        
        // Update welcome time
        document.getElementById('welcomeTime').textContent = new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
        
        // Tab switching
        function switchTab(tab) {
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tab + '-tab').classList.add('active');
            
            if (tab === 'reminders') loadReminders();
            if (tab === 'finance') loadFinanceSummary();
            if (tab === 'email') loadTemplates();
        }
        
        // Notification
        function showNotification(message, type) {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = 'notification ' + type;
            setTimeout(() => {
                notification.className = '';
                notification.textContent = '';
            }, 3000);
        }
        
        // ============================================
        // AI CHAT
        // ============================================
        
        function sendMessage() {
            const input = document.getElementById('chatInput');
            const message = input.value.trim();
            if (!message) return;
            
            // Add user message to chat
            addChatMessage(message, 'user');
            input.value = '';
            
            // Show typing indicator
            document.getElementById('typingIndicator').style.display = 'block';
            
            // Send to AI
            fetch('/api/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: message})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('typingIndicator').style.display = 'none';
                if (data.response) {
                    addChatMessage(data.response, 'assistant');
                } else if (data.error) {
                    addChatMessage('Error: ' + data.error, 'assistant');
                }
            })
            .catch(error => {
                document.getElementById('typingIndicator').style.display = 'none';
                addChatMessage('Sorry, I had trouble responding. Please try again.', 'assistant');
            });
        }
        
        function sendQuickMessage(message) {
            document.getElementById('chatInput').value = message;
            sendMessage();
        }
        
        function addChatMessage(text, role) {
            const messages = document.getElementById('chatMessages');
            const time = new Date().toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'});
            
            const messageDiv = document.createElement('div');
            messageDiv.className = 'chat-message ' + role;
            messageDiv.innerHTML = `
                <div class="chat-bubble ${role}">
                    ${text}
                    <div class="time">${time}</div>
                </div>
            `;
            
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
        
        // ============================================
        // REMINDERS
        // ============================================
        
        function addReminder() {
            const text = document.getElementById('reminderText').value.trim();
            if (!text) return;
            
            fetch('/api/reminders/add', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text})
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('reminderText').value = '';
                loadReminders();
                showNotification(data.message || 'Reminder added!', 'success');
            });
        }
        
        function loadReminders() {
            fetch('/api/reminders')
            .then(response => response.json())
            .then(data => {
                const list = document.getElementById('remindersList');
                const reminders = data.reminders || [];
                
                if (reminders.length === 0) {
                    list.innerHTML = '<div class="empty-state"><div class="icon">📝</div><p>No reminders yet!</p></div>';
                    return;
                }
                
                list.innerHTML = reminders.map((r, i) => `
                    <div class="list-item ${r.completed ? 'completed' : ''}">
                        <span>${r.completed ? '✅' : '⬜'} ${r.text}</span>
                        <div>
                            ${!r.completed ? `<button class="btn btn-success btn-small" onclick="completeReminder(${i})">Done</button>` : ''}
                            <button class="btn btn-danger btn-small" onclick="deleteReminder(${i})">🗑️</button>
                        </div>
                    </div>
                `).join('');
            });
        }
        
        function completeReminder(index) {
            fetch('/api/reminders/complete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({index: index})
            })
            .then(response => response.json())
            .then(data => {
                loadReminders();
                showNotification('Reminder completed! ✅', 'success');
            });
        }
        
        function deleteReminder(index) {
            fetch('/api/reminders/delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({index: index})
            })
            .then(response => response.json())
            .then(data => {
                loadReminders();
                showNotification('Reminder deleted!', 'success');
            });
        }
        
        // ============================================
        // FINANCE
        // ============================================
        
        function addTransaction() {
            const amount = document.getElementById('amount').value;
            const type = document.getElementById('type').value;
            const category = document.getElementById('category').value.trim();
            const description = document.getElementById('description').value.trim();
            
            if (!amount || !category) {
                showNotification('Please fill in amount and category', 'error');
                return;
            }
            
            const endpoint = type === 'income' ? '/api/finance/income' : '/api/finance/expense';
            
            fetch(endpoint, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    amount: amount,
                    category: category,
                    description: description || category
                })
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('amount').value = '';
                document.getElementById('category').value = '';
                document.getElementById('description').value = '';
                loadFinanceSummary();
                showNotification('Transaction added!', 'success');
            });
        }
        
        function loadFinanceSummary() {
            fetch('/api/finance/summary')
            .then(response => response.json())
            .then(data => {
                const summary = document.getElementById('financeSummary');
                
                if (!data.total_income && !data.total_expenses) {
                    summary.innerHTML = '<div class="empty-state"><div class="icon">💰</div><p>No transactions yet!</p></div>';
                    return;
                }
                
                let html = `
                    <div class="summary-box">
                        <h3>Balance</h3>
                        <div style="font-size: 2em; font-weight: bold;">$${(data.balance || 0).toFixed(2)}</div>
                        <div class="summary-details">
                            <div>💰 Income<br><strong>$${(data.total_income || 0).toFixed(2)}</strong></div>
                            <div>💸 Expenses<br><strong>$${(data.total_expenses || 0).toFixed(2)}</strong></div>
                        </div>
                    </div>
                `;
                
                if (data.categories && Object.keys(data.categories).length > 0) {
                    html += '<h3>By Category</h3>';
                    for (const [cat, amount] of Object.entries(data.categories)) {
                        html += `
                            <div style="margin-bottom: 10px;">
                                <span>${cat}: $${amount.toFixed(2)}</span>
                                <div class="budget-bar">
                                    <div class="budget-fill good" style="width: ${Math.min((amount / (data.total_expenses || 1)) * 100, 100)}%"></div>
                                </div>
                            </div>
                        `;
                    }
                }
                
                summary.innerHTML = html;
            });
        }
        
        // ============================================
        // EMAIL
        // ============================================
        
        function loadTemplates() {
            fetch('/api/email/templates')
            .then(response => response.json())
            .then(data => {
                const list = document.getElementById('templatesList');
                const templates = data.templates || [];
                
                list.innerHTML = templates.map(t => `
                    <div class="list-item">
                        <div>
                            <strong>${t.name}</strong>
                            <br><small style="color:#666;">${t.subject}</small>
                        </div>
                        <button class="btn btn-primary btn-small" onclick="useTemplate('${t.key}')">Use</button>
                    </div>
                `).join('');
            });
        }
        
        function useTemplate(key) {
            fetch('/api/email/preview/' + key)
            .then(response => response.json())
            .then(data => {
                const placeholders = data.placeholders || [];
                
                if (placeholders.length === 0) {
                    generateEmail(key, {});
                    return;
                }
                
                let replacements = {};
                let currentIndex = 0;
                
                function askNext() {
                    if (currentIndex >= placeholders.length) {
                        generateEmail(key, replacements);
                        return;
                    }
                    
                    const placeholder = placeholders[currentIndex];
                    const value = prompt('Please enter: ' + placeholder);
                    
                    if (value !== null) {
                        replacements[placeholder] = value;
                        currentIndex++;
                        askNext();
                    }
                }
                
                askNext();
            });
        }
        
        function generateEmail(key, replacements) {
            fetch('/api/email/generate', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    template_key: key,
                    replacements: replacements
                })
            })
            .then(response => response.json())
            .then(data => {
                const previewCard = document.getElementById('emailPreviewCard');
                const preview = document.getElementById('emailPreview');
                
                previewCard.style.display = 'block';
                preview.innerHTML = `
                    <p><strong>Subject:</strong> ${data.subject}</p>
                    <div class="email-preview">${data.body}</div>
                    <br>
                    <button class="btn btn-primary" onclick="copyEmail()">📋 Copy to Clipboard</button>
                `;
                
                preview.dataset.emailText = `Subject: ${data.subject}\\n\\n${data.body}`;
                
                showNotification('Email generated!', 'success');
                previewCard.scrollIntoView({behavior: 'smooth'});
            });
        }
        
        function copyEmail() {
            const preview = document.getElementById('emailPreview');
            const text = preview.dataset.emailText;
            
            navigator.clipboard.writeText(text).then(() => {
                showNotification('Copied to clipboard! 📋', 'success');
            });
        }
        
        // Load initial data
        loadReminders();
    </script>
</body>
</html>
"""

# ============================================
# ROUTES
# ============================================

@app.route('/')
def home():
    """Main page"""
    current_time = datetime.now().strftime('%I:%M %p')
    return render_template_string(HTML_TEMPLATE, current_time=current_time)

# ============================================
# AI CHAT ROUTE
# ============================================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Send a message to the AI chatbot"""
    data = request.get_json(silent=True)
    
    if not data:
        return jsonify({'response': '❌ Please type a message.'})
    
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'response': '❌ Please type a message first.'})
    
    try:
        response = ai_bot.get_response(message)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'response': f'❌ Error: {str(e)}'})

# ============================================
# REMINDER API ROUTES
# ============================================

@app.route('/api/reminders')
def get_reminders():
    """Get all reminders"""
    active = [r for r in reminders.reminders if not r['completed']]
    completed = [r for r in reminders.reminders if r['completed']]
    all_reminders = active + completed
    return jsonify({'reminders': all_reminders})

@app.route('/api/reminders/add', methods=['POST'])
def add_reminder():
    """Add a reminder"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Text is required'}), 400
    
    result = reminders.add_reminder(text)
    return jsonify({'message': result})

@app.route('/api/reminders/complete', methods=['POST'])
def complete_reminder():
    """Complete a reminder"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    index = data.get('index', -1)
    
    active = [r for r in reminders.reminders if not r['completed']]
    if 0 <= index < len(active):
        actual_index = reminders.reminders.index(active[index])
        result = reminders.complete_reminder(actual_index + 1)
        return jsonify({'message': result})
    
    return jsonify({'error': 'Invalid index'}), 400

@app.route('/api/reminders/delete', methods=['POST'])
def delete_reminder():
    """Delete a reminder"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    index = data.get('index', -1)
    
    active = [r for r in reminders.reminders if not r['completed']]
    if 0 <= index < len(active):
        actual_index = reminders.reminders.index(active[index])
        result = reminders.delete_reminder(actual_index + 1)
        return jsonify({'message': result})
    
    return jsonify({'error': 'Invalid index'}), 400

# ============================================
# FINANCE API ROUTES
# ============================================

@app.route('/api/finance/income', methods=['POST'])
def add_income():
    """Add income"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    amount = data.get('amount', 0)
    source = data.get('category', 'Unknown')
    result = finance.add_income(amount, source)
    return jsonify({'message': result})

@app.route('/api/finance/expense', methods=['POST'])
def add_expense():
    """Add expense"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    amount = data.get('amount', 0)
    category = data.get('category', 'Other')
    description = data.get('description', '')
    result = finance.add_expense(amount, category, description)
    return jsonify({'message': result})

@app.route('/api/finance/summary')
def finance_summary():
    """Get finance summary"""
    total_income = sum(item['amount'] for item in finance.data['income'])
    total_expenses = sum(item['amount'] for item in finance.data['expenses'])
    balance = total_income - total_expenses
    
    categories = {}
    for expense in finance.data['expenses']:
        cat = expense['category']
        categories[cat] = categories.get(cat, 0) + expense['amount']
    
    return jsonify({
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance,
        'categories': categories
    })

# ============================================
# EMAIL API ROUTES
# ============================================

@app.route('/api/email/templates')
def get_templates():
    """Get all email templates"""
    templates_list = []
    for key, template in email_helper.templates.items():
        templates_list.append({
            'key': key,
            'name': template['name'],
            'subject': template['subject']
        })
    return jsonify({'templates': templates_list})

@app.route('/api/email/preview/<key>')
def preview_template(key):
    """Preview a template and get placeholders"""
    import re
    
    if key not in email_helper.templates:
        return jsonify({'error': 'Template not found'}), 404
    
    template = email_helper.templates[key]
    placeholders = re.findall(r'\[(.*?)\]', template['subject'] + ' ' + template['body'])
    
    return jsonify({
        'name': template['name'],
        'subject': template['subject'],
        'body': template['body'],
        'placeholders': list(set(placeholders))
    })

@app.route('/api/email/generate', methods=['POST'])
def generate_email():
    """Generate an email from template"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'No data'}), 400
    
    key = data.get('template_key', '')
    replacements = data.get('replacements', {})
    
    if key not in email_helper.templates:
        return jsonify({'error': 'Template not found'}), 404
    
    template = email_helper.templates[key]
    subject = template['subject']
    body = template['body']
    
    for placeholder, value in replacements.items():
        subject = subject.replace(f"[{placeholder}]", str(value))
        body = body.replace(f"[{placeholder}]", str(value))
    
    return jsonify({
        'subject': subject,
        'body': body
    })

# ============================================
# START THE SERVER
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("🌐 YOUR WEB ASSISTANT IS STARTING!")
    print("=" * 50)
    print("\n📱 On your laptop, open:")
    print("   http://localhost:5000")
    print("\n📱 On your phone (same WiFi):")
    print("   http://YOUR_COMPUTER_IP:5000")
    print("\n💬 AI Chat tab is ready to use!")
    print("\nPress Ctrl+C to stop.\n")
    
   if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)