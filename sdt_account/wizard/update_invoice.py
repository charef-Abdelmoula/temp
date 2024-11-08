# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class UpdateInvoiceKanbanState(models.TransientModel):
    _name = 'update.invoice.kanban.state'
    _description = 'Generate Invoice Bills'

    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Kanban State',
        copy=False, default='normal', required=True)

    def update_kanban_state(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.move'].browse(active_ids):
            record.kanban_state = self.kanban_state
        return {'type': 'ir.actions.act_window_close'}

class SetPaymentType(models.TransientModel):
    """
    This wizard allow to update payment type on account move.
    The action set:
    - ppc_paymenttype
    - payment_reference
    - ppc_paymenttype get its value from what we manually write
    - payment_reference get it's value by combining the value of the field "ref" and addint the new value of "ppc_paymenttype"
    """

    _name = "set.payment.type"
    _description = "Set Payment Type on move"

    payment_type = fields.Char('Payment Type', required=True)

    def update_payment_type(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['account.move'].browse(active_ids):
            record.write({'ppc_paymenttype': self.payment_type,
                          'payment_reference': record.ref + '('+self.payment_type+')'})
        return {'type': 'ir.actions.act_window_close'}

class ManualAuditStatus(models.TransientModel):
    """
    This wizard will change the Audit Status to “Manually Audited” only if the state is “To check" or "Audited”
    The action set:
    - audit_status
    """

    _name = "manual.audit.status"
    _description = "Update Audit Status to Manually Updated"


    def update_audit_status(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['account.move'].browse(active_ids):
            if record.audit_status in ['audited','to_check']:
                record.write({'audit_status': 'manually_audited'})
        return {'type': 'ir.actions.act_window_close'}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
