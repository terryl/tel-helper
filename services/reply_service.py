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
