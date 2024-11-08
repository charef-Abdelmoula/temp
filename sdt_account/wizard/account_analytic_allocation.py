# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError


class AccountAnalyticAllocation(models.TransientModel):
    """
    This wizard will allows to select a values for account analytic lines:
    """

    _name = "account.analytic.allocation"
    _description = "Update Country Allocation on Analytic Entries"

    no_split = fields.Boolean('No Split', help="Tick this field if you don't want to split amount based on country allocation" )
    country_allocation = fields.Many2one('country.allocation', string='Country Allocation')

    @api.multi
    def update_entries(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.analytic.line'].browse(active_ids):
            if self.no_split:
                record.no_split = self.no_split
            if self.country_allocation:
                record.country_allocation = self.country_allocation
        return {'type': 'ir.actions.act_window_close'}


