# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class ResPartnerType(models.Model):
    _name= 'res.partner.type'
    _description = 'Res Partner Type'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    partner_type_id = fields.Many2one('res.partner.type', string='Partner Type', tracking=True)
    venice_supnum = fields.Char('SupNum')
    venice = fields.Boolean('Venice')
    venice_system = fields.Selection([('Germany','Germany'),
                                    ('Belgium','Belgium'),
                                    ('Netherlands','Netherlands')], 'Venice System')
    venice_nummer = fields.Char('Client Number')
    venice_subnummer = fields.Char('Client Sub Number')
    global_partner = fields.Boolean('Global Partner')
#    distrismart fields defined below are defined in view in sdt_vendors_process module due to view limitation
    distrismart_sync = fields.Boolean('DistriSmart Sync')
    distrismart_client = fields.Char('DistriSmart Customer')
    distrismart_supplier = fields.Boolean('Distrismart Vendor')
    bankstament_partner = fields.Boolean('Bank Statement Partner')
    bankstatement_checked = fields.Boolean('Bank Statement Checked')
    papersmart_sync = fields.Boolean('PaperSmart Sync')
    papersmart_supplier = fields.Boolean('PaperSmart Supplier')
    papersmart_client = fields.Boolean('PaperSmart Client')
    sinv_creation = fields.Boolean('SINV Creation')
    sinv_checked = fields.Boolean('SINV Checked')
    pinv_creation = fields.Boolean('PINV Creation')
    pinv_checked = fields.Boolean('PINV Checked')
    sdt_section = fields.Selection([('sdt','SDT'),
                                    ('distrismart','Distri Smart'),
                                    ('papersmart','Paper Smart')], 'SDT Section')
    ppc_user_imported = fields.Boolean('User Imported')
    ppv_vendor_imported = fields.Boolean('Vendor imported')
    ppc_created = fields.Char('PS Creation')
    ppc_updated = fields.Char('PS Update')
    ppc_lastsign = fields.Char('PS Last Sign In')
    ppc_name = fields.Char('PS Full name')
    ppc_vorname = fields.Char('PS Surname')
    ppc_nachname = fields.Char('PS First name')
    ppc_anrede = fields.Char('PS Title')
    ppc_email = fields.Char('PS Email')
    ppc_customernumber = fields.Integer('PS Customer Number')
    ppc_company = fields.Char('PS Customer Company')
    ppc_business = fields.Boolean('PS Is Business')
    ppc_customer = fields.Boolean('PS Is Private')
    ppc_bill_name = fields.Char('PS Name')
    ppc_bill_company = fields.Char('PS Company')
    ppc_bill_street = fields.Char('PS Street')
    ppc_bill_city = fields.Char('PS City')
    ppc_bill_zip = fields.Char('PS Zip')
    ppc_bill_country = fields.Char('PS Country')
    ppc_bill_phone = fields.Char('PS Phone')
    ppc_bill_registrationnumber = fields.Char('PS Registration Number')
    ppc_bill_taxnumber = fields.Char('PS Tax Number')
    ppc_tax_choice = fields.Char('PS Tax Choice')
    ppc_newsletter = fields.Boolean('PS Newsletter')
    ppc_lastshopping = fields.Char('PS Last Shopping')
    ppc_paymenttype = fields.Char('PS Payment Type')
    ppc_cc_digits = fields.Char('PS Credit Digitis')
    ppc_cc_expiry = fields.Char('PS Credit Expiry')
    ppc_cc_limit = fields.Char('PS Credit Limit')
    product_tmpl_id = fields.Many2one('product.template', 'Product Template')
    department_id = fields.Many2one('invoice.department', string='Department', copy=False)
    hr_id = fields.Many2one('invoice.hr', string='HR', copy=False)
    audit_vat_country = fields.Char('Audit VAT Country', copy=False)

    @api.model 
    def server_action_update_ppc_customernumber(self):
        active_ids = self._context.get('active_ids')
        for record in self.browse(active_ids):
            if int(record.venice_nummer) == record.ppc_customernumber:
                record.ppc_customernumber = 0
        return True

# Into Res.Partner
# Add a new field "sdt_section", it is a list field with 3 entries:
# - [sdt] Label: SDT
# - [distrismart] Label: Distri Smart
# - [papersmart] Label: Paper Smart
# 
# Add a new tab "PaperSmart":
# It is unhide only if "sdt_section" = [papersmart] (otherwhise it is hidden).
# Inside that Tab, create the following fields: