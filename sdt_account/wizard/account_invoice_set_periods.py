# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError


class AccountInvoiceSetPeriods(models.TransientModel):
    """
    This wizard will allows to select a value for Periods of Invoice Lines:
    """

    _name = "account.invoice.set.periods"
    _description = "Update Periods on Invoice Lines"

    period_id = fields.Many2one('invoice.periode', string='Periode on Invoice Lines')
    date = fields.Date('Accounting Date')

    @api.multi
    def update_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            if self.period_id:
                for line in record.invoice_line_ids:
                    line.period_id = self.period_id
            if self.date:
                record.date = self.date
        return {'type': 'ir.actions.act_window_close'}

class AccountInvoiceSetVatDeclaration(models.TransientModel):
    """
    This wizard will allows to select a value for Periods of Invoice Lines:
    """

    _name = "account.invoice.set.vat.declaration"
    _description = "Update VAT Declaration on Invoices"

    vat_declaration = fields.Selection([('to_do','To Do'),
                                        ('done','Done'),
                                        ('issue','Issue')], string='VAT Declaration', default='to_do')

    @api.multi
    def update_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            if record.vat_period_id and record.vat_period_id.statement_issued:
                raise UserError(_("You are trying to change the status of a VAT Statement issued"))
            record.vat_declaration = self.vat_declaration
        return {'type': 'ir.actions.act_window_close'}
