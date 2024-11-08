# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class GenerateInvBill(models.TransientModel):
    _name = 'generate.inv.bill'
    _description = 'Generate Invoice Bills'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    country = fields.Char(string='Country', compute='_get_country')
    import_warning = fields.Text('Import Summary', readonly='1')

    @api.depends('company_id')
    def _get_country(self):
        """
        Return country as DE, BE, AT, ZL, FR
        """
        for record in self:
            if record.company_id:
                record.country = record.company_id.name[:2]

    def generate_inv_bills(self):
        count = 0
        countries = [self.country]
        if self.country == 'DE':
            countries = ['DE','ZL']
        # for record in self.env['ftp.data'].search([('state', '=', 'todo'),('country','=', self.country)]):
        for record in self.env['ftp.data'].search([('state', '=', 'todo'),('country','in', countries)]):
            if record.import_config_id:
                count += 1
                record.generate_inv_bills()
        Warning_msg = ("Total records processed: %s")%(count)
        import_id = self.env['generate.inv.bill'].create({'import_warning': Warning_msg})

        return {
            'name': 'Inv/Bills Generation Summary',
            'view_mode': 'form',
            'res_id': import_id.id,
            'res_model': 'generate.inv.bill',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
