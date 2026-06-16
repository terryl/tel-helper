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
