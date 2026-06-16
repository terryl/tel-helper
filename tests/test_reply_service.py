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


def test_update_rule(app):
    with app.app_context():
        from services.reply_service import ReplyService
        account = Account(phone='+1234567890', session_name='test')
        db.session.add(account)
        db.session.commit()

        rule = ReplyService.create_rule(account.id, 'hello', 'Hi!')
        ReplyService.update_rule(rule.id, keyword='bye', reply_text='Goodbye!')

        updated = AutoReply.query.get(rule.id)
        assert updated.keyword == 'bye'
        assert updated.reply_text == 'Goodbye!'


def test_delete_rule(app):
    with app.app_context():
        from services.reply_service import ReplyService
        account = Account(phone='+1234567890', session_name='test')
        db.session.add(account)
        db.session.commit()

        rule = ReplyService.create_rule(account.id, 'hello', 'Hi!')
        ReplyService.delete_rule(rule.id)
        assert AutoReply.query.get(rule.id) is None
