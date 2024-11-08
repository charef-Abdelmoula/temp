# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    sdt_global = fields.Boolean('Global Journal')
    sdt_papersmart = fields.Boolean('PaperSmart Journal')
    sdt_distrismart = fields.Boolean('DistriSmart Journal')
    department_id = fields.Many2one('invoice.department', string='Department')
    hr_id = fields.Many2one('invoice.hr', string='HR')
    journal_partner_id = fields.Many2one('res.partner', string='Journal Partner')
    single_partner = fields.Boolean(string='Is Single Partner Journal')

    update_market_partner = fields.Boolean(string='Update Market Partner')
    update_audit_status = fields.Boolean(string='Update Audit Status')

    @api.model
    def _get_sequence_prefix(self, code, refund=False):
        prefix = code.upper()
        if refund:
            prefix = 'R' + prefix
        return prefix + '/%(range_y)s(%(month)s)'
