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
                    is_online=getattr(member.user, 'status', None) is not None,
                    last_seen=getattr(member.user.status, 'last_seen', None)
                )
                count += 1
            
            return {'group': chat.title, 'members_scanned': count}
