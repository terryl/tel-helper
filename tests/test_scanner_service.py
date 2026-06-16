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


def test_get_members_by_group(app):
    with app.app_context():
        from services.scanner_service import ScannerService
        ScannerService.store_member('111', 'G1', '1', 'u1')
        ScannerService.store_member('111', 'G1', '2', 'u2')
        ScannerService.store_member('222', 'G2', '3', 'u3')

        members = ScannerService.get_members_by_group('111')
        assert len(members) == 2


def test_get_all_groups(app):
    with app.app_context():
        from services.scanner_service import ScannerService
        ScannerService.store_member('111', 'Group A', '1')
        ScannerService.store_member('222', 'Group B', '2')

        groups = ScannerService.get_all_groups()
        assert len(groups) == 2


def test_export_csv(app):
    with app.app_context():
        from services.scanner_service import ScannerService
        ScannerService.store_member('111', 'G1', '1', 'u1', 'First', 'Last')

        csv_data = ScannerService.export_members_csv('111')
        assert 'User ID' in csv_data
        assert 'u1' in csv_data
