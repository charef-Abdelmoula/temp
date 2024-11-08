# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime
from dateutil.parser import parse

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

class FTPData(models.Model):
    _name = 'ftp.data'
    _description = 'RAW data imported from ftp file'
    _inherit = ['mail.thread']
    # _rec_name = 'document_number'

    name = fields.Char(string='Name')
    # Common Fields
    country = fields.Char(string='Country')
    book = fields.Char(string='Book')
    document_type = fields.Char(string='Document type')
    document_number = fields.Char(string='Document number')
    purchase_order_no = fields.Char(string='purchase order no.')
    sales_order_no = fields.Char(string='sales order no.')
    document_date = fields.Char(string='Document date')
    document_date_date = fields.Date(string='Document Date', compute='_get_document_date', store=True)
    vat_system = fields.Char(string='VAT system')
    vat_amount_1 = fields.Float(string='VAT amount #1')
    vat_amount_2 = fields.Float(string='VAT amount #2')
    vat_amount_3 = fields.Float(string='VAT amount #3')
    vat_amount_4 = fields.Float(string='VAT amount #4')
    expiry_date = fields.Char(string='Expiry date')

    # PINV Fields
    supplier_number = fields.Integer(string='Supplier number')
    supplier_name = fields.Char(string='Supplier Name')
    remarks_vendor_inv_no = fields.Char(string='Remark (vendor invoice number)')
    vat_rate_1 = fields.Float(string='amount ex-VAT (VAT rate #1)', tracking=True)
    vat_rate_2 = fields.Float(string='amount ex-VAT (VAT rate #2)', tracking=True)
    vat_rate_3 = fields.Float(string='amount ex-VAT (VAT rate #3)', tracking=True)
    vat_rate_4 = fields.Float(string='amount ex-VAT (VAT rate #4)', tracking=True)
    vat_rate_total = fields.Float(string='amount ex VAT total', tracking=True)
    vat_total = fields.Float(string='VAT total', tracking=True)
    document_total = fields.Float(string='document total', tracking=True)
    check_amount_by_sup_document = fields.Float(string='check Amount by supplier document')
    cash_discount_rate_percentage = fields.Float(string='cash discount rate in %')
    cash_discount_vat_rate_1 = fields.Float(string='cash discount ex-VAT (VAT rate #1)')
    cash_discount_vat_amount_1 = fields.Float(string='VAT amount cash discount #1')
    cash_discount_vat_rate_2 = fields.Float(string='cash discount ex-VAT (VAT rate #2)')
    cash_discount_vat_amount_2 = fields.Float(string='VAT amount cash discount #2')
    cash_discount_vat_rate_3 = fields.Float(string='cash discount ex-VAT (VAT rate #3)')
    cash_discount_vat_amount_3 = fields.Float(string='VAT amount cash discount #3')
    cash_discount_vat_rate_4 = fields.Float(string='cash discount ex-VAT (VAT rate #4)')
    cash_discount_vat_amount_4 = fields.Float(string='VAT amount cash discount #4')
    total_cash_discount = fields.Float(string='total cash discount ex VAT')
    total_cash_vat_discount = fields.Float(string='total cash VAT discount')
    cash_discount_expiry_date = fields.Char(string='Cash discount expiry date')
    ic_input = fields.Float(string='IC_Input')
    ic_output = fields.Float(string='IC_Output')

    # SINV Fields
    purchase_invoice_no = fields.Char(string='purchase invoice No.')
    customer_number = fields.Integer(string='customer number')
    customer_name = fields.Char(string='Customer Name')
    customer_vat_id = fields.Char(string='Customer VAT-ID')
    customer_group = fields.Char(string='Customer Group')
    remark = fields.Char(string='Remark')
    inv_vat_rate_1 = fields.Float(string='inv amount ex-VAT (VAT-rate #1)', tracking=True)
    inv_vat_rate_2 = fields.Float(string='inv amount ex-VAT (VAT-rate #2)', tracking=True)
    inv_vat_rate_3 = fields.Float(string='inv amount ex-VAT (VAT-rate #3)', tracking=True)
    inv_vat_rate_4 = fields.Float(string='inv amount ex-VAT (VAT-rate #4)', tracking=True)
    total_vat_amount = fields.Float(string='total VAT amount', tracking=True)
    document_total_ex_vat = fields.Float(string='document total ex-VAT', tracking=True)
    document_total_inc_vat = fields.Float(string='document total (including VAT)', tracking=True)

    cd_cash_discount_vat_rate_1 = fields.Float(string='CD_cash discount amount ex-VAT (VAT-rate #1)')
    cd_vat_amount_on_discount_1 = fields.Float(string='CD_VAT amount on discount #1')
    cd_cash_discount_vat_rate_2 = fields.Float(string='CD_cash discount amount ex-VAT (VAT-rate #2)')
    cd_vat_amount_on_discount_2 = fields.Float(string='CD_VAT amount on discount #2')
    cd_cash_discount_vat_rate_3 = fields.Float(string='CD_cash discount amount ex-VAT (VAT-rate #3)')
    cd_vat_amount_on_discount_3 = fields.Float(string='CD_VAT amount on discount #3')
    cd_cash_discount_vat_rate_4 = fields.Float(string='CD_cash discount amount ex-VAT (VAT-rate #4)')
    cd_vat_amount_on_discount_4 = fields.Float(string='CD_VAT amount on discount #4')
    cd_total_vat_amount = fields.Float(string='CD_total VAT amount')
    cd_document_total_ex_vat = fields.Char(string='CD_document total ex-VAT')
    cd_document_total_inc_vat = fields.Char(string='CD_document total (including VAT)')
    cd_cash_discount_expiry_date = fields.Char(string='CD_Cash discount expiry date')

    import_config_id = fields.Many2one('import.config', string='Import Configuration', tracking=True)
    type = fields.Selection(related='import_config_id.type', string='Type', store=True)
    record_created = fields.Boolean('INV/Bill Created', tracking=True)
    sale_invoice_id = fields.Many2one('account.move', string='ACC Invoice ID', tracking=True)
    cn_invoice_id = fields.Many2one('account.move', string='ACC Invoice CN ID', tracking=True)
    purchase_invoice_id = fields.Many2one('account.move', string='ACC Bill ID', tracking=True)
    refund_invoice_id = fields.Many2one('account.move', string='ACC Bill CN ID', tracking=True)
    creation_error = fields.Text(string='Creation Error')

    state = fields.Selection([('todo','To Do'),
                              ('done','Converted'),
                              ('blocked','Blocked'),
                              ('cancel','Cancelled')], default='todo', index=True, readonly=True,
                              string='Status', copy=False,
                              help=" * 'To Do': is when it is imported\n"
                                   " * 'Done': when it is converted into a bill\n"
                                   " * 'Blocked': is when it occurs an issue (the info don't match the import configuration)", tracking=True)
    reason_for_blocking = fields.Text(string='Reason of Blocking', tracking=True)
    import_filename = fields.Char('Record Created From')
    duplicate_entry = fields.Boolean(String='Duplicate Entry')
    audit_region = fields.Char(string='Audit Region', compute='_compute_region', store=True)
    audit_label = fields.Char(string='Audit Label', tracking=True)
    audit_06_rate = fields.Char(string='Audit 06 Rate', compute='_compute_audit_06_rate', store=True)
    cashdiscount_rate = fields.Float(string='CD Rate', compute='_compute_discount_fields', store=True)
    cashdiscount_expiration = fields.Date(string='CD Expiration', compute='_compute_discount_fields', store=True)

    @api.depends('cash_discount_rate_percentage', 'cash_discount_expiry_date')
    def _compute_discount_fields(self):
    # Back in account.move, add 2 new field:
    # cashdiscount_rate ( Cash Discount )=  cash_discount_rate_percentage / 100 (divided by 100)
    # cashdiscount_expiration ( Cash Discount Limit ) =  cash_discount_expiry_date (transformed from char to date)
        for record in self:
            record.cashdiscount_rate = 0
            record.cashdiscount_expiration = False
            if record.cash_discount_rate_percentage:
                record.cashdiscount_rate = record.cash_discount_rate_percentage / 100
            if record.cash_discount_expiry_date:
                expiry_date = parse(record.cash_discount_expiry_date, dayfirst=False)
                expiry_date = datetime.strftime(expiry_date, DEFAULT_SERVER_DATE_FORMAT)
                record.cashdiscount_expiration = expiry_date

    @api.model 
    def server_action_compute_audit_06_rate(self):
        active_ids = self._context.get('active_ids')
        for record in self.browse(active_ids):
            audit_06_rate = ''
            if record.inv_vat_rate_1 or record.vat_rate_1:
                audit_06_rate = 'Rate 1'
            if record.inv_vat_rate_2 or record.vat_rate_2:
                if len(audit_06_rate) > 0:
                    audit_06_rate += '; Rate 2'
                else:
                    audit_06_rate = 'Rate 2'
            if record.inv_vat_rate_3 or record.vat_rate_3:
                if len(audit_06_rate) > 0:
                    audit_06_rate += '; Rate 3'
                else:
                    audit_06_rate = 'Rate 3'
            if record.inv_vat_rate_4 or record.vat_rate_4:
                if len(audit_06_rate) > 0:
                    audit_06_rate += '; Rate 4'
                else:
                    audit_06_rate = 'Rate 4'
            if len(audit_06_rate) == 0:
                audit_06_rate = 'NULL'
            record.audit_06_rate = audit_06_rate
        return True

    @api.depends('inv_vat_rate_1','inv_vat_rate_2','inv_vat_rate_3','inv_vat_rate_4','vat_rate_1','vat_rate_2','vat_rate_3','vat_rate_4')
    def _compute_audit_06_rate(self):
        for record in self:
            audit_06_rate = ''
            if record.inv_vat_rate_1 or record.vat_rate_1:
                audit_06_rate = 'Rate 1'
            if record.inv_vat_rate_2 or record.vat_rate_2:
                if len(audit_06_rate) > 0:
                    audit_06_rate += '; Rate 2'
                else:
                    audit_06_rate = 'Rate 2'
            if record.inv_vat_rate_3 or record.vat_rate_3:
                if len(audit_06_rate) > 0:
                    audit_06_rate += '; Rate 3'
                else:
                    audit_06_rate = 'Rate 3'
            if record.inv_vat_rate_4 or record.vat_rate_4:
                if len(audit_06_rate) > 0:
                    audit_06_rate += '; Rate 4'
                else:
                    audit_06_rate = 'Rate 4'
            if len(audit_06_rate) == 0:
                audit_06_rate = 'NULL'
            record.audit_06_rate = audit_06_rate
# We need for the 8 PURCHASE journals within FTP Data (4 purchase journal, 4 purchase credit note journal) --> See second picture
#
# Generate a new name based on the value of the following fied: Country, Book, Document Number, Document Date
#
# Here the name would be: BE21*PUR/BE02014269
# ---> YY of the Document Date & Country & "*" & Book "/" Document Number

            # date_invoice = rec.document_date
            # date_due = rec.expiry_date
            # fiscal_year = ''
            # if rec.document_date:
                # fiscal_year = rec.document_date.split('-')[0]
                # date_invoice = parse(date_invoice, dayfirst=False)
                # date_invoice = datetime.strftime(date_invoice, DEFAULT_SERVER_DATE_FORMAT)
            # if rec.expiry_date:
                # date_due = parse(date_due, dayfirst=False)
                # date_due = datetime.strftime(date_due, DEFAULT_SERVER_DATE_FORMAT)
            # document_name = fiscal_year + '-' + rec.document_number
    @api.depends('country')
    def _compute_region(self):
        """
        Return Germany when country in DE or ZL
        """
        for record in self:
            if record.country and record.country in ('DE','ZL'):
                record.audit_region = 'Germany'

    @api.depends('document_date')
    def _get_document_date(self):
        """
        Return date field from the char field
        """
        for record in self:
            if record.document_date:
                document_date = parse(record.document_date, dayfirst=False)
                record.document_date_date = datetime.strftime(document_date, DEFAULT_SERVER_DATE_FORMAT)

    def name_get(self):
        result = []
        for data in self:
            fiscal_year = ''
            if data.document_date:
                fiscal_year = data.document_date.split('-')[0][2:]
            name = data.country + fiscal_year + '*' + data.book + '|' + data.document_number
            result.append((data.id, name))
        return result

    def action_audit_label(self):
        ''' Open the audit label wizard to log audit action.
        :return: An action opening the audit action wizard.
        '''
        return {
            'name': _('Audit Remarks'),
            'res_model': 'audit.label',
            'view_mode': 'form',
            'context': {
                'active_model': 'ftp.data',
                'active_ids': self.ids,
            },
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    @api.model 
    def server_action_remarks_vendor_inv_no_update(self):
        """
        Use this server action to update all those invoices and bill for which vendor ref is with decimal points eg. 1765093.0
        Apply a filter payment ref contain .0 and run this server action from more dropdown.
        @ Year of PInvoiceDate: venice_pinvoiceaccyear
        @ Reference/Description: name
        @ Number with reference: number_ref
        @ INV Name: inv_name
        @ INV Year: venice_sinvoiceaccyear
        """
        active_ids = self._context.get('active_ids')
        for record in self.browse(active_ids):
            if record.remarks_vendor_inv_no and record.remarks_vendor_inv_no[-2:] == '.0':
                record.remarks_vendor_inv_no = record.remarks_vendor_inv_no[:-2]
        return True

    @api.model 
    def server_action_update_xls_ref(self):
        """
        Use this server action to update all those invoices and bill for which vendor ref is with decimal points eg. 1765093.0
        Apply a filter payment ref contain .0 and run this server action from more dropdown.
        @ Year of PInvoiceDate: venice_pinvoiceaccyear
        @ Reference/Description: name
        @ Number with reference: number_ref
        @ INV Name: inv_name
        @ INV Year: venice_sinvoiceaccyear
        """
        active_ids = self._context.get('active_ids')
        for record in self.browse(active_ids):
            record_with_file = self.search([('document_number','=',record.document_number),('import_filename','!=',False)])
            if record_with_file:
                record.import_filename = record_with_file[0].import_filename
        return True

    @api.model 
    def mark_duplicate(self):
        """
        """
        active_ids = self._context.get('active_ids')
        for record in self.browse(active_ids):
            record_with_file = self.search([('document_number','=',record.document_number),('import_config_id','=',record.import_config_id.id)])
            if len(record_with_file)>1:
                record.duplicate_entry = True
        return True

    @api.model 
    def reset_duplicate(self):
        """
        """
        active_ids = self._context.get('active_ids')
        for record in self.browse(active_ids):
            record.duplicate_entry = False
        return True

    @api.model
    def create(self, vals):
        if vals.get('country', False) and vals.get('book', False) and vals.get('document_type', False):
            document_type = vals['document_type'].replace(" ","")
            import_config_id = self.env['import.config'].search([('country','=',vals['country']),
                                                                 ('book','=',vals['book']),
                                                                 ('document_type','=',document_type)], limit=1)
            if not import_config_id:
                vals['import_config_id'] = False
                vals['state'] = 'blocked'
                vals['reason_for_blocking'] = "System can't find any matching configuration!"
            else:
                vals['state'] = 'todo'
                vals['import_config_id'] = import_config_id.id
        return super(FTPData, self).create(vals)

    def action_assign_config(self):
        records = self.filtered(lambda rec: rec.state != 'done')
        for rec in records:
            if not rec.country:
                rec.reason_for_blocking = 'Missing Country Data'
                rec.state = 'blocked'
            if not rec.book:
                rec.reason_for_blocking = 'Missing Book Data'
                rec.state = 'blocked'
            if not rec.document_type:
                rec.reason_for_blocking = 'Missing Document Type Data'
                rec.state = 'blocked'
            if rec.country and rec.book and rec.document_type:
                document_type = rec.document_type.replace(" ","")
                import_config_id = self.env['import.config'].search([('country','=',rec.country),
                                                                     ('book','=',rec.book),
                                                                     ('document_type','=',document_type)], limit=1)
                if not import_config_id:
                    rec.import_config_id = False
                    rec.state = 'blocked'
                    rec.reason_for_blocking = "System can't find any matching configuration!"
                else:
                    rec.state = 'todo'
                    rec.reason_for_blocking = ''
                    rec.import_config_id = import_config_id.id
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

    @api.model
    def generate_inv_bills_cron(self):
        for i in range(3):
            for record in self.search([('state', '=', 'todo')], limit=100):
                if record.import_config_id:
                    record.generate_inv_bills()

    def generate_inv_bills(self):
        # records = self.filtered(lambda rec: rec.state == 'todo' and rec.import_config_id)
        partner_pool = self.env['res.partner']
        invoice_pool = self.env['account.move']

        partner_ids = partner_pool.search([('active','=',True)])
        vendor_map = dict([(vendor.venice_supnum, vendor.id) for vendor in partner_ids])

        for rec in self:
            if rec.state != 'todo':
                # raise UserError(_('You can only generate Inv/Bills from todo records!'))
                rec.state = 'blocked'
                rec.reason_for_blocking = "You are trying to generate inv/bill from a record which is not in todo state!"
                continue
            if not rec.import_config_id:
                # raise UserError(_('Import configuration is not assigened to record!'))
                rec.state = 'blocked'
                rec.reason_for_blocking = "System can't find any matching configuration!"
                continue

            date_invoice = rec.document_date
            date_due = rec.expiry_date
            fiscal_year = ''
            if rec.document_date:
                fiscal_year = rec.document_date.split('-')[0]
                date_invoice = parse(date_invoice, dayfirst=False)
                date_invoice = datetime.strftime(date_invoice, DEFAULT_SERVER_DATE_FORMAT)
            if rec.expiry_date:
                date_due = parse(date_due, dayfirst=False)
                date_due = datetime.strftime(date_due, DEFAULT_SERVER_DATE_FORMAT)
            document_name = fiscal_year + '-' + rec.document_number
            journal_id = self.env['account.journal'].sudo().browse(rec.import_config_id.journal_id.id)
            if fiscal_year:
                fiscal_year_yy = fiscal_year[2:]
            invoice_origin = rec.country + fiscal_year_yy + '*' + rec.book + '|' + rec.document_number
            inv_vals = {
                'name': document_name,
                'journal_id': journal_id.id,
                'company_id': rec.import_config_id.company_id.id,
                'invoice_date': date_invoice,
                'invoice_date_due': date_due,
                'venice_sinvoiceaccyear': fiscal_year,
                'venice_porderdocnumber': rec.purchase_order_no,
                'venice_sorderdocnumber': rec.sales_order_no,
                'venice_docnum': rec.document_number,
                'import_wizard': True,
                'ftp_raw_data_id': rec.id,
                'invoice_origin': invoice_origin
            }
            if rec.import_config_id.type == 'PUR':
                product1_price_unit = rec.vat_rate_1
                product2_price_unit = rec.vat_rate_2
                product3_price_unit = rec.vat_rate_3
                product4_price_unit = rec.vat_rate_4
                inv_vals['ref'] = rec.remarks_vendor_inv_no
                inv_vals['payment_reference'] = rec.remarks_vendor_inv_no
                inv_vals['venice_suppname'] = rec.supplier_name
                inv_vals['venice_pinvremark'] = rec.remarks_vendor_inv_no

                vendornumber = str(int(rec.supplier_number))
                if vendornumber != '0':
                    if vendornumber not in vendor_map:
                        # raise UserError(_('No vendor found with SupNum  %s.') % (vendornumber))
                        rec.state = 'blocked'
                        rec.reason_for_blocking = (_('No vendor found with SupNum  %s.') % (vendornumber))
                        continue
                    else:
                        vendor_map[vendornumber] = partner_pool.search([('venice_supnum','=',vendornumber)]).id
                    inv_vals['partner_id'] = vendor_map[vendornumber]
                    inv_vals['venice_suppnum'] = vendornumber

                # if rec.supplier_number != '0':
        # #             DS006/BE
                    # if len(rec.supplier_number) < 3:
                        # prefix = 3 - len(rec.supplier_number)
                        # if prefix == 1:
                            # add = '0'
                        # else:
                            # add = '00'
                        # rec.supplier_number = add+rec.supplier_number

                supplier_invoice_line_data = []

                if product1_price_unit != 0 and rec.import_config_id.product_id_1:
                    supplier_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_1.id,
                                                    'account_id': rec.import_config_id.product_id_1.property_account_expense_id.id,
                                                    'price_unit': product1_price_unit,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_1.supplier_taxes_id.ids)],
                                                        }))

                if product2_price_unit != 0 and rec.import_config_id.product_id_2:
                    supplier_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_2.id,
                                                    'account_id': rec.import_config_id.product_id_2.property_account_expense_id.id,
                                                    'price_unit': product2_price_unit,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_2.supplier_taxes_id.ids)],
                                                        }))

                if product3_price_unit != 0 and rec.import_config_id.product_id_3:
                    supplier_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_3.id,
                                                    'account_id': rec.import_config_id.product_id_3.property_account_expense_id.id,
                                                    'price_unit': product3_price_unit,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_3.supplier_taxes_id.ids)],
                                                        }))

                if product4_price_unit != 0 and rec.import_config_id.product_id_4:
                    supplier_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_4.id,
                                                    'account_id': rec.import_config_id.product_id_4.property_account_expense_id.id,
                                                    'price_unit': product4_price_unit,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_4.supplier_taxes_id.ids)],
                                                        }))

                if product1_price_unit == 0 and product2_price_unit == 0 and product3_price_unit == 0 and product4_price_unit == 0 and rec.import_config_id.product_id_0:
                    supplier_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_0.id,
                                                    'account_id': rec.import_config_id.product_id_0.property_account_expense_id.id,
                                                    'price_unit': 0,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_0.supplier_taxes_id.ids)],
                                                        }))

                # if rec.book == 'PUR':
                if rec.import_config_id.document_type == 'invoice':
                    inv_vals['move_type'] = 'in_invoice'
                    inv_vals['invoice_line_ids'] = supplier_invoice_line_data
                    bill_id = invoice_pool.search([('name','=',document_name),('move_type','=','in_invoice'),('state','in',('draft','imported'))])
                    # _logger.warning( "partner_id '%s' and partner name '%s'.", bill_data['partner_id'], bill_data['venice_suppname'])
                    if bill_id:
                        bill_id.sudo().write(inv_vals)
                    else:
                        bill_id = invoice_pool.sudo().create(inv_vals)
                        rec.purchase_invoice_id = bill_id.id

                # if rec.book == 'PCN':
                if rec.import_config_id.document_type == 'creditnote':
                    inv_vals['move_type'] = 'in_refund'
                    inv_vals['invoice_line_ids'] = supplier_invoice_line_data
                    bill_id = invoice_pool.search([('name','=',document_name),('move_type','=','in_refund'),('state','in',('draft','imported'))])
                    if bill_id:
                        bill_id.sudo().write(inv_vals)
                    else:
                        bill_id = invoice_pool.sudo().create(inv_vals)
                        rec.refund_invoice_id = bill_id.id

            if rec.import_config_id.type == 'SLS':
                inv_vals['ref'] = document_name
                inv_vals['payment_reference'] = rec.remark
                inv_vals['venice_customername'] = rec.customer_name
                inv_vals['venice_pinvremark'] = rec.remark
                inv_vals['venice_pinvoicedocnum'] = rec.purchase_invoice_no
                product1_price_unit = rec.inv_vat_rate_1
                product2_price_unit = rec.inv_vat_rate_2
                product3_price_unit = rec.inv_vat_rate_3
                product4_price_unit = rec.inv_vat_rate_4

                venice_system = False
                if rec.country == 'BE':
                    venice_system = 'Belgium'
                    customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == 'Belgium'])
                elif rec.country == 'NL':
                    venice_system = 'Netherlands'
                    customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == 'Netherlands'])
                else:
                    customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == False])
                customernumber = str(int(rec.customer_number))
                if customernumber not in customer_map:
                    if customernumber and customernumber != '0' and customernumber not in customer_map:
                        customer_id = partner_pool.create({'name': rec.customer_name,
                                                           'venice_nummer' : customernumber,
                                                           'sinv_creation' : True,
                                                           'sdt_section' : 'distrismart',
                                                           'venice_system': venice_system,
                                                           # 'vat': rec.customer_vat_id,
                                                            })
                        customer_map[customernumber] = customer_id.id
                        partner_ids |= customer_id
                else:
                    if venice_system:
                        customer_map[customernumber] = partner_pool.search([('venice_nummer','=',customernumber), ('venice_system','=',venice_system)]).id
                    else:
                        customer_map[customernumber] = partner_pool.search([('venice_nummer','=',customernumber), ('venice_system','=',False)]).id
                inv_vals['partner_id'] = customer_map[customernumber]
                inv_vals['venice_customernumber'] = customernumber

                customer_invoice_line_data = []
                if product1_price_unit != 0 and rec.import_config_id.product_id_1:
                    customer_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_1.id,
                                                    'account_id': rec.import_config_id.product_id_1.property_account_income_id.id,
                                                    'price_unit': product1_price_unit,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_1.taxes_id.ids)],
                                                        }))

                if product2_price_unit != 0 and rec.import_config_id.product_id_2:
                    customer_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_2.id,
                                                    'account_id': rec.import_config_id.product_id_2.property_account_income_id.id,
                                                    'price_unit': product2_price_unit,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_2.taxes_id.ids)],
                                                        }))
                if product3_price_unit != 0 and rec.import_config_id.product_id_3:
                    customer_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_3.id,
                                                    'account_id': rec.import_config_id.product_id_3.property_account_income_id.id,
                                                    'price_unit': product3_price_unit,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_3.taxes_id.ids)],
                                                        }))

                if product4_price_unit != 0 and rec.import_config_id.product_id_4:
                    customer_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_4.id,
                                                    'account_id': rec.import_config_id.product_id_4.property_account_income_id.id,
                                                    'price_unit': product4_price_unit,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_4.taxes_id.ids)],
                                                        }))

                if product1_price_unit == 0 and product2_price_unit == 0 and product3_price_unit == 0 and product4_price_unit == 0 and rec.import_config_id.product_id_0:
                    customer_invoice_line_data.append((0,0, {
                                                    'quantity': 1,
                                                    'product_id': rec.import_config_id.product_id_0.id,
                                                    'account_id': rec.import_config_id.product_id_0.property_account_income_id.id,
                                                    'price_unit': 0,
                                                    'tax_ids': [(6, 0, rec.import_config_id.product_id_0.taxes_id.ids)],
                                                        }))

                # if rec.book in ('SLS','MA','AMZ','SCMP','KFL'):
                if rec.import_config_id.document_type == 'invoice':
                    inv_vals['move_type'] = 'out_invoice'
                    inv_vals['invoice_line_ids'] = customer_invoice_line_data
                    invoice_id = invoice_pool.search([('name','=',document_name),('move_type','=','out_invoice'),('state','in',('draft','imported'))])
                    if invoice_id:
                        invoice_id.sudo().write(inv_vals)
                    else:
                        invoice_id = invoice_pool.sudo().create(inv_vals)
                        rec.sale_invoice_id = invoice_id.id

                # if rec.book in ('SCN','MACN','AMZCN','SCNCMP','KFLCN'):
                if rec.import_config_id.document_type == 'creditnote':
                    inv_vals['move_type'] = 'out_refund'
                    inv_vals['invoice_line_ids'] = customer_invoice_line_data
                    invoice_id = invoice_pool.search([('name','=',document_name),('move_type','=','out_refund'),('state','in',('draft','imported'))])
                    if invoice_id:
                        invoice_id.sudo().write(inv_vals)
                    else:
                        invoice_id = invoice_pool.sudo().create(inv_vals)
                        rec.cn_invoice_id = invoice_id.id

            rec.state = 'done'
        return True

    @api.model 
    def server_action_link_raw_data(self):
        """
        Use this server action to update all those invoices and bill for which name is missing year
        Apply a filter INV Year = 0 or Reference/Description contains 0- from odoo interface to filter such records.
        @ Year of PInvoiceDate: venice_pinvoiceaccyear
        @ Reference/Description: name
        @ Number with reference: number_ref
        @ INV Name: inv_name
        @ INV Year: venice_sinvoiceaccyear
        """
        active_ids = self._context.get('active_ids')
        for record in self.browse(active_ids):
    # sale_invoice_id = fields.Many2one('account.invoice', string='Sales Invoice ID')
    # cn_invoice_id = fields.Many2one('account.invoice', string='Credit Note ID')
    # purchase_invoice_id = fields.Many2one('account.invoice', string='Purchase Invoice ID')
    # refund_invoice_id = fields.Many2one('account.invoice', string='Refund ID')
            fiscal_year = ''
            if record.document_date:
                fiscal_year = record.document_date.split('-')[0]

            if record.sale_invoice_id:
                record.sale_invoice_id.ftp_raw_data_id = record.id

                record.sale_invoice_id.venice_sinvoiceaccyear = fiscal_year
                record.sale_invoice_id.venice_porderdocnumber = record.purchase_order_no
                record.sale_invoice_id.venice_sorderdocnumber = record.sales_order_no
                record.sale_invoice_id.venice_docnum = record.document_number
                record.sale_invoice_id.import_wizard = True
    
                if record.import_config_id.type == 'PUR':
                    record.sale_invoice_id.venice_suppname = record.supplier_name
                    record.sale_invoice_id.venice_pinvremark = record.remarks_vendor_inv_no
    
                if record.import_config_id.type == 'SLS':
                    record.sale_invoice_id.venice_customername = record.customer_name
                    record.sale_invoice_id.venice_pinvremark = record.remark
                    record.sale_invoice_id.venice_pinvoicedocnum = record.purchase_invoice_no


            if record.cn_invoice_id:
                record.cn_invoice_id.ftp_raw_data_id = record.id

                record.cn_invoice_id.venice_sinvoiceaccyear = fiscal_year
                record.cn_invoice_id.venice_porderdocnumber = record.purchase_order_no
                record.cn_invoice_id.venice_sorderdocnumber = record.sales_order_no
                record.cn_invoice_id.venice_docnum = record.document_number
                record.cn_invoice_id.import_wizard = True
    
                if record.import_config_id.type == 'PUR':
                    record.cn_invoice_id.venice_suppname = record.supplier_name
                    record.cn_invoice_id.venice_pinvremark = record.remarks_vendor_inv_no
    
                if record.import_config_id.type == 'SLS':
                    record.cn_invoice_id.venice_customername = record.customer_name
                    record.cn_invoice_id.venice_pinvremark = record.remark
                    record.cn_invoice_id.venice_pinvoicedocnum = record.purchase_invoice_no

            if record.purchase_invoice_id:
                record.purchase_invoice_id.ftp_raw_data_id = record.id

                record.purchase_invoice_id.venice_sinvoiceaccyear = fiscal_year
                record.purchase_invoice_id.venice_porderdocnumber = record.purchase_order_no
                record.purchase_invoice_id.venice_sorderdocnumber = record.sales_order_no
                record.purchase_invoice_id.venice_docnum = record.document_number
                record.purchase_invoice_id.import_wizard = True
    
                if record.import_config_id.type == 'PUR':
                    record.purchase_invoice_id.venice_suppname = record.supplier_name
                    record.purchase_invoice_id.venice_pinvremark = record.remarks_vendor_inv_no
                    record.purchase_invoice_id.ref = record.remarks_vendor_inv_no
                    record.purchase_invoice_id.payment_reference = record.remarks_vendor_inv_no
    
                if record.import_config_id.type == 'SLS':
                    record.purchase_invoice_id.venice_customername = record.customer_name
                    record.purchase_invoice_id.venice_pinvremark = record.remark
                    record.purchase_invoice_id.venice_pinvoicedocnum = record.purchase_invoice_no

            if record.refund_invoice_id:
                record.refund_invoice_id.ftp_raw_data_id = record.id

                record.refund_invoice_id.venice_sinvoiceaccyear = fiscal_year
                record.refund_invoice_id.venice_porderdocnumber = record.purchase_order_no
                record.refund_invoice_id.venice_sorderdocnumber = record.sales_order_no
                record.refund_invoice_id.venice_docnum = record.document_number
                record.refund_invoice_id.import_wizard = True
    
                if record.import_config_id.type == 'PUR':
                    record.refund_invoice_id.venice_suppname = record.supplier_name
                    record.refund_invoice_id.venice_pinvremark = record.remarks_vendor_inv_no
                    record.purchase_invoice_id.ref = record.remarks_vendor_inv_no
                    record.purchase_invoice_id.payment_reference = record.remarks_vendor_inv_no
    
                if record.import_config_id.type == 'SLS':
                    record.refund_invoice_id.venice_customername = record.customer_name
                    record.refund_invoice_id.venice_pinvremark = record.remark
                    record.refund_invoice_id.venice_pinvoicedocnum = record.purchase_invoice_no

        return True
