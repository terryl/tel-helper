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
