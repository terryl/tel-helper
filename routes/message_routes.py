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
