from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from services.scanner_service import ScannerService
from services.account_service import AccountService

scanner_bp = Blueprint('scanner', __name__)

@scanner_bp.route('/')
def results():
    groups = ScannerService.get_all_groups()
    return render_template('scanner/results.html', groups=groups)

@scanner_bp.route('/group/<group_id>')
def group_members(group_id):
    members = ScannerService.get_members_by_group(group_id)
    return render_template('scanner/results.html', members=members, group_id=group_id)

@scanner_bp.route('/export/<group_id>')
def export_csv(group_id):
    csv_data = ScannerService.export_members_csv(group_id)
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=group_{group_id}_members.csv'}
    )

@scanner_bp.route('/scan', methods=['POST'])
def scan():
    account_id = request.form.get('account_id')
    group_identifier = request.form.get('group_identifier')
    
    import asyncio
    result = asyncio.run(ScannerService.scan_group(int(account_id), group_identifier))
    
    flash(f"Scanned {result['members_scanned']} members from {result['group']}", 'success')
    return redirect(url_for('scanner.results'))
