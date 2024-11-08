# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError


class AccountInvoiceSetValues(models.TransientModel):
    """
    This wizard will allows to select a value for 2 fields:

- BILL Type

- VAT Periode

In the list view select invoices in draft, and can use the action in order to set up the value.
    """

    _name = "account.invoice.set.values"
    _description = "Update selected Invoices"

    vat_period_id =  fields.Many2one('vat.period', string='VAT Period', domain=[('active','=',True)], copy=False)
    bill_type = fields.Selection([
            ('ic_acquisitions','IC Acquisitions'),
            ('purchased_services_eu','Purchased Services EU'),
            ('input_vat', 'Input VAT'),
            ('import_vat', 'Import VAT'),
        ], string='BILL Type')
#     period_id = fields.Many2one('invoice.periode', string='Periode on Invoice Lines')

    @api.multi
    def update_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            if record.state not in ('draft','imported','open'):
                raise UserError(_("Selected invoice(s) cannot be updated as they are not in 'Draft','Imported' or 'Open' state."))
            if self.vat_period_id:
                record.vat_period_id = self.vat_period_id
            if self.bill_type:
                record.bill_type = self.bill_type
        return {'type': 'ir.actions.act_window_close'}

class AccountInvoiceSetImported(models.TransientModel):
    """
    This wizard will allows to select a value for fields:

- Imported Through Wizard

    """

    _name = "account.invoice.set.imported"
    _description = "Update selected Invoices"

    import_wizard = fields.Boolean('Imported Through Wizard')

    @api.multi
    def update_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            record.import_wizard = self.import_wizard
        return {'type': 'ir.actions.act_window_close'}
