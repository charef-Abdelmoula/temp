# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.depends('distrismart', 'default_code')
    def _get_country_ref(self):
        for record in self:
            record.ds_ref_de = ''
            record.ds_ref_be = ''
            record.ds_ref_nl = ''
            record.ds_ref_fr = ''
            if record.distrismart:
                if record.default_code:
                    record.ds_ref_de = record.default_code + '/DE'
                    record.ds_ref_be = record.default_code + '/BE'
                    record.ds_ref_nl = record.default_code + '/NL'
                    record.ds_ref_fr = record.default_code + '/FR'

    @api.depends('account_analytic_id')
    def _is_analytic_product(self):
        for record in self:
            if record.account_analytic_id:
                record.analytic_product = True

    analytic_product = fields.Boolean('Analytic Product', compute='_is_analytic_product', help='Checked if analytic account is bind on product', store=True)
    account_analytic_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    distrismart = fields.Boolean('Distri Smart')
    ds_ref_de = fields.Char('DE Reference', compute='_get_country_ref', store=True)
    ds_ref_be = fields.Char('BE Reference', compute='_get_country_ref', store=True)
    ds_ref_nl = fields.Char('NL Reference', compute='_get_country_ref', store=True)
    ds_ref_fr = fields.Char('FR Reference', compute='_get_country_ref', store=True)
    ds_vendor = fields.One2many('res.partner', 'product_tmpl_id', string='DS Vendors', domain=[('distrismart_supplier', '=', True)])
    cashdiscount_account_id = fields.Many2one('account.account', string='CD Account')
    cashdiscount_account_label = fields.Char(string='CD Description')

# class ProductProduct(models.Model):
    # _inherit = "product.product"
    #
    # @api.model
    # def _convert_prepared_anglosaxon_line(self, line, partner):
        # res = super(ProductProduct, self)._convert_prepared_anglosaxon_line(line, partner)
        # res['invl_id'] = line.get('invl_id', False)
        # return res