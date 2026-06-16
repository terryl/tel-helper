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
