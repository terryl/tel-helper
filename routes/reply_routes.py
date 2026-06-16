from flask import Blueprint, render_template, request, redirect, url_for, flash
from services.reply_service import ReplyService
from services.account_service import AccountService

reply_bp = Blueprint('replies', __name__)

@reply_bp.route('/')
def rules():
    accounts = AccountService.get_all_accounts()
    return render_template('replies/rules.html', accounts=accounts)

@reply_bp.route('/edit/<int:rule_id>', methods=['GET', 'POST'])
def edit_rule(rule_id):
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        reply_text = request.form.get('reply_text')
        is_active = 'is_active' in request.form
        ReplyService.update_rule(rule_id, keyword, reply_text, is_active)
        flash('Rule updated.', 'success')
        return redirect(url_for('replies.rules'))
    
    from models import AutoReply
    rule = AutoReply.query.get_or_404(rule_id)
    return render_template('replies/edit_rule.html', rule=rule)

@reply_bp.route('/create', methods=['POST'])
def create_rule():
    account_id = request.form.get('account_id')
    keyword = request.form.get('keyword')
    reply_text = request.form.get('reply_text')
    ReplyService.create_rule(int(account_id), keyword, reply_text)
    flash('Rule created.', 'success')
    return redirect(url_for('replies.rules'))

@reply_bp.route('/delete/<int:rule_id>', methods=['POST'])
def delete_rule(rule_id):
    ReplyService.delete_rule(rule_id)
    flash('Rule deleted.', 'success')
    return redirect(url_for('replies.rules'))
