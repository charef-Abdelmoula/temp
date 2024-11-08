# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AccountPayment(models.Model):
    _inherit = "account.payment"

    cashdiscount_total = fields.Monetary(currency_field='currency_id', string='Total CD')
    cashdiscount_notes = fields.Char(string='Internal Notes')
    account_move = fields.Boolean(string='Account Move', default=False)

    # @api.model
    def server_action_link_payment_to_move(self):
        active_ids = self._context.get('active_ids')
        for payment in self.browse(active_ids):
            for invoice in payment.reconciled_invoice_ids:
                invoice.payment_id = payment.id
                payment.account_move = True
                invoice.payment_date = payment.date
            for bill in payment.reconciled_bill_ids:
                bill.payment_id = payment.id
                payment.account_move = True
                bill.payment_date = payment.date
            # for statement in payment.reconciled_statement_ids:
                # statement.payment_id = payment.id