# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import date, datetime, time
from dateutil.parser import parse

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.tools import float_compare
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

from _ast import Lambda

class InvoicePeriode(models.Model):
    _name = 'invoice.periode'
    _description = 'Invoice Line Periode' 

    name = fields.Char('Periode', required=True)

class InvoiceHr(models.Model):
    _name = 'invoice.hr'
    _description = 'HR on Invoice Lines'

    name = fields.Char('HR', required=True)

class InvoiceDepartment(models.Model):
    _name = 'invoice.department'
    _description = 'Invoice Line department'

    name = fields.Char('Department Name', required=True)

class VatPeriod(models.Model):
    _name = 'vat.period'
    _description = 'VAT Period'

    name = fields.Char('Vat Period', required=True)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, default=lambda self: self.env['res.company']._company_default_get('account.invoice'))
    statement_issued = fields.Boolean('Statement Issued')

class AccountTax(models.Model):
    _inherit = 'account.tax'

    discount_product_id = fields.Many2one('product.product', string='Cash Discount Product')

class AccountMove(models.Model):
    _inherit = 'account.move'

    # @api.depends('invoice_line_ids')
    # def _get_analytic_product(self):
        # for record in self:
            # record.analytic_product = False
            # lines_with_analytic_account = [line.id for line in record.invoice_line_ids if line.account_analytic_id]
            #
            # if len(record.invoice_line_ids)>0 and len(lines_with_analytic_account)==len(record.invoice_line_ids):
                # record.analytic_product = True

    number_ref = fields.Char('Number with Reference', readonly=True, copy=False)
    ppc_user_imported = fields.Boolean('User Imported')
    ppv_vendor_imported = fields.Boolean('Vendor imported')
    ppc_invoice = fields.Boolean('PaperSmart Invoice', related='journal_id.sdt_papersmart')
    ds_invoice = fields.Boolean('PaperSmart Invoice', related='journal_id.sdt_distrismart')
    ppc_orderingdate = fields.Datetime('PS Ordering Date')
    ppc_customerorder = fields.Char('PS Customer Order')
    ppc_vendororde = fields.Char('PS Vendor Order')
    ppc_customersurname = fields.Char('PS Customer Surname')
    ppc_customerfirstname = fields.Char('PS Customer First Name')
    ppc_title = fields.Char('PS Customer Title')
    ppc_email = fields.Char('PS Customer Email')
    ppc_customernumber = fields.Char('PS Customer Number')
    ppc_company = fields.Char('PS Customer Company')
    ppc_paymenttype = fields.Char('PS Payment Type')
    ppc_orderingstate = fields.Char('PS Ordering State')
    ppc_invoicenumber = fields.Char('PS Invoice Number')
    ppc_invoicedate = fields.Date('PS Invoice Date')
    ppc_couponcode = fields.Char('PS Coupon Code')
    ppc_couponvalue = fields.Char('PS Coupon Value')
    ppc_netvalueofarticles = fields.Monetary('PS Net Value of Articles')
    ppc_netshipment = fields.Monetary('PS Net Shipment')
    ppc_rebate = fields.Monetary('PS Rebate')
    ppc_nettotal = fields.Monetary('PS Net Total')
    ppc_vat = fields.Monetary('PS VAT')
    ppc_grosstotal = fields.Monetary('PS Gross Total')
    ppc_agiopaymentprovider = fields.Monetary('PS Payment Provider')
    ppc_paidon = fields.Date('PS Paid On')
    ppc_expectedgross = fields.Monetary('PS Expected Gross')
    ppc_paymentprovider = fields.Char('PS Payment Provider')
    ps_paymentprovidertxid = fields.Char('PS Payment Provider TXID')

    ppv_invoiceid = fields.Char('PS Invoice Id')
    ppv_created = fields.Char('PS Creation')
    ppv_updated = fields.Char('PS Update')
    ppv_netcommission = fields.Monetary('PS Net Commission')
    ppv_netdiscount = fields.Monetary('PS Net Discount')
    ppv_netpaymentfee = fields.Monetary('PS Net Payment Fee')
    ppv_grossvendorpayout = fields.Monetary('PS Gross Vendor Payout')
    ppv_vendorid = fields.Char('PS Vendor Id')
    ppv_invoicedate = fields.Date('PS Invoice Date')
    ppv_nettotal = fields.Monetary('PS Invoice Net Total')
    ppv_vat = fields.Monetary('PS VAT')
    ppv_grosstotal = fields.Monetary('PS Gross Total')
    venice_accyear = fields.Char(string='Fiscal Year', size=4)
    venice_docnum = fields.Char(string='Doc Number')
    helpdesk_ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Tiket')
    ticket_stage_id = fields.Many2one(relation='helpdesk_ticket_id.stage_id', string='Ticket Stage')
    payment_id = fields.Many2one('account.payment', string='Payment')
    payment_date = fields.Date(string='Payment Date')
    # state = fields.Selection([
            # ('draft','Draft'),
            # ('imported','Imported'),
            # ('posted', 'Posted'),
            # ('cancel', 'Cancelled'),
        # ], string='Status', index=True, readonly=True, default='draft',
        # track_visibility='onchange', copy=False,
        # help=" * The 'Draft' status is used when a user is encoding a new and unconfirmed Invoice.\n"
             # " * The 'Imported' status is used when a invoice is created using import wizard(INV04,INV05,BILL04).\n"
             # " * The 'Open' status is used when user creates invoice, an invoice number is generated. It stays in the open status till the user pays the invoice.\n"
             # " * The 'In Payment' status is used when payments have been registered for the entirety of the invoice in a journal configured to post entries at bank reconciliation only, and some of them haven't been reconciled with a bank statement line yet.\n"
             # " * The 'Paid' status is set automatically when the invoice is paid. Its related journal entries may or may not be reconciled.\n"
             # " * The 'Cancelled' status is used when user cancel invoice.")
    # invoice_line_ids = fields.One2many('account.invoice.line', 'invoice_id', string='Invoice Lines', oldname='invoice_line',
        # readonly=True, states={'draft': [('readonly', False)], 'imported': [('readonly', False)]}, copy=True)
    # invoice_line_ids = fields.One2many('account.move.line', 'move_id', string='Invoice lines',
        # copy=False, readonly=True,
        # domain=[('exclude_from_invoice_tab', '=', False)],
        # states={'draft': [('readonly', False)], 'imported': [('readonly', False)]},)
    # date_invoice = fields.Date(string='Invoice Date',
        # readonly=True, states={'draft': [('readonly', False)], 'imported': [('readonly', False)]}, index=True,
        # help="Keep empty to use the current date", copy=False)

    # invoice_date = fields.Date(string='Invoice/Bill Date', readonly=True, index=True, copy=False,
        # states={'draft': [('readonly', False)], 'imported': [('readonly', False)]})

    # partner_id = fields.Many2one('res.partner', string='Partner', change_default=True,
        # readonly=True, states={'draft': [('readonly', False)], 'imported': [('readonly', False)]},
        # tracking=True, help="You can find a contact by its Name, TIN, Email or Internal Reference.")

    # partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
        # tates={'draft': [('readonly', False)], 'imported': [('readonly', False)]},
        # check_company=True,
        # string='Partner', change_default=True)

    # payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms', oldname='payment_term',
        # readonly=True, states={'draft': [('readonly', False)], 'imported': [('readonly', False)]},
        # help="If you use payment terms, the due date will be computed automatically at the generation "
             # "of accounting entries. If you keep the payment terms and the due date empty, it means direct payment. "
             # "The payment terms may compute several due dates, for example 50% now, 50% in one month.")

    # invoice_payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms',
        # check_company=True,
        # readonly=True, states={'draft': [('readonly', False)], 'imported': [('readonly', False)]})


    # user_id = fields.Many2one('res.users', string='Salesperson', track_visibility='onchange',
        # readonly=True, states={'draft': [('readonly', False)], 'imported': [('readonly', False)]},
        # default=lambda self: self.env.user, copy=False)

    # invoice_user_id = fields.Many2one('res.users', copy=False, tracking=True,
        # string='Salesperson',
        # default=lambda self: self.env.user)

    # fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', oldname='fiscal_position',
        # readonly=True, states={'draft': [('readonly', False)], 'imported': [('readonly', False)]})

    # fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position', readonly=True,
        # states={'draft': [('readonly', False)], 'imported': [('readonly', False)]},
        # check_company=True,
        # domain="[('company_id', '=', company_id)]", ondelete="restrict",
        # help="Fiscal positions are used to adapt taxes and accounts for particular customers or sales orders/invoices. "
             # "The default value comes from the customer.")

    vat_period_id =  fields.Many2one('vat.period', string='VAT Period', domain=[('active','=',True)], copy=False)
    vat_declaration = fields.Selection([('to_do','To Do'),
                                        ('done','Done'),
                                        ('issue','Issue')], string='VAT Declaration', default='to_do')
    vat_check_date = fields.Datetime('VAT Check Date')
    vat_issue_date = fields.Datetime('VAT Issue Date')
    audit_vat_country = fields.Char(related='partner_id.audit_vat_country', string='Audit Vat Country', store=True)
    bill_type = fields.Selection([
            ('ic_acquisitions','IC Acquisitions'),
            ('purchased_services_eu','Purchased Services EU'),
            ('input_vat', 'Input VAT'),
            ('import_vat', 'Import VAT'),
        ], string='BILL Type')
    inv_type = fields.Selection([
            ('ic_suppliers','IC Suppliers'),
            ('export_suppliers','Export Suppliers'),
            ('sales_with_VAT', 'Sales with VAT'),
            ('ic_services', 'IC Services'),
        ], string='INV Type')
    reason_for_cancellation = fields.Char('Reason for Cancellation')
#     period_id =  fields.Many2one('invoice.periode', string='Periode')
    venice_pinvoicebook = fields.Char('PINV Book')#PInvoiceBook
    venice_sinvoicebook = fields.Char('SINV Book')#SInvoiceBook

    venice_repcountry = fields.Char("Rep Country")
    dropshipping = fields.Boolean('Dropshipping')

# Sales Order
    venice_sorderdocnumber = fields.Char('SO Doc. Numb.')#SorderDocNumber
    venice_sorderdate = fields.Date('SO Date')#SOrderDate
    venice_sorderaccyear = fields.Char('SO Year')#SOrderAccYear
    venice_sorddocamountvatex = fields.Float('SO Amount (EVAT)')#SOrdDocAmountVatEx
    so_name = fields.Char('SO Name') #“SOrderAccYear” & “-“ &” SorderDocNumber”

# Purchase Order
    venice_porderdocnumber = fields.Char('PO Doc. Numb.')#POrderDocNumber
    venice_porderdate = fields.Date('PO Date')#POrderDate
    venice_porderaccyear = fields.Char('PO Year')#POrderAccYear
    venice_porderamountvatex = fields.Float('PO Amount (EVAT)')#POrderAmountVatEx
    po_name = fields.Char('PO Name') #“POrderAccYear” & “-“ &” POrderDocNumber”

# Vendor Bill
    venice_suppname = fields.Char('SuppName')
    venice_suppnum = fields.Char('SuppNum')
    venice_pinvoicedocnum = fields.Char('PInvoiceDocNum')
    venice_pinvoicedate = fields.Date('PInvoiceDate')
    venice_pinvoiceaccyear = fields.Char('Year of PInvoiceDate')
    venice_pinvoiceamount = fields.Char('PInvoiceAmount')
    venice_pinvexpirationDate = fields.Date('PInvExpirationDate')
    venice_pinvremark = fields.Char('PInvRemark')
    venice_pinvvatsystemdsc = fields.Char('PInvVatSystemDsc')

# Client Invoice
    venice_sinvoicedocnumber = fields.Char('INV Doc. Numb.')#SInvoiceDocNum
    venice_sinvoicedate = fields.Date('INV Date')#SInvoiceDate
    venice_sinvoiceaccyear = fields.Char('INV Year')#SInvoiceAccYear
    venice_sinvoiceamountvatex = fields.Float('INV Amount (EVAT)')#SInvoiceAmountVatEx
    inv_name = fields.Char('INV Name') #“SInvoiceAccYear” & “-“ &” SInvoiceDocNum”
    venice_sinvoiceamount = fields.Float('INV Amount')#SInvoiceAmount
    venice_sinvexpirationdate = fields.Date('INV Due Date')#SInvExpirationDate
    sinvdiscount = fields.Float('INV Discount')#for future development
    clientfiscalposition = fields.Char('INV Fiscal Position')
# “clientfiscalposition” (INV Fiscal Position)   From Odoo Field Fiscal Position, we will use the same entries based on those conditions:
# * In Odoo : « Régime Intra-Communautaire »   (*)
#  If « INV Amount » = « INV Amount (EVAT)
#  * In Odoo : « Régime Normal »   (*)
#  If « INV Amount » > « INV Amount (EVAT) 

# Client Information
    venice_customername = fields.Char('Customer Name')#CustomerName
    venice_customernumber = fields.Char('Customer Number')#CustomerNumber
    venice_customersubnumber = fields.Char('Customer Sub Number')#Customer Sub Number
    venice_sinvremark = fields.Char('INV Remark')#SInvRemark
    venice_deliveryname = fields.Char('Delivery Name')#DeliveryName
    venice_deliverynumber = fields.Char('Delivery Number')#DeliveryNumber
    venice_deliverysubnumber = fields.Char('Delivery Sub Number')#DeliverySubNumber

    pinvdiscount = fields.Float('PINV Discount')#for future development
# I add it manually, will do server action on it linked to Payment Term with impact on total VAT amount, we will check it later)
    # analytic_product = fields.Boolean(compute='_get_analytic_product', string='Analytic Product', store=True, readonly=True,
                                      # help='Ticked automaticall if all invoice lines have analytic account on them.')
    import_wizard = fields.Boolean('FTP Import')
    ftp_raw_data_id = fields.Many2one('ftp.data', string='FTP Data Link')
    delta_ex_vat = fields.Float(string='Delta Ex Vat', compute='_compute_delta_fields', store=True)
    delta_vat = fields.Float(string='Delta Vat', compute='_compute_delta_fields', store=True)
    delta_total = fields.Float(string='Delta Total', compute='_compute_delta_fields', store=True)
    audit_variance = fields.Float(string='Audit Variance', compute='_compute_delta_fields', store=True)
    partner_type_id = fields.Many2one('res.partner.type', related='partner_id.partner_type_id', string='Partner Type', store=True)

    original_partner_id = fields.Many2one('res.partner', string='Original Partner')
    market_statement_line_id = fields.Many2one('market.statement.line', string='Settlement')
    market_statement_id =  fields.Many2one(related='market_statement_line_id.market_statement_id', string='Settlement', store=True)
    customer_group = fields.Char(related='ftp_raw_data_id.customer_group', string='Customer Group', store=True)

    cashdiscount_status = fields.Selection([('na','NA'),
                                            ('open','Open'),
                                            ('expired','Expired'),
                                            ('deducted','Deducted'),], string='Cash Discount Status', default='open')
    cashdiscount_rate = fields.Float(related='ftp_raw_data_id.cashdiscount_rate', string='Cash Discount', store=True)
    cashdiscount_expiration = fields.Date(related='ftp_raw_data_id.cashdiscount_expiration', string='Cash Discount Limit', store=True)
    cashdiscount_total = fields.Monetary(string='Total CD', readonly=True, tracking=True)

# In account.move, add a new field under "to_check" in other info:
# - CD Statut (cashdiscount_statut), it can be "Open, NA, Expired, Deducted"
# ---> When we create the entry:
# -- If " cashdiscount_rate" is SET (>0) and cashdiscount_expiration <= DATE OF THE DAY: statut Open
# -- If " cashdiscount_rate" is SET (>0) and cashdiscount_expiration > DATE OF THE DAY: statut Expired
# -- If " cashdiscount_rate " is NOT SET (=0) : statut NA
# Create a schelduled server action, every single night at 1 AM Belgium, it check for all "OPEN" CD Statut if cashdiscount_expiration <= DATE OF THE DAY + 1 , if yes statut Open, if no statut Expired.

    @api.model
    def update_cd_status_invoice_cron(self):
        for record in self.search([('state','in',['draft','posted']),('cashdiscount_status', '=', 'open')]):
            if not record.cashdiscount_rate:
                record.cashdiscount_status = 'na'
            else:
                if record.cashdiscount_expiration:
                    if record.cashdiscount_expiration < fields.Date.context_today(self):
                        record.cashdiscount_status = 'expired'
                    else:
                        record.cashdiscount_status = 'open'

# From there, we can have (see picture below)
# - Delta Ex Vat = FTP Amont Ex Vat      -         "Untaxed Amount"
#
# - Delta Vat = FTP VAT Total   -    ( "Total" - "Untaxed Amount")
#
# - Delta Total = FTP Document total        -         "Total"
# - Audit Variance (Position above "Audit Label)
# Audit Variance : is a kind of statistical variance: (Delta Ex Vat)² + (Delta Vat)² + (Delta Total)²
    @api.depends('ftp_raw_data_id', 'amount_untaxed', 'amount_total', 
                 'ftp_raw_data_id.vat_rate_total','ftp_raw_data_id.vat_total','ftp_raw_data_id.document_total',
                 'ftp_raw_data_id.document_total_ex_vat','ftp_raw_data_id.total_vat_amount','ftp_raw_data_id.document_total_inc_vat',
                 'amazon_raw_data_id','amazon_raw_data_id.total_tax_excluded','amazon_raw_data_id.total_tax',
                 'amazon_raw_data_id.total_tax_included')
    def _compute_delta_fields(self):
        for invoice in self:
# SLS:
    # delta_ex_vat = document_total_ex_vat - amount_untaxed
    # delta_vat = total_vat_amount - (amount_total - amount_untaxed)
    # delta_total = document_total_inc_vat - amount_total 
# PUR:
    # delta_ex_vat = vat_rate_total - amount_untaxed
    # delta_vat = vat_total - (amount_total - amount_untaxed)
    # delta_total = document_total - amount_total
            invoice.delta_ex_vat = 0
            invoice.delta_vat = 0
            invoice.delta_total = 0
            invoice.audit_variance = 0
            if invoice.ftp_raw_data_id:
                if invoice.ftp_raw_data_id.import_config_id.type == 'PUR':
                    invoice.delta_ex_vat = invoice.amount_untaxed - invoice.ftp_raw_data_id.vat_rate_total
                    invoice.delta_vat = (invoice.amount_total - invoice.amount_untaxed) - invoice.ftp_raw_data_id.vat_total
                    invoice.delta_total = invoice.amount_total - invoice.ftp_raw_data_id.document_total 
                if invoice.ftp_raw_data_id.import_config_id.type == 'SLS':
                    invoice.delta_ex_vat = invoice.amount_untaxed - invoice.ftp_raw_data_id.document_total_ex_vat
                    invoice.delta_vat = (invoice.amount_total - invoice.amount_untaxed) - invoice.ftp_raw_data_id.total_vat_amount
                    invoice.delta_total = invoice.amount_total - invoice.ftp_raw_data_id.document_total_inc_vat
                invoice.audit_variance = (invoice.delta_ex_vat**2) + (invoice.delta_vat**2) + (invoice.delta_total**2)

            if invoice.amazon_raw_data_id:
                # We need to update this action for the invoice generated from Amazon Invoice (amazon_invioce = TRUE)
                # The field to update are:
                # - delta_ex_vat = from market.amazon (total_tax_excluded) - amount_untaxed
                # - delta_vat = from market.amazon (total_tax) - amount_total + amount_untaxed
                # - delta_total = from market.amazon (total_tax_included) - amount_total
                # Those 3 field update the field in account.move: "audit_variance" (same formula used for ftp.data)
                # This action needs to be trigger when we generate an new invoice from market.amazon.
                invoice.delta_ex_vat = invoice.amount_untaxed - invoice.amazon_raw_data_id.total_tax_excluded
                invoice.delta_vat = (invoice.amount_total + invoice.amount_untaxed) - invoice.amazon_raw_data_id.total_tax
                invoice.delta_total = invoice.amount_total - invoice.amazon_raw_data_id.total_tax_included
                invoice.audit_variance = (invoice.delta_ex_vat**2) + (invoice.delta_vat**2) + (invoice.delta_total**2)

    def server_action_compute_delta_fields(self):
        active_ids = self._context.get('active_ids')
        for invoice in self.browse(active_ids):
# SLS:
    # delta_ex_vat = document_total_ex_vat - amount_untaxed
    # delta_vat = total_vat_amount - (amount_total - amount_untaxed)
    # delta_total = document_total_inc_vat - amount_total 
# PUR:
    # delta_ex_vat = vat_rate_total - amount_untaxed
    # delta_vat = vat_total - (amount_total - amount_untaxed)
    # delta_total = document_total - amount_total
            invoice.delta_ex_vat = 0
            invoice.delta_vat = 0
            invoice.delta_total = 0
            invoice.audit_variance = 0
            if invoice.ftp_raw_data_id:
                if invoice.ftp_raw_data_id.import_config_id.type == 'PUR':
                    invoice.delta_ex_vat = invoice.amount_untaxed - invoice.ftp_raw_data_id.vat_rate_total
                    invoice.delta_vat = (invoice.amount_total - invoice.amount_untaxed) - invoice.ftp_raw_data_id.vat_total
                    invoice.delta_total = invoice.amount_total - invoice.ftp_raw_data_id.document_total 
                if invoice.ftp_raw_data_id.import_config_id.type == 'SLS':
                    invoice.delta_ex_vat = invoice.amount_untaxed - invoice.ftp_raw_data_id.document_total_ex_vat
                    invoice.delta_vat = (invoice.amount_total - invoice.amount_untaxed) - invoice.ftp_raw_data_id.total_vat_amount
                    invoice.delta_total = invoice.amount_total - invoice.ftp_raw_data_id.document_total_inc_vat
                invoice.audit_variance = (invoice.delta_ex_vat**2) + (invoice.delta_vat**2) + (invoice.delta_total**2)

            if invoice.amazon_raw_data_id:
                # We need to update this action for the invoice generated from Amazon Invoice (amazon_invioce = TRUE)
                # The field to update are:
                # - delta_ex_vat = from market.amazon (total_tax_excluded) - amount_untaxed
                # - delta_vat = from market.amazon (total_tax) - amount_total + amount_untaxed
                # - delta_total = from market.amazon (total_tax_included) - amount_total
                # Those 3 field update the field in account.move: "audit_variance" (same formula used for ftp.data)
                # This action needs to be trigger when we generate an new invoice from market.amazon.
                invoice.delta_ex_vat = invoice.amount_untaxed - invoice.amazon_raw_data_id.total_tax_excluded
                invoice.delta_vat = (invoice.amount_total + invoice.amount_untaxed) - invoice.amazon_raw_data_id.total_tax
                invoice.delta_total = invoice.amount_total - invoice.amazon_raw_data_id.total_tax_included
                invoice.audit_variance = (invoice.delta_ex_vat**2) + (invoice.delta_vat**2) + (invoice.delta_total**2)
        return True

    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)

    multiple_lines_same_product = fields.Boolean(string='Multiple Product Lines', compute='_compute_multipe_lines', store=True)
    multiple_lines = fields.Boolean(string='Multiple Lines', compute='_compute_multipe_lines', store=True)
    audit_tax_grid = fields.Char(string='Audit Tax Grid', compute='_compute_tax_grid', store=True)
    audit_invoice_line = fields.Char(string='Audit Invoice Line', compute='_compute_audit_invoice_line', store=True)
    audit_status = fields.Selection([('unaudited','Unaudited'),
                                     ('audited','Audited'),
                                     ('to_check','To check'),
                                     ('manually_audited','Manually Audited')], string='Audit Status', default='unaudited', tracing=True)
    audit_template_id = fields.Many2one('audit.template', string='Audit Template', tracking=True)
    audit_06_rate = fields.Char(related='ftp_raw_data_id.audit_06_rate', string='Audit 06 Rate', store=True)
    audit_label = fields.Char(string='Audit Label', tracking=True)
    amazon_invoice = fields.Boolean('Amazon Invoice')
    amazon_raw_data_id = fields.Many2one('market.amazon', string='FTP Data Link')
    # amazon_import_config_id = fields.Many2one('import.config.amazon', string='Amazon Import Configuration', tracking=True)
    amazon_import_config_id = fields.Many2one(related='amazon_raw_data_id.import_config_id', string='Amazon Import Configuration', tracking=True, store=True)
    buyer_tax_registration_jurisdiction = fields.Char(string="Buyer Tax Registration Jurisdiction", tracking=True)
    amazon_audit_06_rate = fields.Selection(related='amazon_raw_data_id.fiscal_position', string='Audit 06 Rate', store=True)
    record_created_from = fields.Char(related='amazon_raw_data_id.record_created_from', string='Record Created From', store=True)
    product_tax_code = fields.Char(string='Product Tax Code', tracking=True)

    @api.depends('invoice_line_ids')
    def _compute_multipe_lines(self):
        for invoice in self:
            if len(invoice.invoice_line_ids) > 1:
                invoice.multiple_lines = True
            product_ids = [line.product_id.id for line in invoice.invoice_line_ids]
            if len(product_ids) != len(set(product_ids)):
                invoice.multiple_lines_same_product = True

    @api.model 
    def server_action_update_audit_tax_grid(self):
        active_ids = self._context.get('active_ids')
        for invoice in self.browse(active_ids):
            tax_grid = ''
            for line in invoice.line_ids.filtered(lambda x: x.account_id).sorted(lambda x: x.account_id.code):
                account_code = str(line.account_id.code) + ': '
                if line.tax_ids and line.tax_tag_ids:
                    tax_names = [tax_id.name for tax_id in line.tax_ids]
                    tag_names = [tag_id.name for tag_id in line.tax_tag_ids]
                    tax_tag_name = ', '.join(tax_names) + ', ' + ', '.join(tag_names) + '; '
                if line.tax_ids and not line.tax_tag_ids:
                    tax_names = [tax_id.name for tax_id in line.tax_ids]
                    tax_tag_name = ', '.join(tax_names) + ', NA; '
                if not line.tax_ids and line.tax_tag_ids:
                    tag_names = [tag_id.name for tag_id in line.tax_tag_ids]
                    tax_tag_name = 'NA, '+ ', '.join(tag_names) + '; '
                if not line.tax_ids and not line.tax_tag_ids:
                    account_code = ''
                    tax_tag_name = ''
                tax_grid += account_code + tax_tag_name
            invoice.audit_tax_grid = tax_grid
        return True

# "tax_ids" and tax_tag_ids

# 2/ update of the tax audit grid, in place of L1, L2, we will use the code of the account of the line. (The best is if we can rank it smaller to larger): code, VAT, Tax grid ; code, VAT, Tax grid 
# (NA when the VAT or the Tax grid is empty)

    @api.depends('line_ids','line_ids.account_id','line_ids.tax_ids','line_ids.tax_tag_ids')
    def _compute_tax_grid(self):
        for invoice in self:
            tax_grid = ''
            for line in invoice.line_ids.filtered(lambda x: x.account_id).sorted(lambda x: x.account_id.code):
                account_code = str(line.account_id.code) + ': '
                if line.tax_ids and line.tax_tag_ids:
                    tax_names = [tax_id.name for tax_id in line.tax_ids]
                    tag_names = [tag_id.name for tag_id in line.tax_tag_ids]
                    tax_tag_name = ', '.join(tax_names) + ', ' + ', '.join(tag_names) + '; '
                if line.tax_ids and not line.tax_tag_ids:
                    tax_names = [tax_id.name for tax_id in line.tax_ids]
                    tax_tag_name = ', '.join(tax_names) + ', NA; '
                if not line.tax_ids and line.tax_tag_ids:
                    tag_names = [tag_id.name for tag_id in line.tax_tag_ids]
                    tax_tag_name = 'NA, '+ ', '.join(tag_names) + '; '
                if not line.tax_ids and not line.tax_tag_ids:
                    account_code = ''
                    tax_tag_name = ''
                tax_grid += account_code + tax_tag_name
            invoice.audit_tax_grid = tax_grid

    @api.model 
    def server_action_update_audit_invoice_line(self):
        active_ids = self._context.get('active_ids')
        for invoice in self.browse(active_ids):
            invoice_line_grid = ''
            for line in invoice.invoice_line_ids.filtered(lambda x: x.account_id).sorted(lambda x: x.account_id.code):
                account_name = str(line.account_id.display_name) + ': '
                product_name = line.product_id and line.product_id.display_name or ''
                tax_tag_name = ''
                if line.tax_ids:
                    tax_names = [tax_id.name for tax_id in line.tax_ids]
                    tax_tag_name = ', '.join(tax_names) + '; '
                invoice_line_grid += account_name + product_name+ ', ' + tax_tag_name
            invoice.audit_invoice_line = invoice_line_grid
        return True

    @api.model 
    def server_action_update_audit_status(self):
        active_ids = self._context.get('active_ids')
        Audit_template = self.env['audit.template']
        for invoice in self.browse(active_ids):
            audit_template_ids = Audit_template.search([('state','=', 'active'),
                                                        ('company_id','=', invoice.company_id.id),
                                                        # ('journal_id','=', invoice.journal_id.id),
                                                        ('audit_tax_grid','=', invoice.audit_tax_grid),
                                                        ('audit_invoice_line','=', invoice.audit_invoice_line),
                                                        ('audit_vat_country','=', invoice.audit_vat_country),
                                                        ('import_wizard','=', invoice.import_wizard),
                                                        ('audit_06_rate','=', invoice.audit_06_rate)])
            if audit_template_ids:
                for audit_template in audit_template_ids:
                    if invoice.journal_id.id in audit_template.journal_ids.ids:
                        invoice.audit_status = 'audited'
                        invoice.audit_template_id = audit_template.id
            else:
                invoice.audit_status = 'to_check'
                invoice.audit_template_id = False
        return True

    @api.model
    def server_action_update_market_partner(self):
        """
            Within account.move, can you add an action in LIST VIEW (and form view) "Update Market Partner",
            - it checks if the accoun.move is in Draft, if yes:
            - it checks if the journal linked to the account.move has the the field "singlepartner" = TRUE, if yes:
            - it move "partner_id" to "original_partner_id" and set "partner_id" = journal_partner_id (from account.journal)
        """
        active_ids = self._context.get('active_ids')
        for move in self.browse(active_ids):
            if move.state == 'draft':
                if move.journal_id.single_partner and move.journal_id.journal_partner_id:
                    move.original_partner_id = move.partner_id.id
                    move.partner_id = move.journal_id.journal_partner_id.id
        return True

    @api.model
    def action_update_market_partner(self):
        """
            Within account.move, can you add an action in LIST VIEW (and form view) "Update Market Partner",
            - it checks if the accoun.move is in Draft, if yes:
            - it checks if the journal linked to the account.move has the the field "singlepartner" = TRUE, if yes:
            - it move "partner_id" to "original_partner_id" and set "partner_id" = journal_partner_id (from account.journal)
        """
        for move in self:
            if move.state == 'draft':
                if move.journal_id.single_partner and move.journal_id.journal_partner_id:
                    move.original_partner_id = move.partner_id.id
                    move.partner_id = move.journal_id.journal_partner_id.id
        return True

    @api.model
    def action_update_audit_status(self):
        Audit_template = self.env['audit.template']
        for invoice in self:
            audit_template_ids = Audit_template.search([('state','=', 'active'),
                                                        ('company_id','=', invoice.company_id.id),
                                                        # ('journal_id','=', invoice.journal_id.id),
                                                        ('audit_tax_grid','=', invoice.audit_tax_grid),
                                                        ('audit_invoice_line','=', invoice.audit_invoice_line),
                                                        ('audit_vat_country','=', invoice.audit_vat_country),
                                                        ('import_wizard','=', invoice.import_wizard),
                                                        ('audit_06_rate','=', invoice.audit_06_rate)])
            if audit_template_ids:
                for audit_template in audit_template_ids:
                    if invoice.journal_id.id in audit_template.journal_ids.ids:
                        invoice.audit_status = 'audited'
                        invoice.audit_template_id = audit_template.id
            else:
                invoice.audit_status = 'to_check'
                invoice.audit_template_id = False
        return True

    def action_post(self):
        #inherit of the function from account.move to validate a new tax and the priceunit of a downpayment
        """
        Action in list view : "Post entries", should be update and check in the journal linked to the account.move if
        - update_market_partner = True --> if yes it does the action
        - update_audit_status = True --> if yes it does the action
        THEN it post the entry.
        """
        for invoice in self:
            if invoice.journal_id.update_market_partner:
                invoice.action_update_market_partner()
            if invoice.journal_id.update_audit_status:
                invoice.action_update_audit_status()
        return super(AccountMove, self).action_post()

# 3/ new audit field “Audit invoice line”, where it extract: Product, account, Tax; Product, account, Tax) | if it can be ranked with the account code

    @api.depends('invoice_line_ids','invoice_line_ids.account_id','invoice_line_ids.product_id','invoice_line_ids.tax_ids')
    def _compute_audit_invoice_line(self):
        for invoice in self:
            invoice_line_grid = ''
            for line in invoice.invoice_line_ids.filtered(lambda x: x.account_id).sorted(lambda x: x.account_id.code):
                account_name = str(line.account_id.display_name) + ': '
                product_name = line.product_id and line.product_id.display_name or ''
                tax_tag_name = ''
                if line.tax_ids:
                    tax_names = [tax_id.name for tax_id in line.tax_ids]
                    tax_tag_name = ', '.join(tax_names) + '; '
                invoice_line_grid += account_name + product_name+ ', ' + tax_tag_name
            invoice.audit_invoice_line = invoice_line_grid

    def action_audit_label(self):
        ''' Open the audit label wizard to log audit action.
        :return: An action opening the audit action wizard.
        '''
        return {
            'name': _('Audit Remarks'),
            'res_model': 'audit.label',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_set_payment_type(self):
        ''' Open the set payment type wizard to update payment_reference and ppc_paymenttype.
        :return: An action opening the audit action wizard.
        '''
        return {
            'name': _('Set Payment Type'),
            'res_model': 'set.payment.type',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_manual_audit_status(self):
        ''' Open the update audit status to manual wizard to update audit_status on move.
        :return: An action opening the audit status wizard.
        '''
        return {
            'name': _('Set Audit Status to Manual'),
            'res_model': 'manual.audit.status',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.move',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    # @api.onchange('venice_accyear', 'venice_docnum')
    # def onchange_fiscal_year(self):
        # if self.venice_accyear:
            # self.name = self.venice_accyear
        # if self.venice_docnum:
            # self.name += '-'+self.venice_docnum

    # def write(self, vals):
        # for record in self:
            # if vals.get('vat_declaration', False):
                # if vals.get('vat_declaration', False) == 'issue':
                    # vals['vat_issue_date'] = fields.Datetime.now(self)
                # elif vals.get('vat_declaration', False) == 'done':
                    # vals['vat_check_date'] = fields.Datetime.now(self)
                # else:
                    # vals['vat_check_date'] = False
                    # vals['vat_issue_date'] = False
            # if record.name:
    # #             ttyme = datetime.fromtimestamp(time.mktime(time.strptime(record.date_invoice, "%Y-%m-%d")))
                # ttyme = datetime.combine(fields.Date.from_string(record.invoice_date), time.min)
                # month = '%02d' % ttyme.month
                # day = '%02d' % ttyme.day
                # year = ttyme.strftime("%y")
    # #             print ("\nmonth",month,"day",day,"year",year)
                # number_seq = record.number.split('/')
                # number_ref_seq = record.number.split('/')
                # if len(number_seq) > 1:
                    # number_seq[1] = year+'('+month+')'+number_seq[1][6:]
                    # number_ref_seq[1] = year+'('+month+')'+day
                    # if record.name:
                        # number_ref_seq[1] += '*'+record.name
                # vals['name'] = "/".join(number_seq)
                # vals['number_ref'] = "/".join(number_ref_seq)
                # invoice_ids = self.search([('id','!=',record.id),('name','=',vals['name'])])
                # if invoice_ids:
                    # if record.journal_id.sequence_id:
                        # # If invoice is actually refund and journal has a refund_sequence then use that one or use the regular one
                        # sequence = record.journal_id.sequence_id
                        # if record.type in ['out_refund', 'in_refund'] and record.journal_id.refund_sequence:
                            # sequence = record.journal_id.refund_sequence_id
                        # vals['name'] = sequence.with_context(ir_sequence_date=record.invoice_date).next_by_id()
                    # else:
                        # raise UserError(_('Please define a sequence on the journal.'))
        # return super(AccountInvoice, self).write(vals)

#     @api.model 
#     def server_action_analytic_product(self):
#         active_ids = self._context.get('active_ids')
#         for record in self.browse(active_ids):
#             record.analytic_product = False
#             lines_with_analytic_account = [line.id for line in record.invoice_line_ids if line.account_analytic_id]
#             print ("lines_without_analytic_account", lines_with_analytic_account)
#             if len(record.invoice_line_ids)>0 and len(lines_with_analytic_account)==len(record.invoice_line_ids):
#                 record.analytic_product = True

    # @api.model 
    # def server_action_vendor_ref_update(self):
        # """
        # Use this server action to update all those invoices and bill for which vendor ref is with decimal points eg. 1765093.0
        # Apply a filter payment ref contain .0 and run this server action from more dropdown.
        # @ Year of PInvoiceDate: venice_pinvoiceaccyear
        # @ Reference/Description: name
        # @ Number with reference: number_ref
        # @ INV Name: inv_name
        # @ INV Year: venice_sinvoiceaccyear
        # """
        # active_ids = self._context.get('active_ids')
        # for record in self.browse(active_ids):
            # if record.reference and record.reference[-2:] == '.0':
                # record.reference = record.reference[:-2]
        # return True

    # @api.model 
    # def server_action_INV_update(self):
        # """
        # Use this server action to update all those invoices and bill for which name is missing year
        # Apply a filter INV Year = 0 or Reference/Description contains 0- from odoo interface to filter such records.
        # @ Year of PInvoiceDate: venice_pinvoiceaccyear
        # @ Reference/Description: name
        # @ Number with reference: number_ref
        # @ INV Name: inv_name
        # @ INV Year: venice_sinvoiceaccyear
        # """
        # active_ids = self._context.get('active_ids')
        # for record in self.browse(active_ids):
            # if record.venice_pinvoicedate:
                # year = str(record.venice_pinvoicedate.year)
                # record.venice_pinvoiceaccyear = year
                # name_list = record.name.split('-')
                # record.name = year+ "-" +name_list[1]
                # if record.number_ref:
# #                     P2BE/19(02)01*0-00195
                    # number_list = record.number_ref.split('*')
                    # number_list1 = number_list[1].split('-')
                    # record.number_ref = number_list[0]+ "*" + year + "-" + number_list1[1]
                # if record.inv_name == '0-00000':
                    # record.inv_name = ''
                # if record.venice_sinvoiceaccyear == '0':
                    # record.venice_sinvoiceaccyear = ''
        # return True

    # @api.model 
    # def server_action_name_update(self):
        # active_ids = self._context.get('active_ids')
        # for record in self.browse(active_ids):
            # if record.inv_name and len(record.inv_name) < 10:
                # inv_list = record.inv_name.split('-')
                # if len(inv_list[1])<5:
                    # prefix = 5 - len(inv_list[1])
                    # if prefix == 1:
                        # add = '0'
                    # elif prefix == 2:
                        # add = '00'
                    # elif prefix == 3:
                        # add = '000'
                    # else:
                        # add = '0000'
                    # inv_list[1] = add + inv_list[1]
                # record.inv_name = "-".join(inv_list)
            # if record.so_name and len(record.so_name) < 10:
                # so_list = record.so_name.split('-')
                # if len(so_list[1])<5:
                    # prefix = 5 - len(so_list[1])
                    # if prefix == 1:
                        # add = '0'
                    # elif prefix == 2:
                        # add = '00'
                    # elif prefix == 3:
                        # add = '000'
                    # else:
                        # add = '0000'
                    # so_list[1] = add + so_list[1]
                # record.so_name = "-".join(so_list)
            # if record.po_name and len(record.po_name) < 10:
                # po_list = record.po_name.split('-')
                # if len(po_list[1])<5:
                    # prefix = 5 - len(po_list[1])
                    # if prefix == 1:
                        # add = '0'
                    # elif prefix == 2:
                        # add = '00'
                    # elif prefix == 3:
                        # add = '000'
                    # else:
                        # add = '0000'
                    # po_list[1] = add + po_list[1]
                # record.po_name = "-".join(po_list)
        # return True

    # def action_invoice_import_to_draft(self):
        # if self.filtered(lambda inv: inv.state != 'imported'):
            # raise UserError(_("Invoice must be imported in order to reset it to draft."))
        # # go from canceled state to draft state
        # self.write({'state': 'draft', 'date': False})
        # # Delete former printed invoice
        # try:
            # report_invoice = self.env['ir.actions.report']._get_report_from_name('account.report_invoice')
        # except IndexError:
            # report_invoice = False
        # if report_invoice and report_invoice.attachment:
            # for invoice in self:
                # with invoice.env.do_in_draft():
                    # invoice.number, invoice.state = invoice.move_name, 'open'
                    # attachment = self.env.ref('account.account_invoices').retrieve_attachment(invoice)
                # if attachment:
                    # attachment.unlink()
        # return True

    @api.model
    def server_action_taxes_update(self):
        active_ids = self._context.get('active_ids')
        for invoice in self.browse(active_ids):
            #invoice.invoice_line_ids.with_context({'check_move_validity': False})._onchange_product_id()
            for line in invoice.invoice_line_ids:
                if not line.product_id or line.display_type in ('line_section', 'line_note'):
                    continue
                taxes = line._get_computed_taxes()
                if taxes and line.move_id.fiscal_position_id:
                    taxes = line.move_id.fiscal_position_id.map_tax(taxes, partner=line.partner_id)
                line.tax_ids = taxes
                line.account_id = line._get_computed_account()
                #line.with_context({'check_move_validity': False})._onchange_account_id()
            invoice.invoice_line_ids.with_context({'check_move_validity': False})._onchange_price_subtotal()
            invoice.invoice_line_ids.with_context({'check_move_validity': False})._onchange_mark_recompute_taxes()
            invoice.with_context({'check_move_validity': False})._recompute_dynamic_lines(recompute_all_taxes=True)
            invoice.with_context({'check_move_validity': False})._onchange_invoice_line_ids()
            invoice._compute_invoice_taxes_by_group()
        return True

    @api.model 
    def server_action_update_ftp_data(self):
        active_ids = self._context.get('active_ids')
        for invoice in self.browse(active_ids):
            if invoice.ftp_raw_data_id:
                if invoice.type == 'out_invoice':
                    invoice.ftp_raw_data_id.sale_invoice_id = invoice.id
                if invoice.type == 'out_refund':
                    invoice.ftp_raw_data_id.cn_invoice_id = invoice.id
                if invoice.type == 'in_invoice':
                    invoice.ftp_raw_data_id.purchase_invoice_id = invoice.id
                if invoice.type == 'in_refund':
                    invoice.ftp_raw_data_id.refund_invoice_id = invoice.id
        return True

    @api.model 
    def server_action_update_source_document(self):
        active_ids = self._context.get('active_ids')
        for invoice in self.browse(active_ids):
            if invoice.ftp_raw_data_id:
                fiscal_year = ''
                if invoice.ftp_raw_data_id.document_date:
                    fiscal_year = invoice.ftp_raw_data_id.document_date.split('-')[0][2:]
                name = invoice.ftp_raw_data_id.country + fiscal_year + '*' + invoice.ftp_raw_data_id.book + '|' + invoice.ftp_raw_data_id.document_number
                invoice.invoice_origin = name
        return True

    @api.model 
    def action_create_audit_template(self):
        active_ids = self._context.get('active_ids')
        for invoice in self.browse(active_ids):
            invoice.audit_template_id = self.env['audit.template'].create({'name': 'To Check',
                                               'move_id': invoice.id,
                                               # 'journal_id': invoice.journal_id.id,
                                               'journal_ids': [(6, 0, [invoice.journal_id.id])],
                                               'company_id': invoice.company_id.id,
                                               'audit_tax_grid': invoice.audit_tax_grid,
                                               'audit_invoice_line': invoice.audit_invoice_line,
                                               'audit_vat_country': invoice.audit_vat_country,
                                               'import_wizard': invoice.import_wizard,
                                               'audit_06_rate': invoice.audit_06_rate,
                                               'audit_variance': invoice.audit_variance}).id
        return True

    @api.model
    def server_action_link_product_tax_code(self):
        """
            - it checks if the accoun.move is linked to import configuration amazon:
            - if yes then get the product_tax_code from market.amazon
        """
        active_ids = self._context.get('active_ids')
        for move in self.browse(active_ids):
            if move.amazon_raw_data_id:
                move.product_tax_code = move.amazon_raw_data_id.product_tax_code
        return True

    @api.model
    def action_cash_discount(self):
        active_ids = self._context.get('active_ids')
        for invoice in self.browse(active_ids).filtered(lambda rec: rec.state == 'posted' and rec.payment_state == 'not_paid' ):
            if invoice.cashdiscount_status == 'open':
                # It fill the CD field within invoice.line by checking if the product of the line.ids has a CD account related, 
                # if yes CD account is linked to this account,
                # And the CD Amount is computed: cashdiscount_rate x Subtotal
                # And CD Date = Date of the day when the action is trigered.
                # SET the CD Statut to DEDUCTED
                # Check Total CD = Sum of CD Amount
                total_cd = 0
                for line in invoice.invoice_line_ids:
                    line.cashdiscount_account_id = line.product_id and line.product_id.cashdiscount_account_id and line.product_id.cashdiscount_account_id.id or False
                    line.cashdiscount_total = line.price_subtotal * invoice.cashdiscount_rate
                    line.cashdiscount_date = fields.Date.context_today(self)
                    total_cd += line.price_subtotal * invoice.cashdiscount_rate
                invoice.cashdiscount_total = total_cd
                invoice.cashdiscount_status = 'deducted'
                continue
            if invoice.cashdiscount_status == 'deducted':
                # It empty the 3 CD fields within invoice.line, and SET back the CD Statut to OPEN
                for line in invoice.invoice_line_ids:
                    line.cashdiscount_account_id = False
                    line.cashdiscount_total = 0
                    line.cashdiscount_date = False
                invoice.cashdiscount_status = 'open'
                invoice.cashdiscount_total = 0
        return True
#     @api.onchange('fiscal_position_id')
#     def _onchange_fiscal_position_id(self):
#         if not self.fiscal_position_id:
#             return
#         for line in self.invoice_line_ids:
#             if line.product_id:
#                 price = line.price_unit
#                 line._onchange_product_id()
#                 line.write({'price_unit': price})
#             taxes_grouped = self.get_taxes_values()
#             tax_lines = self.tax_line_ids.filtered('manual')
#             for tax in taxes_grouped.values():
#                 tax_lines += tax_lines.new(tax)
#             self.tax_line_ids = tax_lines

    # def action_vat_done(self):
        # for invoice in self:
            # invoice.vat_declaration = 'done'
            # invoice.vat_check_date = fields.Datetime.now(self)
        # return True
        #
    # def action_vat_issue(self):
        # for invoice in self:
            # invoice.vat_declaration = 'issue'
            # invoice.vat_issue_date = fields.Datetime.now(self)
        # return True
        #
    # @api.onchange('vat_declaration')
    # def onchange_vat_declaration(self):
        # for invoice in self:
            # if invoice.vat_declaration == 'to_do':
                # invoice.vat_check_date = False
                # invoice.vat_issue_date = False

    # def action_invoice_imported_open(self):
        # # lots of duplicate calls to action_invoice_open, so we remove those already open
        # to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        # if to_open_invoices.filtered(lambda inv: not inv.partner_id):
            # raise UserError(_("The field Vendor is required, please complete it to validate the Vendor Bill."))
        # if to_open_invoices.filtered(lambda inv: inv.state != 'imported'):
            # raise UserError(_("Invoice must be in imported state in order to validate it."))
        # if to_open_invoices.filtered(lambda inv: float_compare(inv.amount_total, 0.0, precision_rounding=inv.currency_id.rounding) == -1):
            # raise UserError(_("You cannot validate an invoice with a negative total amount. You should create a credit note instead."))
        # if to_open_invoices.filtered(lambda inv: not inv.account_id):
            # raise UserError(_('No account was found to create the invoice, be sure you have installed a chart of account.'))
        # to_open_invoices.action_date_assign()
        # to_open_invoices.action_move_create()
        # return to_open_invoices.invoice_validate()

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.model
    def _get_default_department(self):
        department_id = False
        if self._context.get('partner_id'):
            partner_id = self.env['res.partner'].browse(self._context.get('partner_id'))
            department_id = partner_id.department_id and partner_id.department_id.id or False
        if not department_id and self._context.get('journal_id'):
            journal = self.env['account.journal'].browse(self._context.get('journal_id'))
            department_id = journal.department_id and journal.department_id.id or False
        return department_id

    @api.model
    def _get_default_hr(self):
        hr_id = False
        if self._context.get('partner_id'):
            partner_id = self.env['res.partner'].browse(self._context.get('partner_id'))
            hr_id = partner_id.hr_id and partner_id.hr_id.id or False
        if not hr_id and self._context.get('journal_id'):
            journal = self.env['account.journal'].browse(self._context.get('journal_id'))
            hr_id = journal.hr_id and journal.hr_id.id or False
        return hr_id

    department_id = fields.Many2one('invoice.department', string='Department', default=_get_default_department)
    period_id = fields.Many2one('invoice.periode', string='Periode', copy=False)
    hr_id = fields.Many2one('invoice.hr', string='HR', default=_get_default_hr)
    cashdiscount_account_id = fields.Many2one('account.account', string='CD Account')
    cashdiscount_total = fields.Monetary(string='CD Amount')
    cashdiscount_date = fields.Date(string='CD Date')

    # analytic_client = fields.Char('Analytic Client', compute='_compute_analytic_client', store=True)
    #
    # @api.depends('invoice_id', 'invoice_id.type', 'invoice_id.partner_id', 'invoice_id.venice_customername')
    # def _compute_analytic_client(self):
        # for invoice_line in self:
            # if invoice_line.invoice_id and invoice_line.invoice_id.type == 'out_invoice':
                # invoice_line.analytic_client = invoice_line.invoice_id.partner_id.name
            # if invoice_line.invoice_id and invoice_line.invoice_id.type == 'in_invoice':
                # invoice_line.analytic_client = invoice_line.invoice_id.venice_customername or ''

    # @api.model
    # def create(self, vals):
        # result = super(AccountMoveLine, self).create(vals)
        # if result.move_id:
            # hr_id = False
            # department_id = False
            # if not result.hr_id:
                # hr_id = result.move_id.partner_id.hr_id and result.move_id.partner_id.hr_id.id or False
                # if not hr_id:
                    # hr_id = result.move_id.journal_id.hr_id and result.move_id.journal_id.hr_id.id or False
                # result.write({'hr_id': hr_id})
                # result.move_id.partner_id.write({'hr_id': hr_id})
            # else:
                # result.move_id.partner_id.write({'hr_id': result.hr_id.id})
            # if not result.department_id:
                # department_id = result.move_id.partner_id.department_id and result.move_id.partner_id.department_id.id or False
                # if not department_id:
                    # department_id = result.move_id.journal_id.department_id and result.move_id.journal_id.department_id.id or False
                # result.write({'department_id': department_id})
                # result.move_id.partner_id.write({'department_id': department_id})
            # else:
                # result.move_id.partner_id.write({'department_id': result.department_id.id})
        # return result
        #
    # def write(self, vals):
        # for record in self:
            # if vals.get('hr_id', False):
                # record.move_id.partner_id.write({'hr_id': vals.get('hr_id', False)})
            # if vals.get('department_id', False):
                # record.move_id.partner_id.write({'department_id': vals.get('department_id', False)})
        # return super(AccountMoveLine, self).write(vals)
        #
    # def unlink(self):
        # if self.filtered(lambda r: r.move_id and r.move_id.state not in ['draft','imported']):
            # raise UserError(_('You can only delete an invoice line if the invoice is in either draft or imported state.'))
        # return models.Model.unlink(self)

class PSPaymentType(models.Model):
    _name = 'ppc.paymenttype'
    _description = 'PPC Payment Type'
    _rec_name = 'ppc_paymenttype'

    ppc_paymenttype = fields.Char('PS Payment Type', required=True)
    payment_term = fields.Many2one('account.payment.term', 'Payment Term')
    ppv_vendorpayment = fields.Many2one('account.payment.term', 'PS INV05 Payment Term')

class PSInvoiceLine(models.Model):
    _name = 'ppc.invoiceline'
    _description = 'PPC Invoice Line'
    _rec_name = 'ppc_netvalueofarticles'

    ppc_netvalueofarticles = fields.Char('PS NetValue of Articles')
    ppc_netshipment = fields.Char('PS Netshipment')
    ppc_rebate = fields.Char('PS Rebate')
    ppv_netcommission = fields.Char('Net Commission')
    ppv_netdiscount = fields.Char('Net Discount')

# class AccountMoveLine(models.Model):
    # _inherit = "account.move.line"
    #
    # invl_id = fields.Many2one('account.invoice.line', string='Invoice Line')
    # department_id = fields.Many2one('invoice.department', string='Department',)
    # period_id = fields.Many2one('invoice.periode', string='Periode')
    # hr_id = fields.Many2one('invoice.hr', string='HR')
    # analytic_client = fields.Char('Analytic Client')
    #
    # @api.one
    # def _prepare_analytic_line(self):
        # """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            # an analytic account. This method is intended to be extended in other modules.
        # """
        # res = super(AccountMoveLine, self)._prepare_analytic_line()[0]
        # res['invl_id'] = self.invl_id and self.invl_id.id or False
        # res['department_id'] = self.invl_id and self.invl_id.department_id and self.invl_id.department_id.id or False
        # res['period_id'] = self.invl_id and self.invl_id.period_id and self.invl_id.period_id.id or False
        # res['hr_id'] = self.invl_id and self.invl_id.hr_id and self.invl_id.hr_id.id or False
        # res['analytic_client'] = self.invl_id and self.invl_id.analytic_client or ''
        # return res
        #
    # def _prepare_analytic_distribution_line(self, distribution):
        # """ Prepare the values used to create() an account.analytic.line upon validation of an account.move.line having
            # analytic tags with analytic distribution.
        # """
        # res = super(AccountMoveLine, self)._prepare_analytic_distribution_line(distribution)
        # res['invl_id'] = self.invl_id and self.invl_id.id or False
        # res['department_id'] = self.invl_id and self.invl_id.department_id and self.invl_id.department_id.id or False
        # res['period_id'] = self.invl_id and self.invl_id.period_id and self.invl_id.period_id.id or False
        # res['hr_id'] = self.invl_id and self.invl_id.hr_id and self.invl_id.hr_id.id or False
        # res['analytic_client'] = self.invl_id and self.invl_id.analytic_client or ''
        # return res

class DsScript(models.Model):
    _name = 'ds.script'
    _description = 'DS Script'
    _rec_name = 'analytic_dsimport_department'
#     name = fields.Char('DS Script', required=True)

    "Dropshipping Imports"
    analytic_dsimport_department = fields.Many2one('invoice.department', string='Dropshipping Department')
    analytic_dsimport_de = fields.Many2one('account.analytic.account', string='Dropshipping DE AA')
    analytic_dsimport_be = fields.Many2one('account.analytic.account', string='Dropshipping BE AA')
    analytic_dsimport_nl = fields.Many2one('account.analytic.account', string='Dropshipping NL AA')
    analytic_dsimport_fr = fields.Many2one('account.analytic.account', string='Dropshipping FR AA')

    "Various Imports"
    analytic_vsimport_department = fields.Many2one('invoice.department', string='Various Department')
    analytic_vsimport_de = fields.Many2one('account.analytic.account', string='Various DE VS')
    analytic_vsimport_be = fields.Many2one('account.analytic.account', string='Various BE VS')
    analytic_vsimport_nl = fields.Many2one('account.analytic.account', string='Various NL VS')
    analytic_vsimport_fr = fields.Many2one('account.analytic.account', string='Various FR VS')

    "HR Column"
    analytic_hrimport_de = fields.Many2one('invoice.hr', string='HR DE Tag')
    analytic_hrimport_be = fields.Many2one('invoice.hr', string='HR BE Tag')
    analytic_hrimport_nl = fields.Many2one('invoice.hr', string='HR NL Tag')
    analytic_hrimport_fr = fields.Many2one('invoice.hr', string='HR FR Tag')

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'

    market_partner_id = fields.Many2one('res.partner', string='Partner')
    market_start_date = fields.Date(string='Settlement Start Date')
    market_reserve_start = fields.Float(string='Current Reserve Amount')
    market_end_date = fields.Date(string='Settlement End Date')
    market_reserve_end = fields.Float(string='Previous Reserve Amount Balance')
    market_deposit_date = fields.Date(string='Deposit Date')
    market_amount = fields.Float(string='Total Amount')
    market_transaction_line_ids = fields.One2many('market.transaction.line', 'statement_id', string='Transaction Lines')

    @api.model
    def server_action_update_partner_on_bsl(self):
        """
        Within bank.statement, can you add an action in FORM VIEW  "Update Partner on BSL",
        it checks if the journal linked to the bank.statement has the the field "single_partner" = TRUE,
        if yes it set for all the bank.statement.lines linked to the bank.statement : partner_id = journal_partner_id (from account.journal)
        AND it set "market_partner_id" =  journal_partner_id (from account.journal).
        """
        active_ids = self._context.get('active_ids')
        for bank_statement in self.browse(active_ids):
            if bank_statement.journal_id.single_partner:
                if bank_statement.journal_id.journal_partner_id:
                    bank_statement.market_partner_id = bank_statement.journal_id.journal_partner_id.id
                    for line in bank_statement.line_ids:
                        line.partner_id = bank_statement.journal_id.journal_partner_id.id
                        line.partner_name = bank_statement.journal_id.journal_partner_id.display_name
        return True

class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)
    partner_type_id = fields.Many2one('res.partner.type', related='partner_id.partner_type_id', string='Partner Type', store=True)
    internal_notes = fields.Text(string="Internal Notes")
    market_place = fields.Char(string='Market Place')
    fulfillment = fields.Char(string='Fulfillment')
    price_principal = fields.Float(string='Price - Principal')
    price_returnshipping = fields.Float(string='Price - Shipping Return')
    price_shipping = fields.Float(string='Price - Shipping')
    price_shippingtax = fields.Float(string='Price - Shipping Tax')
    price_tax = fields.Float(string='Price - Principal Tax')
    com_principal = fields.Float(string='Com. Principal')
    com_refund = fields.Float(string='Com. Refund')
    com_shipping = fields.Float(string='Com. Shipping')
    com_variable = fields.Float(string='Com. Variable')
    com_total = fields.Float(string='Com. Total')
    posted_date_char = fields.Char(string='Posted Date')
    # statement_journal_id = fields.Many2one(related='statement_id.journal_id', string='Journal', store=True)
    # transaction_type_id = fields.Many2one('market.transaction.type', string='Transaction Type')

    def action_audit_label(self):
        ''' Open the audit label wizard to log audit action.
        :return: An action opening the audit action wizard.
        '''
        return {
            'name': _('Transaction Type'),
            'res_model': 'audit.label',
            'view_mode': 'form',
            'context': {
                'active_model': 'account.bank.statement.line',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }