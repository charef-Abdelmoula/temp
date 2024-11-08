# -*- encoding: utf-8 -*-
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "SDT Accounting", 
    "version": "1.1", 
    "author": "Purnendu Singh", 
    "category": "Accounting", 
    "description": """
        Accounting adoption for SDT
\n
\n
\n
\n

     """, 
    "website": "https://www.odoo.com", 
    "license": "AGPL-3", 
    "depends": [
        "account_accountant",
        # "account_cancel",
    ], 
    "demo": [], 
    "data": [
        'security/ir.model.access.csv',
        'security/sdt_security.xml',
        # 'data/import_config_data.xml',
        'data/ftp_sync_data.xml',
        'data/ir_cron_data.xml',
        'views/import_config_view.xml',
        'views/ftp_sync_view.xml',
        'wizard/audit_label_views.xml',
        'wizard/update_record_created_from_views.xml',
        'wizard/generate_inv_bills.xml',
        'wizard/update_invoice_view.xml',
        # 'wizard/account_payment_register_views.xml',
        'wizard/import_market_amazon.xml',
        # 'wizard/import_INV04.xml',
        # 'wizard/import_vendor_bills.xml',
        # 'wizard/import_vendor_bills_cn.xml',
        # 'wizard/import_customer_invoices_cn.xml',
        # 'wizard/import_INV05.xml',
        # 'wizard/import_INV06.xml',
        # 'wizard/import_BILL_INV04.xml',
        # 'wizard/import_BILL_INV06.xml',
        # 'wizard/import_partners.xml',
        # 'wizard/account_invoice_set_values.xml',
        # 'wizard/account_invoice_set_periods.xml',
        # 'wizard/account_invoice_set_lines.xml',
        # 'wizard/account_analytic_allocation.xml',
        # 'wizard/account_invoice_state_view.xml',
        # 'wizard/account_bank_statement_partner.xml',
        # 'wizard/invoice_payment_xls.xml',
        # 'wizard/invoice_bills_xls.xml',
        # 'wizard/account_invoice_xls.xml',
        'views/res_partner_view.xml',
        'views/account_journal.xml',
        # 'wizard/account_invoice_cash_discount.xml',
        'views/account_move_view.xml',
        'views/account_payment.xml',
        'views/account_analytic_view.xml',
        'views/product_template_view.xml',
        'views/sdt_view.xml',
        'views/ftp_data_view.xml',
    ], 
    "test": [], 
    "js": [], 
    "css": [], 
    "qweb": [], 
    "installable": True, 
    "auto_install": False, 
    "active": False
}
