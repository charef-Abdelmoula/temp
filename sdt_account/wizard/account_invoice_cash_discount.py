# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError


class AccountInvoiceCashDiscount(models.TransientModel):
    """
    This wizard will allows to select a value for 2 fields:

- BILL Type

- VAT Periode

In the list view select invoices in draft, and can use the action in order to set up the value.
    """

    _name = "account.invoice.cash.discount"
    _description = "Update selected Invoices"

    cash_discount =  fields.Float(string='Cash Discount(%)', required=True)
    date = fields.Date(string='Payment Date')

    @api.multi
    def generate_credit_note(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        invoice_pool = self.env['account.invoice']
        invoice_line_pool = self.env['account.invoice.line']
        for invoice in invoice_pool.browse(active_ids):
            bill_data = {
                'type': 'in_refund',
                'refund_invoice_id': invoice.id,
                'journal_id': invoice.journal_id.id,
                'partner_id': invoice.partner_id.id,
                'company_id': invoice.company_id.id,
                'date': self.date,
                'date_invoice' : self.date,
                'date_due' : self.date,
                'reference': invoice.reference,
                'origin': invoice.number,
                'venice_suppname': invoice.venice_suppname,
                'name': 'Cash Discount'
            }
            bill_id = invoice_pool.create(bill_data)
            message = _("This vendor bill credit note has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a><br>Reason: %s") % (invoice.id, invoice.number, invoice.name)
            bill_id.message_post(body=message)
            for line in invoice.invoice_line_ids:
                product = False
                for tax in line.invoice_line_tax_ids:
                    product = tax.discount_product_id and tax.discount_product_id.id or False
                supplier_invoice_line_data = {
                    'product_id': product,
                    'quantity': line.quantity,
                    'price_unit': line.price_unit - (line.price_unit * (1 - (self.cash_discount or 0.0) / 100.0)),
#                     'price_unit': line.price_unit * (1 - (self.cash_discount or 0.0) / 100.0),
                    'invoice_id': bill_id.id,
#                     'account_id': invoice.journal_id.default_credit_account_id.id,
                    'account_id': line.account_id.id,
                    'name': 'import'
                }
                supplier_invoice_line = invoice_line_pool.create(supplier_invoice_line_data)
                supplier_invoice_line._onchange_product_id()
                supplier_invoice_line.account_id = line.account_id.id


            action = self.env.ref('account.action_invoice_tree1').read()[0]
            action['views'] = [(self.env.ref('account.invoice_supplier_form').id, 'form')]
            action['res_id'] = bill_id.id
            return action

        return {'type': 'ir.actions.act_window_close'}
