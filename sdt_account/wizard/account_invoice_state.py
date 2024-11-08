# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from odoo.exceptions import UserError


class AccountInvoiceCancel(models.TransientModel):
    """
    This wizard will cancel the all the selected invoices.
    If in the journal, the option allow cancelling entry is not selected then it will give warning message.
    """

    _name = "account.invoice.cancel"
    _description = "Cancel the Selected Invoices"

    reason_for_cancellation = fields.Char('Reason for Cancellation', required=True)

    @api.multi
    def invoice_cancel(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            if record.state in ('cancel'):
                raise UserError(_("Selected invoice(s) cannot be cancelled as they are already in 'Cancelled' or 'Done' state."))
            record.action_invoice_cancel()
            record.write({'reason_for_cancellation': self.reason_for_cancellation})
        return {'type': 'ir.actions.act_window_close'}


class AccountInvoiceDraft(models.TransientModel):
    """
    This wizard will set to draft the all the selected cancelled invoices.
    """

    _name = "account.invoice.draft"
    _description = "Set to Draft Selected Invoices"

    @api.multi
    def invoice_draft(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            record.action_invoice_draft()
        return {'type': 'ir.actions.act_window_close'}

class AccountInvoiceImportDraft(models.TransientModel):
    """
    This wizard will set to draft the all the selected cancelled invoices.
    """

    _name = "account.invoice.import.draft"
    _description = "Set to Draft Selected Imported Invoices"

    @api.multi
    def invoice_draft(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            record.action_invoice_import_to_draft()
        return {'type': 'ir.actions.act_window_close'}
