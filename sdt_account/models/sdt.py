# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from dateutil.parser import parse

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from pickle import FALSE

class CountryAllocation(models.Model):
    _name= 'country.allocation'
    _description = 'Country Allocation'

    @api.depends('allocation_de', 'allocation_be', 'allocation_nl', 'allocation_fr')
    def _get_varification(self):
        for record in self:
            total_allowance = record.allocation_de + record.allocation_be + record.allocation_nl + record.allocation_fr
            record.verification = False
            if total_allowance == 100:
                record.verification = True

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)
    code = fields.Char('Code')
    allocation_de = fields.Float('DE', default=0.0)
    allocation_be = fields.Float('BE', default=0.0)
    allocation_nl = fields.Float('NL', default=0.0)
    allocation_fr = fields.Float('FR', default=0.0)
    verification = fields.Boolean(compute='_get_varification', string='Varification', store=True, readonly=True)

    def _check_allocation(self):
        """ Number must be between 0 and 100 """
        for allocation in self:
            if allocation.allocation_de < 0 or allocation.allocation_de > 100:
                return False
            if allocation.allocation_be < 0 or allocation.allocation_be > 100:
                return False
            if allocation.allocation_nl < 0 or allocation.allocation_nl > 100:
                return False
            if allocation.allocation_fr < 0 or allocation.allocation_fr > 100:
                return False
        return True

    _constraints = [
        (_check_allocation, 'Allocation must be between 0 and 100.', ['allocation_de', 'allocation_be', 'allocation_nl', 'allocation_fr']),
    ]


class PartnerMatching(models.Model):
    _name= 'partner.matching'
    _description = 'Partner Matching'

    name = fields.Char('Name')
    active = fields.Boolean('Active')
    matching_line_ids = fields.One2many('partner.matching.line', 'matching_id', string='Matching Lines')

class PartnerMatchingLine(models.Model):
    _name= 'partner.matching.line'
    _description = 'Partner Matching Line'

    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    partner_name = fields.Char('Partner Name', required=True)
    matching_id = fields.Many2one('partner.matching', string='Matching')

class AuditTemplate(models.Model):
    _name= 'audit.template'
    _description = 'Audit Template'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True, tracking=True)
    move_id = fields.Many2one('account.move', string='Template Created From', tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, tracking=True,default=lambda self: self.env.company)
    journal_id = fields.Many2one('account.journal', string='Journal', tracking=True)
    journal_ids = fields.Many2many('account.journal', string='Journals', tracking=True)
    audit_tax_grid = fields.Char(string='Audit Tax Grid', tracking=True)
    audit_invoice_line = fields.Char(string='Audit Invoice Line', tracking=True)
    audit_vat_country = fields.Char(string='Audit Vat Country', tracking=True)

    import_wizard = fields.Boolean(string='FTP Import', tracking=True)
    audit_06_rate = fields.Char(string='Audit 06 Rate', tracking=True)
    audit_variance = fields.Float(string='Audit Variance', tracking=True)
    state = fields.Selection([('inactive','Inactive'),
                              ('active','Active')], string='State', default='inactive', tracking=True)

    def action_active(self):
        return self.write({'state': 'active'})

    def action_inactive(self):
        return self.write({'state': 'inactive'})

    @api.model
    def server_action_set_journals(self):
        """
           As we decided to have journals as many2many on audit templates. I write this server action to update journal_ids with existing journal_id.
           This is a one time server action which we can remove once used
        """
        active_ids = self._context.get('active_ids')
        for template in self.browse(active_ids):
            if template.journal_id:
                template.journal_ids = [(6,0,[template.journal_id.id])]
        return True

class MarketTransactionType(models.Model):
    _name = 'market.transaction.type'
    _description = 'Market Transaction Type'

    name = fields.Char(string='Transaction Type', required=True)

class MarketTransactionLine(models.Model):
    _name = 'market.transaction.line'
    _description = 'Market Transaction Lines'
    _rec_name = 'statement_id'

    statement_id = fields.Many2one('account.bank.statement', string='Statement')
    market_statement_id = fields.Many2one('market.statement', string='Market Statement')
    transaction_type_id = fields.Many2one('market.transaction.type', string='Transaction Type')
    date = fields.Date(string='Date')
    amount = fields.Float(string='Amount')

class MarketJournal(models.Model):
    _name= 'market.journal'
    _description = 'market.journal'
    _inherit = ['mail.thread']

    name = fields.Char(string='Name', required=True, tracking=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, tracking=True,default=lambda self: self.env.company)

class MarketStatement(models.Model):
    _name= 'market.statement'
    _description = 'Market Statement'
    _inherit = ['mail.thread']

    name = fields.Char(string='Reference', required=True, tracking=True)
    market_journal_id = fields.Many2one('market.journal', string='Market Journal', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, tracking=True ,default=lambda self: self.env.company)
    market_partner_id = fields.Many2one('res.partner', string='Partner')
    bank_statement_line_id = fields.Many2one('account.bank.statement.line', string='Bank Statement Line')
    market_start_date = fields.Date(string='Settlement Start Date')
    market_reserve_start = fields.Float(string='Current Reserve Amount')
    market_end_date = fields.Date(string='Settlement End Date')
    market_reserve_end = fields.Float(string='Previous Reserve Amount Balance')
    market_deposit_date = fields.Date(string='Deposit Date')
    market_amount = fields.Float(string='Total Amount')
    market_statement_line_ids = fields.One2many('market.statement.line', 'market_statement_id', string='Transaction Lines')
    market_transaction_line_ids = fields.One2many('market.transaction.line', 'market_statement_id', string='Transaction Lines')

    def name_get(self):
        result = []
        for data in self:
            name = data.name
            if data.market_end_date:
                # fiscal_year = data.document_date.split('-')[0][2:]
                name += ' '+ '['+ data.market_end_date.strftime('%d-%m-%Y')+ ']'
            result.append((data.id, name))
        return result

    def link_account_move_to_lines(self):
        """
        1.  Transaction type: Order then Bill (transaction type: refund then credit note)
        2. The label (msl) = the payment reference (account.move)
        3. The amount (msl) = the total amount (account.move)
        —> here we shall use rounded amount with 2 digits.
        """
        for line in self.market_statement_line_ids:
            # if not line.move_id:
            if line.state in ('new','pending','blocked','pending_multiple'):
                move_ids = False
                line.move_ids = [(6, 0, [])]
                line.move_id = False
                if line.transaction_type == 'Order':
                    #commented search is for my testing
                    # move_ids = self.env['account.move'].search([('move_type', 'in', ['out_invoice','in_invoice']),
                                                                # ('state','=','posted')])
                    move_ids = self.env['account.move'].search([('move_type', 'in', ['out_invoice','in_invoice']),
                                                                ('state','=','posted'),
                                                                ('payment_state','=','not_paid'),
                                                                # ('market_statement_line_id','=',False),
                                                                ('payment_reference','=',line.payment_ref)])

                if line.transaction_type == 'refund':
                    move_ids = self.env['account.move'].search([('move_type', '=', ['out_refund','in_refund']),
                                                                ('state','=','posted'),
                                                                ('payment_state','=','not_paid'),
                                                                # ('market_statement_line_id','=',False),
                                                                ('payment_reference','=',line.payment_ref)])
                if move_ids:
                    if len(move_ids)>1:
                        line.state = 'pending_multiple'
                        line.move_ids = [(6, 0, move_ids.ids)]
                    else:
                        line.move_id = move_ids.id
                        move_ids.market_statement_line_id = line.id
                        if int(move_ids.amount_total) == int(line.amount):
                            line.state = 'matched'
                        else:
                            line.state = 'blocked'
                            line.move_amount_total = move_ids.amount_total
                            # line.internal_notes = _("Amount on market statement line: %f doesn't match to amount on Move: %f", line.amount, move.amount_total)
                if not move_ids:
                    line.state = 'pending'
        return True

class MarketStatementLine(models.Model):
    _name= 'market.statement.line'
    _description = 'Market Statement Lines'
    _inherit = ['mail.thread']
    _rec_name = 'payment_ref'

    move_id = fields.Many2one(
        comodel_name='account.move',
        string='Account Move')
    move_ids = fields.One2many('account.move', 'market_statement_line_id', string='Matched Account Moves')
    market_statement_id = fields.Many2one(
        comodel_name='market.statement',
        string='Statement', index=True, required=True, ondelete='cascade')

    sequence = fields.Integer(index=True, help="Gives the sequence order when displaying a list of bank statement lines.", default=1)
    transaction_type = fields.Char(string='Transaction Type')
    payment_ref = fields.Char(string='Label')
    ref = fields.Char(string='Reference')
    amount = fields.Monetary(currency_field='currency_id')
    move_amount_total = fields.Monetary(related='move_id.amount_total', string='INV(06) Total')
    audit_delta = fields.Float(string='Audit Delta', compute='_compute_audit_delta', help="Total Amount - INV(O6) Total = Audit Delta")
    amount_currency = fields.Monetary(currency_field='foreign_currency_id',
        help="The amount expressed in an optional other currency if it is a multi-currency entry.")
    foreign_currency_id = fields.Many2one('res.currency', string='Foreign Currency',
        help="The optional other currency if it is a multi-currency entry.")
    currency_id = fields.Many2one('res.currency', string='Journal Currency')
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner', ondelete='restrict',
        domain="['|', ('parent_id','=', False), ('is_company','=',True)]")
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)
    date = fields.Date(string='Date')
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
    state = fields.Selection([
        ('new', 'New'),
        ('matched', 'Matched'),
        ('matched_with_delta', 'Matched With Delta'),
        ('pending', 'Pending'),
        ('pending_multiple', 'Pending Multiple'),
        ('blocked', 'Blocked')], string='State',
        copy=False, default='new',
        help="State will be decided based on move matched to this MSL:\n"
             "  - New: All records will be in new state when created.\n"
             "  - Matched: When Amount on MSL and Total Amount matched exactly.\n"
             "  - Matched With Delta: When forcefully Matched any Move to MSL.\n"
             "  - Pending: If no matching move found.\n"
             "  - Pending Multiple: If multiple matching move found.\n"
             "  - Blocked: When Move found but amount doesn't matches.\n")

    @api.depends('amount', 'audit_delta', 'move_id')
    def _compute_audit_delta(self):
        for line in self:
            # Market Total Amount - INV(O6) = Audit Delta
            line.audit_delta = 0
            if line.move_id:
                line.audit_delta = line.amount - line.move_id.amount_total

    def server_action_link_move(self):
        """
        1.  Transaction type: Order then Bill (transaction type: refund then credit note)
        2. The label (msl) = the payment reference (account.move)
        3. The amount (msl) = the total amount (account.move)
        —> here we shall use rounded amount with 2 digits.
        """
        active_ids = self._context.get('active_ids')
        for line in self.browse(active_ids):
            # if not line.move_id:
            if line.state in ('new','pending','blocked','pending_multiple'):
                move_ids = False
                line.move_ids = [(6, 0, [])]
                line.move_id = False
                if line.transaction_type == 'Order':
                    #commented search is for my testing
                    # move_ids = self.env['account.move'].search([('move_type', 'in', ['out_invoice','in_invoice']),
                                                                # ('state','=','posted')])
                    move_ids = self.env['account.move'].search([('move_type', 'in', ['out_invoice','in_invoice']),
                                                                ('state','=','posted'),
                                                                ('payment_state','=','not_paid'),
                                                                # ('market_statement_line_id','=',False),
                                                                ('payment_reference','=',line.payment_ref)])

                if line.transaction_type == 'refund':
                    move_ids = self.env['account.move'].search([('move_type', '=', ['out_refund','in_refund']),
                                                                ('state','=','posted'),
                                                                ('payment_state','=','not_paid'),
                                                                # ('market_statement_line_id','=',False),
                                                                ('payment_reference','=',line.payment_ref)])
                if move_ids:
                    if len(move_ids)>1:
                        line.state = 'pending_multiple'
                        line.move_ids = [(6, 0, move_ids.ids)]
                    else:
                        line.move_id = move_ids.id
                        move_ids.market_statement_line_id = line.id
                        if int(move_ids.amount_total) == int(line.amount):
                            line.state = 'matched'
                        else:
                            line.state = 'blocked'
                            line.move_amount_total = move_ids.amount_total
                            # line.internal_notes = _("Amount on market statement line: %f doesn't match to amount on Move: %f", line.amount, move.amount_total)
                if not move_ids:
                    line.state = 'pending'
        return True

class AccountChangeLockDateLog(models.Model):
    _name= 'account.change.lock.date.log'
    _description = 'Lock Date Change Log'
    _inherit = ['mail.thread']
"""
Could you create in "Back Office", Menu Configuration a new model: "account.change.lock.date.log"
Each time there is a change in the value of the field related to "account.change.lock.date"
- period_lock_date
- fiscalyear_lock_date
- tax_lock_date
- vat_lock_date


We need to have a log with:
- Create On (date)
- Modify By (res.user)
- Res.company (res.company)
- Note (char)
- Period Lock Date (value)
- Fiscal Lock Date (value)
- Tax Lock Date (value)
"""

class MarketAmazon(models.Model):
    _name= 'market.amazon'
    _description = 'Market Amazon'
    _inherit = ['mail.thread']

    @api.depends('order_id', 'transaction_type', 'sku')
    def _compute_name(self):
        for record in self:
            name = ''
            if record.order_id:
                name = '[' + record.order_id + '] '
            if record.transaction_type:
                name += record.transaction_type
            # if record.book:
                # name += ' (' + record.book +')'
            if record.sku:
                name += ' / ' + record.sku
            record.name = name

    @api.depends('order_date')
    def _get_order_date(self):
        """
        Return date field from the char field
        """
        for record in self:
            if record.order_date:
                order_date = record.order_date[:-4]
                order_date = datetime.strptime(order_date,"%d-%b-%Y")
                record.order_date_date = datetime.strftime(order_date, DEFAULT_SERVER_DATE_FORMAT)

    @api.depends('shipment_date')
    def _get_shipment_date(self):
        """
        Return date field from the char field
        """
        for record in self:
            if record.shipment_date:
                shipment_date = record.shipment_date[:-4]
                shipment_date = datetime.strptime(shipment_date,"%d-%b-%Y")
                record.shipment_date_date = datetime.strftime(shipment_date, DEFAULT_SERVER_DATE_FORMAT)

    @api.depends('tax_calculation_date')
    def _get_tax_calculation_date(self):
        """
        Return date field from the char field
        """
        for record in self:
            if record.tax_calculation_date:
                tax_calculation_date = record.tax_calculation_date[:-4]
                tax_calculation_date = datetime.strptime(tax_calculation_date,"%d-%b-%Y")
                record.tax_calculation_date_date = datetime.strftime(tax_calculation_date, DEFAULT_SERVER_DATE_FORMAT)

    name = fields.Char(compute='_compute_name', store=False)
# Marketplace ID,"Merchant ID","Order Date","Transaction Type","Is Invoice Corrected","Order ID","Shipment Date",
# DE,72998151612,"27-Nov-2021 UTC",SHIPMENT,FALSE,028-2366379-9105113,"30-Nov-2021 UTC",
    marketplace_id = fields.Char(string='Marketplace ID', required=True, tracking=True)
    merchant_id = fields.Char(string='Merchant ID', tracking=True)
    order_date = fields.Char(string='Order Date', tracking=True)
    order_date_date = fields.Date(string='Order Date', compute='_get_order_date', store=True)
    transaction_type = fields.Char(string='Transaction Type', tracking=True)
    is_invoice_corrected = fields.Boolean(string='Is Invoice Corrected', tracking=True)
    order_id = fields.Char(string='Order ID', tracking=True)
    shipment_date = fields.Char(string='Shipment Date', tracking=True)
    shipment_date_date = fields.Date(string='Shipment Date', compute='_get_shipment_date', store=True)

# "Shipment ID","Transaction ID",ASIN,SKU,Quantity,"Tax Calculation Date","Tax Rate","Product Tax Code",Currency,"Tax Type",
# 15566533008039,15566533008039,B004I2C4PU,B167501,1,"27-Nov-2021 UTC",0.1900,A_GEN_STANDARD,EUR,VAT,
    shipment_id = fields.Char(string='Shipment ID', tracking=True)
    transaction_id = fields.Char(string='Transaction ID', tracking=True)
    asin = fields.Char(string='ASIN', tracking=True)
    sku = fields.Char(string='SKU', tracking=True)
    quantity = fields.Integer(string='Quantity', tracking=True)
    tax_calculation_date = fields.Char(string='Tax Calculation Date', tracking=True)
    tax_calculation_date_date = fields.Date(string='Tax Calculation Date', compute='_get_tax_calculation_date', store=True)
    tax_rate = fields.Float(string='Tax Rate', tracking=True)
    product_tax_code = fields.Char(string='Product Tax Code', tracking=True)
    currency = fields.Char(string='Currency', tracking=True)
    tax_type = fields.Char(string='Tax Type', tracking=True)

# "Tax Calculation Reason Code","Tax Reporting Scheme","Tax Collection Responsibility","Tax Address Role","Jurisdiction Level","Jurisdiction Name",
# Taxable,,Seller,ShipTo,Country,GERMANY,
    tax_calculation_reason_code = fields.Char(string='Tax Calculation Reason Code', tracking=True)
    tax_reporting_scheme = fields.Char(string='Tax Reporting Scheme', tracking=True)
    tax_collection_responsibility = fields.Char(string='Tax Collection Responsibility', tracking=True)
    tax_address_role = fields.Char(string='Tax Address Role', tracking=True)
    jurisdiction_level = fields.Char(string='Jurisdiction Level', tracking=True)
    jurisdiction_name = fields.Char(string='Jurisdiction Name', tracking=True)

# "OUR_PRICE Tax Inclusive Selling Price","OUR_PRICE Tax Amount","OUR_PRICE Tax Exclusive Selling Price","OUR_PRICE Tax Inclusive Promo Amount",
# "OUR_PRICE Tax Amount Promo","OUR_PRICE Tax Exclusive Promo Amount","SHIPPING Tax Inclusive Selling Price","SHIPPING Tax Amount",
# "SHIPPING Tax Exclusive Selling Price","SHIPPING Tax Inclusive Promo Amount","SHIPPING Tax Amount Promo","SHIPPING Tax Exclusive Promo Amount",
# "GIFTWRAP Tax Inclusive Selling Price","GIFTWRAP Tax Amount","GIFTWRAP Tax Exclusive Selling Price","GIFTWRAP Tax Inclusive Promo Amount",
# "GIFTWRAP Tax Amount Promo","GIFTWRAP Tax Exclusive Promo Amount",
# 9.64,1.54,8.10,0.00,0.00,0.00,4.89,0.78,4.11,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,
    our_price_tax_inc_selling_price = fields.Float(string="OUR_PRICE Tax Inclusive Selling Price", tracking=True)
    our_price_tax_amount = fields.Float(string="OUR_PRICE Tax Amount", tracking=True)
    our_price_tax_exc_selling_price = fields.Float(string="OUR_PRICE Tax Exclusive Selling Price", tracking=True)
    our_price_tax_inc_promo_amount = fields.Float(string="OUR_PRICE Tax Inclusive Promo Amount", tracking=True)
    our_price_tax_amount_promo = fields.Float(string="OUR_PRICE Tax Amount Promo", tracking=True)
    our_price_tax_exc_promo_amount = fields.Float(string="OUR_PRICE Tax Exclusive Promo Amount", tracking=True)
    shipping_tax_inc_selling_price = fields.Float(string="SHIPPING Tax Inclusive Selling Price", tracking=True)
    shipping_tax_amount = fields.Float(string="SHIPPING Tax Amount", tracking=True)
    shipping_tax_exc_selling_price = fields.Float(string="SHIPPING Tax Exclusive Selling Price", tracking=True)
    shipping_tax_inc_promo_amount = fields.Float(string="SHIPPING Tax Inclusive Promo Amount", tracking=True)
    shipping_tax_amount_promo = fields.Float(string="SHIPPING Tax Amount Promo", tracking=True)
    shipping_tax_exc_promo_amount = fields.Float(string="SHIPPING Tax Exclusive Promo Amount", tracking=True)
    giftwrap_tax_inc_selling_price = fields.Float(string="GIFTWRAP Tax Inclusive Selling Price", tracking=True)
    giftwrap_tax_amount = fields.Float(string="GIFTWRAP Tax Amount", tracking=True)
    giftwrap_tax_exc_selling_price = fields.Float(string="GIFTWRAP Tax Exclusive Selling Price", tracking=True)
    giftwrap_tax_inc_promo_amount = fields.Float(string="GIFTWRAP Tax Inclusive Promo Amount", tracking=True)
    giftwrap_tax_amount_promo = fields.Float(string="GIFTWRAP Tax Amount Promo", tracking=True)
    giftwrap_tax_exc_promo_amount = fields.Float(string="GIFTWRAP Tax Exclusive Promo Amount", tracking=True)

# "Seller Tax Registration","Seller Tax Registration Jurisdiction","Buyer Tax Registration","Buyer Tax Registration Jurisdiction","Buyer Tax Registration Type",
# "Buyer E Invoice Account Id","Invoice Level Currency Code","Invoice Level Exchange Rate",
# "Invoice Level Exchange Rate Date","Converted Tax Amount","VAT Invoice Number",
# DE319091817,DE,,,,,,0.0000,,0.00,"INV-DE-1305902485-2021-10882",
    seller_tax_registration = fields.Char(string="Seller Tax Registration", tracking=True)
    seller_tax_registration_jurisdiction = fields.Char(string="Seller Tax Registration Jurisdiction", tracking=True)
    buyer_tax_registration = fields.Char(string="Buyer Tax Registration", tracking=True)
    buyer_tax_registration_jurisdiction = fields.Char(string="Buyer Tax Registration Jurisdiction", tracking=True)
    buyer_tax_tegistration_type = fields.Char(string="Buyer Tax Registration Type", tracking=True)
    buyer_envoice_account_id = fields.Char(string="Buyer E Invoice Account Id", tracking=True)
    invoice_level_currency_code = fields.Char(string="Invoice Level Currency Code", tracking=True)
    invoice_level_exchange_rate = fields.Float(string="Invoice Level Exchange Rate", tracking=True)
    invoice_level_exchange_rate_date = fields.Char(string="Invoice Level Exchange Rate Date", tracking=True)
    converted_tax_amount = fields.Float(string="Converted Tax Amount", tracking=True)
    vat_invoice_number = fields.Char(string="VAT Invoice Number", tracking=True)

# "Invoice Url",
# "Export Outside EU",
# "https://www.Amazon.de/gp/invoice/download.html?v=urn%3aalx%3adoc%3a9d8cab0f-1f96-4462-8642-ace99a371392%3a6d17340b-4776-48b5-be38-d0b6f4d01fe7&t=EU_Retail_Forward",
# false,
    invoice_url = fields.Char(string="Invoice URL")
    export_outside_eu = fields.Boolean(string="Export Outside EU")

# "Ship From City","Ship From State","Ship From Country","Ship From Postal Code","Ship From Tax Location Code","Ship To City","Ship To State",
# "Ship To Country","Ship To Postal Code","Ship To Location Code",
# "Return Fc Country","Is Amazon Invoiced","Original VAT Invoice Number",
# "Invoice Correction Details","SDI Invoice Delivery Status","SDI Invoice Error Code","SDI Invoice Error Description",
# "SDI Invoice Status Last Updated Date","EInvoice URL"
# Burgwedel,,DE,30938,802760000,"Mülheim (Mosel)",,DE,54486,802760000,,true,,,,,,,
    ship_from_city = fields.Char(string="Ship From City")
    ship_from_state = fields.Char(string="Ship From State")
    ship_from_country = fields.Char(string="Ship From Country")
    ship_from_postal_code = fields.Char(string="Ship From Postal Code")
    ship_from_tax_location_code = fields.Char(string="Ship From Tax Location Code")
    ship_to_city = fields.Char(string="Ship To City")
    ship_to_state = fields.Char(string="Ship To State")
    ship_to_country = fields.Char(string="Ship To Country")
    ship_to_postal_code = fields.Char(string="Ship To Postal Code")
    ship_to_location_code = fields.Char(string="Ship To Location Code")
    return_fc_country = fields.Char(string="Return Fc Country")
    is_amazon_invoiced = fields.Boolean(string="Is Amazon Invoiced")
    original_vat_invoice_number = fields.Char(string="Original VAT Invoice Number")
    invoice_correction_details = fields.Char(string="Invoice Correction Details")
    sdi_invoice_delivery_status = fields.Char(string="SDI Invoice Delivery Status")
    sdi_invoice_error_code = fields.Char(string="SDI Invoice Error Code")
    sdi_invoice_error_description = fields.Char(string="SDI Invoice Error Description")
    sdi_invoice_status_last_updated_date = fields.Char(string="SDI Invoice Status Last Updated Date")
    einvoice_url = fields.Char(string="EInvoice URL")
    
    general_product_id = fields.Many2one('product.product', string='General Product')
    record_created_from = fields.Char(string='Record Created From')

    state = fields.Selection([('new','New'),
                              ('todo','To Do'),
                              ('done','Converted'),
                              ('blocked','Blocked'),
                              ('cancel','Cancelled')], default='new', index=True, readonly=True,
                              string='Status', copy=False,
                              help=" * 'To Do': is when it is imported\n"
                                   " * 'Done': when it is converted into a bill\n"
                                   " * 'Blocked': is when it occurs an issue (the info don't match the import configuration)", tracking=True)
    import_config_id = fields.Many2one('import.config.amazon', string='Import Configuration', tracking=True)
    reason_for_blocking = fields.Text(string='Reason of Blocking', tracking=True)
    fiscal_position = fields.Selection([('Final Customer','Final Customer'),
                                        ('b2b','B2B'),
                                        ('intra_community','Intra-Community'),], string='Fiscal Position')
    sale_invoice_id = fields.Many2one('account.move', string='ACC Invoice ID', tracking=True)
    cn_invoice_id = fields.Many2one('account.move', string='ACC Invoice CN ID', tracking=True)
# 8. In Other Details (Market Amazon), could you create 3 compute fields:
# - Total Tax Excluded (sum of Green fields)
# - Total Tax (sum of Blue Fields)
# - Total Tax Included (Sum of Yellow Fields)
    total_tax_excluded = fields.Float(string='Total Tax Excluded', compute='_get_total_tax_excluded', store=True)
    @api.depends('our_price_tax_exc_selling_price','shipping_tax_exc_selling_price', 'giftwrap_tax_exc_selling_price')
    def _get_total_tax_excluded(self):
        for record in self:
            record.total_tax_excluded = record.our_price_tax_exc_selling_price + record.shipping_tax_exc_selling_price + record.giftwrap_tax_exc_selling_price

    total_tax = fields.Float(string='Total Tax', compute='_get_total_tax', store=True)
    @api.depends('our_price_tax_amount','shipping_tax_amount', 'giftwrap_tax_amount')
    def _get_total_tax(self):
        for record in self:
            record.total_tax = record.our_price_tax_amount + record.shipping_tax_amount + record.giftwrap_tax_amount

    total_tax_included = fields.Float(string='Total Tax Included', compute='_get_total_tax_included', store=True)
    @api.depends('our_price_tax_inc_selling_price','shipping_tax_inc_selling_price','giftwrap_tax_inc_selling_price')
    def _get_total_tax_included(self):
        for record in self:
            record.total_tax_included = record.our_price_tax_inc_selling_price + record.shipping_tax_inc_selling_price + record.giftwrap_tax_inc_selling_price

    def action_assign_config(self):
        """
        In order to link, 
        (1) tax_type (in market.amazon) = VAT   AND    tax_calculation_reason_code = Taxable
        -----> if it doesnt: State = Blocked AND  "reason_for_blocking" = Not Taxable according to Amazon"
        (2) If the following fields: "OUR_PRICE Tax Inclusive Promo Amount",
                                     "SHIPPING Tax Inclusive Promo Amount",
                                     "GIFTWRAP Tax Inclusive Promo Amount" are not ALL equals to 0.00, 
                                     we can set the condition as the SUM of those 3 fields = 0, 
        ----> if it doesnt: State = Blocked AND  "reason_for_blocking" = "PROMO Amounts are positive"
        (3) each entres need to match their value between "market.amazon" AND " import.config.amazon" for the 4 following fields
        - Transaction Type, transaction_type(char record), transaction_type(selection field on config) 
        - Seller Tax Registration Juridiction, seller_tax_registration_jurisdiction(char on record), seller_tax_registration_jurisdiction(M2o on config)
        - Buyer Tax Registration Juridiction, buyer_tax_registration_jurisdiction(char on recrod), buyer_tax_registration_jurisdiction(M2o on config)
        - Tax Rate, tax_rate(float), tax_rate(float)
        !!! Blanck value need to match with Blanck value for Buyer/Seller Tax Juridication.
        ------> "import_config_id" is linked to an "Import Configuration Amazon" entry.
        """
        records = self.filtered(lambda rec: rec.state != 'done')
        for rec in records:
            if not rec.tax_type == 'VAT' or not rec.tax_calculation_reason_code == 'Taxable':
                rec.reason_for_blocking = 'Not Taxable according to Amazon'
                rec.state = 'blocked'
            if rec.our_price_tax_inc_promo_amount + rec.shipping_tax_inc_promo_amount + rec.giftwrap_tax_inc_promo_amount != 0:
                rec.reason_for_blocking = 'PROMO Amounts are positive'
                rec.state = 'blocked'
            transaction_type = False
            seller_tax_registration_jurisdiction = False
            buyer_tax_registration_jurisdiction = False
            if rec.transaction_type:
                if rec.transaction_type == 'SHIPMENT':
                    transaction_type = 'shipment'
                if rec.transaction_type == 'REFUND':
                    transaction_type = 'refund'
            if rec.seller_tax_registration_jurisdiction:
                seller_tax_registration_jurisdiction = self.env['tax.juridiction'].search([('name','=',rec.seller_tax_registration_jurisdiction),
                                                                                            ('active','=',True)], limit=1)
                seller_tax_registration_jurisdiction = seller_tax_registration_jurisdiction and seller_tax_registration_jurisdiction.id or False
            if rec.buyer_tax_registration_jurisdiction:
                buyer_tax_registration_jurisdiction = self.env['tax.juridiction'].search([('name','=',rec.buyer_tax_registration_jurisdiction),
                                                                                            ('active','=',True)], limit=1)
                buyer_tax_registration_jurisdiction = buyer_tax_registration_jurisdiction and buyer_tax_registration_jurisdiction.id or False
            import_config_id = self.env['import.config.amazon'].search([('transaction_type','=', transaction_type),
                                                                        ('seller_tax_registration_jurisdiction','=',seller_tax_registration_jurisdiction),
                                                                        ('buyer_tax_registration_jurisdiction','=',buyer_tax_registration_jurisdiction),
                                                                        ('tax_rate','=',rec.tax_rate)], limit=1)
            if not import_config_id:
                rec.import_config_id = False
                rec.state = 'blocked'
                rec.reason_for_blocking = "System can't find any matching configuration!"
            else:
                if import_config_id.product_tax_code:
                    general_product = False
                    for tax_line in import_config_id.amazon_config_tax_code_lines:
                        if rec.product_tax_code == tax_line.product_tax_code:
                            general_product = tax_line.product_id.id
                    rec.import_config_id = import_config_id.id
                    rec.fiscal_position = import_config_id.fiscal_position or ''
                    if not general_product:
                        rec.state = 'blocked'
                        rec.reason_for_blocking = "System can't find the matching Product Tax Code!"
                    else:
                        rec.state = 'todo'
                        rec.general_product_id = general_product
                        rec.reason_for_blocking = ''
                else:
                    rec.state = 'todo'
                    rec.reason_for_blocking = ''
                    rec.import_config_id = import_config_id.id
                    rec.general_product_id = import_config_id.general_product_id and import_config_id.general_product_id.id or False
                    rec.fiscal_position = import_config_id.fiscal_position or ''
        return True

    def action_cancel(self):
        # if self.filtered(lambda rec: rec.state in ('done', 'cancel')):
            # raise UserError(_("You can't cancel the Done records."))
        return self.write({'state': 'cancel'})

    def action_cancel_blocked(self):
        """
        1. Candel Blocked Records
        """
        active_ids = self._context.get('active_ids')
        for record in self.browse(active_ids):
            if record.state == 'blocked':
                record.state = 'cancel'
        return True

    def action_todo(self):
        # if self.filtered(lambda rec: rec.state in ('done', 'cancel')):
            # raise UserError(_("You can't cancel the Done records."))
        return self.write({'state': 'todo'})

    def action_new(self):
        # if self.filtered(lambda rec: rec.state in ('done', 'cancel')):
            # raise UserError(_("You can't cancel the Done records."))
        return self.write({'state': 'new'})

    @api.model
    def generate_inv_bills_cron(self):
        for i in range(3):
            for record in self.search([('state', '=', 'todo')], limit=100):
                if record.import_config_id:
                    record.generate_inv_bills()

    def generate_inv_bills(self):
        invoice_pool = self.env['account.move']

        for rec in self:
            if rec.state != 'todo':
                rec.state = 'blocked'
                rec.reason_for_blocking = "You are trying to generate inv/bill from a record which is not in todo state!"
                continue
            if not rec.import_config_id:
                rec.state = 'blocked'
                rec.reason_for_blocking = "System can't find any matching configuration!"
                continue

            document_name = rec.vat_invoice_number + '/' + rec.sku
            journal_id = self.env['account.journal'].sudo().browse(rec.import_config_id.journal_id.id)
            inv_vals = {
                'company_id': rec.import_config_id.company_id.id,
                'journal_id': journal_id.id,
                'import_wizard': True,
                'amazon_invoice': True,
                'amazon_raw_data_id': rec.id,
                'buyer_tax_registration_jurisdiction': rec.buyer_tax_registration_jurisdiction,
                # 'name': document_name,
                'partner_id': rec.import_config_id.customer_partner.id,
                'invoice_origin': rec.order_id,
                'invoice_date': rec.shipment_date_date,
                'payment_reference': rec.vat_invoice_number,
                'venice_sinvoicedocnumber': document_name,
                'product_tax_code': rec.product_tax_code,
                # 'invoice_payment_term_id': rec.
                # 'invoice_date_due': date_due,
            }

            if rec.import_config_id.type == 'SELLER':
                customer_invoice_line_data = []
                if abs(rec.our_price_tax_exc_selling_price) > 0 and rec.general_product_id:
                    customer_invoice_line_data.append((0,0, {
                                                            'quantity': 1,
                                                            'product_id': rec.general_product_id.id,
                                                            'account_id': rec.general_product_id.property_account_income_id.id,
                                                            'price_unit': abs(rec.our_price_tax_exc_selling_price),
                                                            'tax_ids': [(6, 0, rec.general_product_id.taxes_id.ids)],
                                                            }))
                if abs(rec.shipping_tax_exc_selling_price) > 0 and rec.import_config_id.product_shipping_id:
                    customer_invoice_line_data.append((0,0, {
                                                            'quantity': 1,
                                                            'product_id': rec.import_config_id.product_shipping_id.id,
                                                            'account_id': rec.import_config_id.product_shipping_id.property_account_income_id.id,
                                                            'price_unit': abs(rec.shipping_tax_exc_selling_price),
                                                            'tax_ids': [(6, 0, rec.import_config_id.product_shipping_id.taxes_id.ids)],
                                                            }))
                if abs(rec.giftwrap_tax_exc_selling_price) > 0 and rec.import_config_id.giftwrap_product_id:
                    customer_invoice_line_data.append((0,0, {
                                                            'quantity': 1,
                                                            'product_id': rec.import_config_id.giftwrap_product_id.id,
                                                            'account_id': rec.import_config_id.giftwrap_product_id.property_account_income_id.id,
                                                            'price_unit': abs(rec.giftwrap_tax_exc_selling_price),
                                                            'tax_ids': [(6, 0, rec.import_config_id.giftwrap_product_id.taxes_id.ids)],
                                                            }))

                if rec.import_config_id.document_type == 'invoice':
                    inv_vals['move_type'] = 'out_invoice'
                    inv_vals['invoice_line_ids'] = customer_invoice_line_data
                    # invoice_id = invoice_pool.search([('name','=',document_name),('move_type','=','out_invoice'),('state','in',('draft','imported'))])
                    if rec.sale_invoice_id and rec.sale_invoice_id.state in ['draft','imported']:
                        rec.sale_invoice_id.sudo().write(inv_vals)
                    else:
                        invoice_id = invoice_pool.sudo().create(inv_vals)
                        rec.sale_invoice_id = invoice_id.id

                if rec.import_config_id.document_type == 'creditnote':
                    inv_vals['move_type'] = 'out_refund'
                    inv_vals['invoice_line_ids'] = customer_invoice_line_data
                    # invoice_id = invoice_pool.search([('name','=',document_name),('move_type','=','out_refund'),('state','in',('draft','imported'))])
                    if rec.cn_invoice_id and rec.cn_invoice_id.state in ['draft','imported']:
                        rec.cn_invoice_id.sudo().write(inv_vals)
                    else:
                        invoice_id = invoice_pool.sudo().create(inv_vals)
                        rec.cn_invoice_id = invoice_id.id

            rec.state = 'done'
        return True

    def action_record_created_from(self):
        ''' Open the record created from wizard to update field on market amazon.
        :return: An action opening the record created from wizard.
        '''
        return {
            'name': _('Record Created From'),
            'res_model': 'update.record.created.from',
            'view_mode': 'form',
            'context': {
                'active_model': 'market.amazon',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }