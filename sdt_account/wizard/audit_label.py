# -*- coding: utf-8 -*-
from odoo import models, api, fields, _

class AuditLabel(models.TransientModel):
    """
    This wizard allow to add remarks on account move and ftd data about audit.
    """

    _name = "audit.label"
    _description = "Remarks on move and ftp data"

    audit_label = fields.Char('Audit Label', required=True)

    def update_audit_label(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        if self.env.context.get('active_model') == 'account.move':
            for record in self.env['account.move'].browse(active_ids):
                record.write({'audit_label': self.audit_label})
        if self.env.context.get('active_model') == 'ftp.data':
            for record in self.env['ftp.data'].browse(active_ids):
                record.write({'audit_label': self.audit_label})
        if self.env.context.get('active_model') == 'account.bank.statement.line':
            for record in self.env['account.bank.statement.line'].browse(active_ids):
                record.write({'transaction_type': self.audit_label})
        return {'type': 'ir.actions.act_window_close'}


