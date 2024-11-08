# -*- coding: utf-8 -*-
from odoo import models, api, fields, _

class UpdateRecordCreatedFrom(models.TransientModel):
    """
    This wizard allow to add record created from on market amazon records.
    """

    _name = "update.record.created.from"
    _description = "Remarks on market amazon"

    record_created_from = fields.Char('Record Created From', required=True)

    def update_record_created_from(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        for record in self.env['market.amazon'].browse(active_ids):
            record.write({'record_created_from': self.record_created_from})
        return {'type': 'ir.actions.act_window_close'}


