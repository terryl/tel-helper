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


def test_get_messages_by_account(app):
    with app.app_context():
        from services.message_service import MessageService
        account = Account(phone='+1234567890', session_name='test')
        db.session.add(account)
        db.session.commit()

        MessageService.create_message(account.id, '@user1', 'msg1')
        MessageService.create_message(account.id, '@user2', 'msg2')
        messages = MessageService.get_messages_by_account(account.id)
        assert len(messages) == 2


def test_get_pending_messages(app):
    with app.app_context():
        from services.message_service import MessageService
        account = Account(phone='+1234567890', session_name='test')
        db.session.add(account)
        db.session.commit()

        MessageService.create_message(account.id, '@user1', 'msg1')
        pending = MessageService.get_pending_messages()
        assert len(pending) == 1
