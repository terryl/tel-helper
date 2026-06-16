# Telegram Helper Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use compose:subagent (recommended) or compose:execute to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Telegram helper tool with mass messaging, auto-reply, group member scanning, and multi-account management via a Flask web interface.

**Architecture:** Pyrogram (Telegram Client API) + Flask (Web UI) + SQLite (data storage). Modular design with separate services for each feature.

**Tech Stack:** Python 3.10+, Pyrogram, Flask, SQLAlchemy, SQLite, Jinja2, Bootstrap 5

---

## File Structure

```
tel-helper/
├── app.py                    # Flask application entry point
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── models.py                 # SQLAlchemy database models
├── services/
│   ├── __init__.py
│   ├── account_service.py    # Multi-account management
│   ├── message_service.py    # Mass messaging logic
│   ├── reply_service.py      # Auto-reply logic
│   └── scanner_service.py    # Group member scanning
├── routes/
│   ├── __init__.py
│   ├── account_routes.py     # Account management endpoints
│   ├── message_routes.py     # Mass messaging endpoints
│   ├── reply_routes.py       # Auto-reply endpoints
│   └── scanner_routes.py     # Group scanning endpoints
├── templates/
│   ├── base.html             # Base template with navigation
│   ├── accounts/
│   │   ├── list.html         # Account list page
│   │   └── login.html        # Account login page
│   ├── messages/
│   │   ├── compose.html      # Compose mass message
│   │   └── history.html      # Message history
│   ├── replies/
│   │   ├── rules.html        # Auto-reply rules list
│   │   └── edit_rule.html    # Edit auto-reply rule
│   └── scanner/
│       └── results.html      # Scanned group members
├── static/
│   └── css/
│       └── style.css         # Custom styles
└── tests/
    ├── __init__.py
    ├── test_account_service.py
    ├── test_message_service.py
    ├── test_reply_service.py
    └── test_scanner_service.py
```

---

## Task 1: Project Setup and Dependencies

**Covers:** S1 (Project foundation)

**Files:**
- Create: `requirements.txt`
- Create: `config.py`
- Create: `app.py`

- [ ] **Step 1: Create requirements.txt**

```
pyrogram>=2.0.0
tgcrypto>=1.2.0
flask>=3.0.0
flask-sqlalchemy>=3.1.0
flask-migrate>=4.0.0
apscheduler>=3.10.0
python-dotenv>=1.0.0
```

- [ ] **Step 2: Create config.py**

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///telegram_helper.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    API_ID = int(os.getenv('API_ID', '0'))
    API_HASH = os.getenv('API_HASH', '')
    SESSIONS_DIR = os.getenv('SESSIONS_DIR', 'sessions')
```

- [ ] **Step 3: Create app.py**

```python
from flask import Flask
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    from routes.account_routes import account_bp
    from routes.message_routes import message_bp
    from routes.reply_routes import reply_bp
    from routes.scanner_routes import scanner_bp
    
    app.register_blueprint(account_bp, url_prefix='/accounts')
    app.register_blueprint(message_bp, url_prefix='/messages')
    app.register_blueprint(reply_bp, url_prefix='/replies')
    app.register_blueprint(scanner_bp, url_prefix='/scanner')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

- [ ] **Step 4: Install dependencies and verify**

Run: `pip install -r requirements.txt`
Expected: Successful installation without errors

- [ ] **Step 5: Create .env file**

```
SECRET_KEY=your-secret-key-here
API_ID=your-api-id
API_HASH=your-api-hash
```

- [ ] **Step 6: Commit**

```bash
git add requirements.txt config.py app.py .env
git commit -m "feat: initial project setup with Flask and Pyrogram"
```

---

## Task 2: Database Models

**Covers:** S2 (Data layer)

**Files:**
- Create: `models.py`

- [ ] **Step 1: Create models.py**

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(100))
    session_name = db.Column(db.String(100), unique=True, nullable=False)
    is_active = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    messages = db.relationship('Message', backref='account', lazy='dynamic')
    replies = db.relationship('AutoReply', backref='account', lazy='dynamic')

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    recipient = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')
    status = db.Column(db.String(20), default='pending')
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AutoReply(db.Model):
    __tablename__ = 'auto_replies'
    
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    keyword = db.Column(db.String(200), nullable=False)
    reply_text = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ScannedMember(db.Model):
    __tablename__ = 'scanned_members'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String(100), nullable=False)
    group_name = db.Column(db.String(200))
    user_id = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime)
    scanned_at = db.Column(db.DateTime, default=datetime.utcnow)
```

- [ ] **Step 2: Verify models load correctly**

Run: `python -c "from models import db; print('Models loaded successfully')"`
Expected: "Models loaded successfully"

- [ ] **Step 3: Commit**

```bash
git add models.py
git commit -m "feat: add database models for accounts, messages, replies, and members"
```

---

## Task 3: Account Service

**Covers:** S3 (Multi-account management)

**Files:**
- Create: `services/__init__.py`
- Create: `services/account_service.py`
- Create: `tests/test_account_service.py`

- [ ] **Step 1: Create services/__init__.py**

```python
```

- [ ] **Step 2: Create tests/test_account_service.py**

```python
import pytest
from app import create_app
from models import db, Account

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_account_creation(app):
    with app.app_context():
        from services.account_service import AccountService
        account = AccountService.create_account(
            phone='+1234567890',
            session_name='test_session'
        )
        assert account is not None
        assert account.phone == '+1234567890'
```

- [ ] **Step 3: Run test to verify it fails**

Run: `pytest tests/test_account_service.py -v`
Expected: FAIL with "AccountService not defined"

- [ ] **Step 4: Create services/account_service.py**

```python
from models import db, Account
from pyrogram import Client
import os

class AccountService:
    @staticmethod
    def create_account(phone, session_name, api_id=None, api_hash=None):
        account = Account(
            phone=phone,
            session_name=session_name,
            is_active=False
        )
        db.session.add(account)
        db.session.commit()
        return account
    
    @staticmethod
    def get_all_accounts():
        return Account.query.all()
    
    @staticmethod
    def get_account_by_id(account_id):
        return Account.query.get_or_404(account_id)
    
    @staticmethod
    def get_active_accounts():
        return Account.query.filter_by(is_active=True).all()
    
    @staticmethod
    def delete_account(account_id):
        account = Account.query.get_or_404(account_id)
        session_file = f"{account.session_name}.session"
        if os.path.exists(session_file):
            os.remove(session_file)
        db.session.delete(account)
        db.session.commit()
    
    @staticmethod
    async def login_account(account_id, phone_code=None):
        from config import Config
        account = Account.query.get_or_404(account_id)
        
        client = Client(
            name=account.session_name,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH
        )
        
        if phone_code:
            await client.sign_in(account.phone, phone_code)
            account.is_active = True
            db.session.commit()
        
        return client
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pytest tests/test_account_service.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add services/__init__.py services/account_service.py tests/test_account_service.py
git commit -m "feat: add account service with CRUD operations"
```

---

## Task 4: Message Service

**Covers:** S4 (Mass messaging)

**Files:**
- Create: `services/message_service.py`
- Create: `tests/test_message_service.py`

- [ ] **Step 1: Create tests/test_message_service.py**

```python
import pytest
from app import create_app
from models import db, Account, Message

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_message_creation(app):
    with app.app_context():
        from services.message_service import MessageService
        account = Account(phone='+1234567890', session_name='test')
        db.session.add(account)
        db.session.commit()
        
        message = MessageService.create_message(
            account_id=account.id,
            recipient='@username',
            content='Hello!'
        )
        assert message is not None
        assert message.status == 'pending'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_message_service.py -v`
Expected: FAIL with "MessageService not defined"

- [ ] **Step 3: Create services/message_service.py**

```python
from models import db, Message, Account
from datetime import datetime

class MessageService:
    @staticmethod
    def create_message(account_id, recipient, content, message_type='text', scheduled_at=None):
        message = Message(
            account_id=account_id,
            recipient=recipient,
            content=content,
            message_type=message_type,
            scheduled_at=scheduled_at
        )
        db.session.add(message)
        db.session.commit()
        return message
    
    @staticmethod
    def get_messages_by_account(account_id):
        return Message.query.filter_by(account_id=account_id).all()
    
    @staticmethod
    def get_pending_messages():
        return Message.query.filter_by(status='pending').all()
    
    @staticmethod
    async def send_message(message_id):
        from pyrogram import Client
        from config import Config
        
        message = Message.query.get_or_404(message_id)
        account = Account.query.get_or_404(message.account_id)
        
        client = Client(
            name=account.session_name,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH
        )
        
        async with client:
            await client.send_message(message.recipient, message.content)
            message.status = 'sent'
            message.sent_at = datetime.utcnow()
            db.session.commit()
    
    @staticmethod
    async def send_mass_messages(account_id, recipients, content):
        results = []
        for recipient in recipients:
            message = MessageService.create_message(
                account_id=account_id,
                recipient=recipient,
                content=content
            )
            try:
                await MessageService.send_message(message.id)
                results.append({'recipient': recipient, 'status': 'sent'})
            except Exception as e:
                results.append({'recipient': recipient, 'status': 'failed', 'error': str(e)})
        return results
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_message_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/message_service.py tests/test_message_service.py
git commit -m "feat: add message service with mass messaging"
```

---

## Task 5: Auto-Reply Service

**Covers:** S5 (Auto-reply)

**Files:**
- Create: `services/reply_service.py`
- Create: `tests/test_reply_service.py`

- [ ] **Step 1: Create tests/test_reply_service.py**

```python
import pytest
from app import create_app
from models import db, Account, AutoReply

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_reply_rule_creation(app):
    with app.app_context():
        from services.reply_service import ReplyService
        account = Account(phone='+1234567890', session_name='test')
        db.session.add(account)
        db.session.commit()
        
        rule = ReplyService.create_rule(
            account_id=account.id,
            keyword='hello',
            reply_text='Hi there!'
        )
        assert rule is not None
        assert rule.keyword == 'hello'

def test_keyword_matching(app):
    with app.app_context():
        from services.reply_service import ReplyService
        account = Account(phone='+1234567890', session_name='test')
        db.session.add(account)
        db.session.commit()
        
        ReplyService.create_rule(account.id, 'hello', 'Hi!')
        ReplyService.create_rule(account.id, 'help', 'How can I help?')
        
        reply = ReplyService.match_keyword('hello world')
        assert reply == 'Hi!'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_reply_service.py -v`
Expected: FAIL with "ReplyService not defined"

- [ ] **Step 3: Create services/reply_service.py**

```python
from models import db, AutoReply

class ReplyService:
    @staticmethod
    def create_rule(account_id, keyword, reply_text):
        rule = AutoReply(
            account_id=account_id,
            keyword=keyword.lower(),
            reply_text=reply_text
        )
        db.session.add(rule)
        db.session.commit()
        return rule
    
    @staticmethod
    def get_rules_by_account(account_id):
        return AutoReply.query.filter_by(account_id=account_id).all()
    
    @staticmethod
    def get_active_rules_by_account(account_id):
        return AutoReply.query.filter_by(account_id=account_id, is_active=True).all()
    
    @staticmethod
    def update_rule(rule_id, keyword=None, reply_text=None, is_active=None):
        rule = AutoReply.query.get_or_404(rule_id)
        if keyword is not None:
            rule.keyword = keyword.lower()
        if reply_text is not None:
            rule.reply_text = reply_text
        if is_active is not None:
            rule.is_active = is_active
        db.session.commit()
        return rule
    
    @staticmethod
    def delete_rule(rule_id):
        rule = AutoReply.query.get_or_404(rule_id)
        db.session.delete(rule)
        db.session.commit()
    
    @staticmethod
    def match_keyword(message_text, account_id=None):
        query = AutoReply.query.filter_by(is_active=True)
        if account_id:
            query = query.filter_by(account_id=account_id)
        
        message_lower = message_text.lower()
        rules = query.all()
        
        for rule in rules:
            if rule.keyword in message_lower:
                return rule.reply_text
        return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_reply_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/reply_service.py tests/test_reply_service.py
git commit -m "feat: add auto-reply service with keyword matching"
```

---

## Task 6: Scanner Service

**Covers:** S6 (Group member scanning)

**Files:**
- Create: `services/scanner_service.py`
- Create: `tests/test_scanner_service.py`

- [ ] **Step 1: Create tests/test_scanner_service.py**

```python
import pytest
from app import create_app
from models import db, Account, ScannedMember

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_member_storage(app):
    with app.app_context():
        from services.scanner_service import ScannerService
        member = ScannerService.store_member(
            group_id='123456',
            group_name='Test Group',
            user_id='789',
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        assert member is not None
        assert member.group_id == '123456'
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_scanner_service.py -v`
Expected: FAIL with "ScannerService not defined"

- [ ] **Step 3: Create services/scanner_service.py**

```python
from models import db, ScannedMember, Account
from datetime import datetime

class ScannerService:
    @staticmethod
    def store_member(group_id, group_name, user_id, username=None, 
                     first_name=None, last_name=None, is_online=False, last_seen=None):
        existing = ScannedMember.query.filter_by(
            group_id=group_id, 
            user_id=user_id
        ).first()
        
        if existing:
            existing.username = username or existing.username
            existing.first_name = first_name or existing.first_name
            existing.last_name = last_name or existing.last_name
            existing.is_online = is_online
            existing.last_seen = last_seen or existing.last_seen
            existing.scanned_at = datetime.utcnow()
            db.session.commit()
            return existing
        
        member = ScannedMember(
            group_id=group_id,
            group_name=group_name,
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_online=is_online,
            last_seen=last_seen
        )
        db.session.add(member)
        db.session.commit()
        return member
    
    @staticmethod
    def get_members_by_group(group_id):
        return ScannedMember.query.filter_by(group_id=group_id).all()
    
    @staticmethod
    def get_all_groups():
        groups = db.session.query(
            ScannedMember.group_id, 
            ScannedMember.group_name
        ).distinct().all()
        return [{'id': g[0], 'name': g[1]} for g in groups]
    
    @staticmethod
    def export_members_csv(group_id):
        import csv
        import io
        
        members = ScannerService.get_members_by_group(group_id)
        
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['User ID', 'Username', 'First Name', 'Last Name', 'Online', 'Last Seen'])
        
        for member in members:
            writer.writerow([
                member.user_id,
                member.username or '',
                member.first_name or '',
                member.last_name or '',
                member.is_online,
                member.last_seen or ''
            ])
        
        return output.getvalue()
    
    @staticmethod
    async def scan_group(account_id, group_identifier):
        from pyrogram import Client
        from config import Config
        
        account = Account.query.get_or_404(account_id)
        
        client = Client(
            name=account.session_name,
            api_id=Config.API_ID,
            api_hash=Config.API_HASH
        )
        
        async with client:
            chat = await client.get_chat(group_identifier)
            count = 0
            
            async for member in client.get_chat_members(chat.id):
                ScannerService.store_member(
                    group_id=str(chat.id),
                    group_name=chat.title,
                    user_id=str(member.user.id),
                    username=member.user.username,
                    first_name=member.user.first_name,
                    last_name=member.user.last_name,
                    is_online=member.user.status is not None and member.user.status在线,
                    last_seen=getattr(member.user.status, 'last_seen', None)
                )
                count += 1
            
            return {'group': chat.title, 'members_scanned': count}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_scanner_service.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/scanner_service.py tests/test_scanner_service.py
git commit -m "feat: add scanner service for group member scanning"
```

---

## Task 7: Flask Routes

**Covers:** S7 (Web interface - routes)

**Files:**
- Create: `routes/__init__.py`
- Create: `routes/account_routes.py`
- Create: `routes/message_routes.py`
- Create: `routes/reply_routes.py`
- Create: `routes/scanner_routes.py`

- [ ] **Step 1: Create routes/__init__.py**

```python
```

- [ ] **Step 2: Create routes/account_routes.py**

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.account_service import AccountService

account_bp = Blueprint('accounts', __name__)

@account_bp.route('/')
def list_accounts():
    accounts = AccountService.get_all_accounts()
    return render_template('accounts/list.html', accounts=accounts)

@account_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        phone = request.form.get('phone')
        session_name = request.form.get('session_name')
        account = AccountService.create_account(phone, session_name)
        flash('Account created. Please login via Telegram.', 'success')
        return redirect(url_for('accounts.list_accounts'))
    return render_template('accounts/login.html')

@account_bp.route('/delete/<int:account_id>', methods=['POST'])
def delete(account_id):
    AccountService.delete_account(account_id)
    flash('Account deleted.', 'success')
    return redirect(url_for('accounts.list_accounts'))
```

- [ ] **Step 3: Create routes/message_routes.py**

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.message_service import MessageService
from services.account_service import AccountService

message_bp = Blueprint('messages', __name__)

@message_bp.route('/')
def history():
    accounts = AccountService.get_all_accounts()
    return render_template('messages/history.html', accounts=accounts)

@message_bp.route('/compose', methods=['GET', 'POST'])
def compose():
    accounts = AccountService.get_active_accounts()
    if request.method == 'POST':
        account_id = request.form.get('account_id')
        recipients = request.form.get('recipients').split('\n')
        content = request.form.get('content')
        
        import asyncio
        results = asyncio.run(MessageService.send_mass_messages(
            account_id=int(account_id),
            recipients=[r.strip() for r in recipients if r.strip()],
            content=content
        ))
        
        sent = sum(1 for r in results if r['status'] == 'sent')
        flash(f'Messages sent: {sent}/{len(results)}', 'success')
        return redirect(url_for('messages.history'))
    
    return render_template('messages/compose.html', accounts=accounts)
```

- [ ] **Step 4: Create routes/reply_routes.py**

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.reply_service import ReplyService
from services.account_service import AccountService

reply_bp = Blueprint('replies', __name__)

@reply_bp.route('/')
def rules():
    accounts = AccountService.get_all_accounts()
    return render_template('replies/rules.html', accounts=accounts)

@reply_bp.route('/edit/<int:rule_id>', methods=['GET', 'POST'])
def edit_rule(rule_id):
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        reply_text = request.form.get('reply_text')
        is_active = 'is_active' in request.form
        ReplyService.update_rule(rule_id, keyword, reply_text, is_active)
        flash('Rule updated.', 'success')
        return redirect(url_for('replies.rules'))
    
    from models import AutoReply
    rule = AutoReply.query.get_or_404(rule_id)
    return render_template('replies/edit_rule.html', rule=rule)

@reply_bp.route('/create', methods=['POST'])
def create_rule():
    account_id = request.form.get('account_id')
    keyword = request.form.get('keyword')
    reply_text = request.form.get('reply_text')
    ReplyService.create_rule(int(account_id), keyword, reply_text)
    flash('Rule created.', 'success')
    return redirect(url_for('replies.rules'))

@reply_bp.route('/delete/<int:rule_id>', methods=['POST'])
def delete_rule(rule_id):
    ReplyService.delete_rule(rule_id)
    flash('Rule deleted.', 'success')
    return redirect(url_for('replies.rules'))
```

- [ ] **Step 5: Create routes/scanner_routes.py**

```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from services.scanner_service import ScannerService
from services.account_service import AccountService

scanner_bp = Blueprint('scanner', __name__)

@scanner_bp.route('/')
def results():
    groups = ScannerService.get_all_groups()
    return render_template('scanner/results.html', groups=groups)

@scanner_bp.route('/group/<group_id>')
def group_members(group_id):
    members = ScannerService.get_members_by_group(group_id)
    return render_template('scanner/results.html', members=members, group_id=group_id)

@scanner_bp.route('/export/<group_id>')
def export_csv(group_id):
    csv_data = ScannerService.export_members_csv(group_id)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=group_{group_id}_members.csv'}
    )

@scanner_bp.route('/scan', methods=['POST'])
def scan():
    account_id = request.form.get('account_id')
    group_identifier = request.form.get('group_identifier')
    
    import asyncio
    result = asyncio.run(ScannerService.scan_group(int(account_id), group_identifier))
    
    flash(f"Scanned {result['members_scanned']} members from {result['group']}", 'success')
    return redirect(url_for('scanner.results'))
```

- [ ] **Step 6: Commit**

```bash
git add routes/
git commit -m "feat: add Flask routes for all features"
```

---

## Task 8: HTML Templates

**Covers:** S7 (Web interface - templates)

**Files:**
- Create: `templates/base.html`
- Create: `templates/accounts/list.html`
- Create: `templates/accounts/login.html`
- Create: `templates/messages/compose.html`
- Create: `templates/messages/history.html`
- Create: `templates/replies/rules.html`
- Create: `templates/replies/edit_rule.html`
- Create: `templates/scanner/results.html`
- Create: `static/css/style.css`

- [ ] **Step 1: Create templates/base.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Telegram Helper{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="{{ url_for('static', filename='css/style.css') }}" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">Telegram Helper</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/accounts/">账号管理</a>
                <a class="nav-link" href="/messages/">群发消息</a>
                <a class="nav-link" href="/replies/">自动回复</a>
                <a class="nav-link" href="/scanner/">成员扫描</a>
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create templates/accounts/list.html**

```html
{% extends "base.html" %}
{% block title %}账号管理{% endblock %}
{% block content %}
<h2>账号管理</h2>
<a href="{{ url_for('accounts.login') }}" class="btn btn-primary mb-3">添加账号</a>

<table class="table">
    <thead>
        <tr>
            <th>手机号</th>
            <th>用户名</th>
            <th>状态</th>
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        {% for account in accounts %}
        <tr>
            <td>{{ account.phone }}</td>
            <td>{{ account.username or '-' }}</td>
            <td>
                <span class="badge {{ 'bg-success' if account.is_active else 'bg-secondary' }}">
                    {{ '已激活' if account.is_active else '未激活' }}
                </span>
            </td>
            <td>
                <form method="post" action="{{ url_for('accounts.delete', account_id=account.id) }}" style="display:inline">
                    <button type="submit" class="btn btn-danger btn-sm" onclick="return confirm('确定删除？')">删除</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

- [ ] **Step 3: Create templates/accounts/login.html**

```html
{% extends "base.html" %}
{% block title %}添加账号{% endblock %}
{% block content %}
<h2>添加 Telegram 账号</h2>
<form method="post">
    <div class="mb-3">
        <label class="form-label">手机号</label>
        <input type="text" class="form-control" name="phone" required placeholder="+8613800138000">
    </div>
    <div class="mb-3">
        <label class="form-label">Session 名称</label>
        <input type="text" class="form-control" name="session_name" required placeholder="my_account">
    </div>
    <button type="submit" class="btn btn-primary">创建</button>
    <a href="{{ url_for('accounts.list_accounts') }}" class="btn btn-secondary">取消</a>
</form>
{% endblock %}
```

- [ ] **Step 4: Create templates/messages/compose.html**

```html
{% extends "base.html" %}
{% block title %}群发消息{% endblock %}
{% block content %}
<h2>群发消息</h2>
<form method="post">
    <div class="mb-3">
        <label class="form-label">选择账号</label>
        <select class="form-select" name="account_id" required>
            {% for account in accounts %}
            <option value="{{ account.id }}">{{ account.phone }} - {{ account.username or '未设置用户名' }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="mb-3">
        <label class="form-label">接收者（每行一个，用户名或用户ID）</label>
        <textarea class="form-control" name="recipients" rows="5" required placeholder="@user1&#10;@user2&#10;123456789"></textarea>
    </div>
    <div class="mb-3">
        <label class="form-label">消息内容</label>
        <textarea class="form-control" name="content" rows="5" required></textarea>
    </div>
    <button type="submit" class="btn btn-primary">发送</button>
    <a href="{{ url_for('messages.history') }}" class="btn btn-secondary">取消</a>
</form>
{% endblock %}
```

- [ ] **Step 5: Create templates/messages/history.html**

```html
{% extends "base.html" %}
{% block title %}消息历史{% endblock %}
{% block content %}
<h2>消息历史</h2>
<a href="{{ url_for('messages.compose') }}" class="btn btn-primary mb-3">新建群发</a>
<p class="text-muted">消息发送记录将在此显示。</p>
{% endblock %}
```

- [ ] **Step 6: Create templates/replies/rules.html**

```html
{% extends "base.html" %}
{% block title %}自动回复规则{% endblock %}
{% block content %}
<h2>自动回复规则</h2>

<div class="card mb-4">
    <div class="card-header">添加新规则</div>
    <div class="card-body">
        <form method="post" action="{{ url_for('replies.create_rule') }}">
            <div class="row">
                <div class="col-md-3">
                    <select class="form-select" name="account_id" required>
                        {% for account in accounts %}
                        <option value="{{ account.id }}">{{ account.phone }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-3">
                    <input type="text" class="form-control" name="keyword" placeholder="关键词" required>
                </div>
                <div class="col-md-4">
                    <input type="text" class="form-control" name="reply_text" placeholder="回复内容" required>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">添加</button>
                </div>
            </div>
        </form>
    </div>
</div>

<table class="table">
    <thead>
        <tr>
            <th>账号</th>
            <th>关键词</th>
            <th>回复内容</th>
            <th>状态</th>
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        {% for account in accounts %}
            {% for rule in account.replies %}
            <tr>
                <td>{{ account.phone }}</td>
                <td>{{ rule.keyword }}</td>
                <td>{{ rule.reply_text }}</td>
                <td>
                    <span class="badge {{ 'bg-success' if rule.is_active else 'bg-secondary' }}">
                        {{ '启用' if rule.is_active else '禁用' }}
                    </span>
                </td>
                <td>
                    <a href="{{ url_for('replies.edit_rule', rule_id=rule.id) }}" class="btn btn-sm btn-outline-primary">编辑</a>
                    <form method="post" action="{{ url_for('replies.delete_rule', rule_id=rule.id) }}" style="display:inline">
                        <button type="submit" class="btn btn-sm btn-outline-danger">删除</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

- [ ] **Step 7: Create templates/replies/edit_rule.html**

```html
{% extends "base.html" %}
{% block title %}编辑规则{% endblock %}
{% block content %}
<h2>编辑自动回复规则</h2>
<form method="post">
    <div class="mb-3">
        <label class="form-label">关键词</label>
        <input type="text" class="form-control" name="keyword" value="{{ rule.keyword }}" required>
    </div>
    <div class="mb-3">
        <label class="form-label">回复内容</label>
        <textarea class="form-control" name="reply_text" rows="3" required>{{ rule.reply_text }}</textarea>
    </div>
    <div class="mb-3 form-check">
        <input type="checkbox" class="form-check-input" name="is_active" {{ 'checked' if rule.is_active }}>
        <label class="form-check-label">启用规则</label>
    </div>
    <button type="submit" class="btn btn-primary">保存</button>
    <a href="{{ url_for('replies.rules') }}" class="btn btn-secondary">取消</a>
</form>
{% endblock %}
```

- [ ] **Step 8: Create templates/scanner/results.html**

```html
{% extends "base.html" %}
{% block title %}成员扫描{% endblock %}
{% block content %}
<h2>群成员扫描</h2>

<div class="card mb-4">
    <div class="card-header">扫描新群组</div>
    <div class="card-body">
        <form method="post" action="{{ url_for('scanner.scan') }}">
            <div class="row">
                <div class="col-md-4">
                    <select class="form-select" name="account_id" required>
                        {% for account in accounts %}
                        <option value="{{ account.id }}">{{ account.phone }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-6">
                    <input type="text" class="form-control" name="group_identifier" placeholder="群组链接或ID" required>
                </div>
                <div class="col-md-2">
                    <button type="submit" class="btn btn-primary w-100">扫描</button>
                </div>
            </div>
        </form>
    </div>
</div>

{% if groups %}
<h3>已扫描的群组</h3>
<div class="list-group mb-4">
    {% for group in groups %}
    <a href="{{ url_for('scanner.group_members', group_id=group.id) }}" class="list-group-item list-group-item-action">
        {{ group.name or group.id }}
    </a>
    {% endfor %}
</div>
{% endif %}

{% if members %}
<h3>群组成员 ({{ members|length }})</h3>
<a href="{{ url_for('scanner.export_csv', group_id=group_id) }}" class="btn btn-success mb-3">导出 CSV</a>
<table class="table">
    <thead>
        <tr>
            <th>用户ID</th>
            <th>用户名</th>
            <th>姓名</th>
            <th>在线状态</th>
            <th>最后在线</th>
        </tr>
    </thead>
    <tbody>
        {% for member in members %}
        <tr>
            <td>{{ member.user_id }}</td>
            <td>{{ member.username or '-' }}</td>
            <td>{{ member.first_name }} {{ member.last_name or '' }}</td>
            <td>
                <span class="badge {{ 'bg-success' if member.is_online else 'bg-secondary' }}">
                    {{ '在线' if member.is_online else '离线' }}
                </span>
            </td>
            <td>{{ member.last_seen or '-' }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endif %}
{% endblock %}
```

- [ ] **Step 9: Create static/css/style.css**

```css
body {
    background-color: #f8f9fa;
}

.navbar-brand {
    font-weight: bold;
}

.card {
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.table th {
    background-color: #e9ecef;
}
```

- [ ] **Step 10: Commit**

```bash
git add templates/ static/
git commit -m "feat: add HTML templates and CSS for web interface"
```

---

## Task 9: Final Integration and Testing

**Covers:** S8 (Integration)

**Files:**
- Modify: `app.py` (if needed)

- [ ] **Step 1: Run all tests**

Run: `pytest tests/ -v`
Expected: All tests pass

- [ ] **Step 2: Start the application**

Run: `python app.py`
Expected: Flask server starts without errors

- [ ] **Step 3: Verify web interface**

Open browser to `http://localhost:5000`
Expected: Home page loads, navigation works

- [ ] **Step 4: Create README.md**

```markdown
# Telegram Helper Tool

Telegram 辅助工具，支持群发消息、自动回复、群成员扫描和多账号管理。

## 功能

- **多账号管理**: 添加和管理多个 Telegram 账号
- **群发消息**: 向多个用户批量发送消息
- **自动回复**: 根据关键词自动回复消息
- **群成员扫描**: 扫描群组成员并导出数据

## 安装

```bash
pip install -r requirements.txt
```

## 配置

创建 `.env` 文件：

```
SECRET_KEY=your-secret-key
API_ID=your-api-id
API_HASH=your-api-hash
```

获取 API ID 和 Hash: https://my.telegram.org

## 运行

```bash
python app.py
```

访问 http://localhost:5000
```

- [ ] **Step 5: Final commit**

```bash
git add README.md
git commit -m "docs: add README with setup instructions"
```
