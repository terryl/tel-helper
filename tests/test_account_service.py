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


def test_get_all_accounts(app):
    with app.app_context():
        from services.account_service import AccountService
        AccountService.create_account('+1111111111', 'session1')
        AccountService.create_account('+2222222222', 'session2')
        accounts = AccountService.get_all_accounts()
        assert len(accounts) == 2


def test_get_active_accounts(app):
    with app.app_context():
        from services.account_service import AccountService
        a1 = AccountService.create_account('+1111111111', 's1')
        a2 = AccountService.create_account('+2222222222', 's2')
        a1.is_active = True
        db.session.commit()
        active = AccountService.get_active_accounts()
        assert len(active) == 1


def test_delete_account(app):
    with app.app_context():
        from services.account_service import AccountService
        account = AccountService.create_account('+1111111111', 's1')
        account_id = account.id
        AccountService.delete_account(account_id)
        accounts = AccountService.get_all_accounts()
        assert len(accounts) == 0
