# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError


class AccountBankStatementPartner(models.TransientModel):
    """
    This wizard will match partner based on partner name fetched from bank statement import:
    """

    _name = "account.bank.statement.partner"
    _description = "Update Bank Statement Lines"

    matching_id = fields.Many2one('partner.matching', string='Matching Set', required=True)

    @api.multi
    def update_lines(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.bank.statement'].browse(active_ids):
            for line in record.line_ids:
                if line.partner_name:
                    partner_matching_line = self.env['partner.matching.line'].search([('matching_id','=', self.matching_id.id),('partner_name','=',line.partner_name)])
                    if partner_matching_line:
                        line.partner_id = partner_matching_line.partner_id.id
        return {'type': 'ir.actions.act_window_close'}

