# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.depends('no_split', 'country_allocation')
    def _compute_amount(self):
        for record in self:
            if record.no_split==False:
                if record.country_allocation.allocation_de>0:
                    record.amount_de = record.amount * record.country_allocation.allocation_de / 100
                if record.country_allocation.allocation_be>0:
                    record.amount_be = record.amount * record.country_allocation.allocation_be / 100
                if record.country_allocation.allocation_nl>0:
                    record.amount_nl = record.amount * record.country_allocation.allocation_nl / 100
                if record.country_allocation.allocation_fr>0:
                    record.amount_fr = record.amount * record.country_allocation.allocation_fr / 100
            else:
                record.amount_de = 0.0
                record.amount_be = 0.0
                record.amount_nl = 0.0
                record.amount_fr = 0.0

    @api.depends('amount_de', 'amount_be', 'amount_nl', 'amount_fr')
    def _get_value(self):
        for record in self:
            record.de = False
            record.be = False
            record.nl = False
            record.fr = False
            if record.amount_de != 0.0:
                record.de = True
            if record.amount_be != 0.0:
                record.be = True
            if record.amount_nl != 0.0:
                record.nl = True
            if record.amount_fr != 0.0:
                record.fr = True

    department_id = fields.Many2one('invoice.department', string='Department')
    period_id = fields.Many2one('invoice.periode', string='Periode')
    hr_id = fields.Many2one('invoice.hr', string='HR')
    no_split = fields.Boolean('No Split', help="Tick this field if you don't want to split amount based on country allocation" )
    country_allocation = fields.Many2one('country.allocation', string='Country Allocation')

    amount_de = fields.Monetary(compute='_compute_amount', string='DE Amount', store=True, readonly=True)
    amount_be = fields.Monetary(compute='_compute_amount', string='BE Amount', store=True, readonly=True)
    amount_nl = fields.Monetary(compute='_compute_amount', string='NL Amount', store=True, readonly=True)
    amount_fr = fields.Monetary(compute='_compute_amount', string='FR Amount', store=True, readonly=True)

    de = fields.Boolean(compute='_get_value', string='DE Account', store=True, readonly=True)
    be = fields.Boolean(compute='_get_value', string='BE Account', store=True, readonly=True)
    nl = fields.Boolean(compute='_get_value', string='NL Account', store=True, readonly=True)
    fr = fields.Boolean(compute='_get_value', string='FR Account', store=True, readonly=True)

    analytic_client = fields.Char('Analytic Client')
    journal_id = fields.Many2one('account.journal', related='move_id.journal_id', string='Journal', store=True, readonly=True)

    @api.model 
    def server_action_update_analytic_client(self):
        active_ids = self._context.get('active_ids')
        for analytic_line in self.browse(active_ids):
            if analytic_line.analytic_client == False:
                analytic_line.analytic_client = analytic_line.sudo().move_id and analytic_line.sudo().move_id.invl_id and analytic_line.sudo().move_id.invl_id.analytic_client or '' 
        return True

class AccountAnalyticTagCategory(models.Model):
    _name = 'account.analytic.tag.category'
    _description = 'Account Analytic Tag Category'

    name = fields.Char(string='Category Name', index=True, required=True)

class AccountAnalyticTag(models.Model):
    _inherit = 'account.analytic.tag'

    category_id = fields.Many2one('account.analytic.tag.category', string='Category')

