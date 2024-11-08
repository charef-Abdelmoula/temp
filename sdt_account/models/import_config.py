# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class TaxJuridiction(models.Model):
    _name= 'tax.juridiction'
    _description = 'Tax Juridiction'

    name = fields.Char('Name', required=True)
    active = fields.Boolean('Active', default=True)

class ImportConfig(models.Model):
    _name = 'import.config'
    _description = 'Pinvoice and SInvoice Configuration'

    @api.depends('country', 'book', 'type', 'document_type', 'journal_id')
    def _compute_name(self):
        for record in self:
            name = ''
            if record.country:
                name = record.country
            if record.type:
                name += '-' + record.type
            if record.book:
                name += ' (' + record.book +')'
            if record.document_type:
                name += '-' + record.document_type
            if record.journal_id:
                name += '-' + record.journal_id.name
            record.name = name

    name = fields.Char(compute='_compute_name', store=True)
    country = fields.Selection([('DE','DE'),
                                ('BE','BE'),
                                ('NL','NL'),
                                ('ZL','ZL'),
                                ('AT','AT'),
                                ('FR','FR')], string='Country', required=True)
    book = fields.Char(string='Book', required=True)
    type = fields.Selection([('SLS','SLS'),
                             ('PUR','PUR')], string='Type', required=True)
    document_type = fields.Selection([('invoice','Invoice'),
                                      ('creditnote','CreditNote')], string='Document Type', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    product_id_1 = fields.Many2one('product.product', string='Product1')
    product_id_2 = fields.Many2one('product.product', string='Product2')
    product_id_3 = fields.Many2one('product.product', string='Product3')
    product_id_4 = fields.Many2one('product.product', string='Product4')
    product_id_0 = fields.Many2one('product.product', string='Product for 0 price', help='Product to consider when All Prices are zero')
    journal_id = fields.Many2one('account.journal', string='Journal')
    active = fields.Boolean('Active', default=True)

class ImportConfigAmazon(models.Model):
    _name = 'import.config.amazon'
    _description = 'Pinvoice and SInvoice Configuration for Amazon Payments'

    @api.depends('customer_partner', 'document_type')
    def _compute_name(self):
# Please update the name to: Customer Partner - Document Type
#
# Ex/ Amazon DE * DE/AT (IC) - Credit Note
        for record in self:
            name = ''
            tax_type = ''
            if record.customer_partner:
                name = record.customer_partner.name
            if record.document_type:
                name += ' - ' + record.document_type
            if record.tax_type:
                if record.tax_type == 'intra_community':
                    tax_type = ' (Intra-Community)'
                elif record.tax_type == 'full':
                    tax_type = ' (Full)'
                elif record.tax_type == 'reduced':
                    tax_type = ' (Reduced)'
                else:# record.tax_type == 'intermediate':
                    tax_type = ' (Intermediate)'
                name += tax_type
            record.name = name

    name = fields.Char(compute='_compute_name', store=False)
    country = fields.Selection([('DE','DE'),
                                ('AT','AT')], string='Marketplace', required=True)
    # book = fields.Char(string='Book', required=True)
    type = fields.Selection([('SELLER','SELLER')], string='Type', default='SELLER', readonly=True)
    document_type = fields.Selection([('invoice','Invoice'),
                                      ('creditnote','CreditNote')], string='Document Type', required=True)
    transaction_type = fields.Selection([('shipment','Shipment'),
                                         ('refund','Refund')], string='Transation Type', required=True)
    company_id = fields.Many2one('res.company', string='Company', required=True)
    journal_id = fields.Many2one('account.journal', string='Journal')
    active = fields.Boolean('Active', default=True)

    product_shipping_id = fields.Many2one('product.product', string='Shipping Product')
    shipping_tax_rate = fields.Float(string='Shipping Tax Rate', tracking=True)

    # seller_tax_registration_jurisdiction = fields.Char(string="Seller Tax Registration Jurisdiction", tracking=True)
    # buyer_tax_registration_jurisdiction = fields.Char(string="Buyer Tax Registration Jurisdiction", tracking=True)
    seller_tax_registration_jurisdiction = fields.Many2one('tax.juridiction', string="Seller Tax Registration Jurisdiction", tracking=True)
    buyer_tax_registration_jurisdiction = fields.Many2one('tax.juridiction', string="Buyer Tax Registration Jurisdiction", tracking=True)

    fiscal_position = fields.Selection([('Final Customer','Final Customer'),
                                        ('b2b','B2B'),
                                        ('intra_community','Intra-Community'),], string='Fiscal Position')
    customer_partner = fields.Many2one('res.partner', string='Customer Partner', required=True)
    payment_term_id = fields.Many2one('account.payment.term', related='customer_partner.property_payment_term_id', string='Payment Term')
    tax_type = fields.Selection([('intra_community','Intra-Community'),
                                 ('full','Full'),
                                 ('reduced','Reduced'),
                                 ('intermediate','Intermediate')], string='Tax Type')
    tax_rate = fields.Float(string='Tax Rate', tracking=True)
    general_product_id = fields.Many2one('product.product', string='Generic Product')
    giftwrap_product_id = fields.Many2one('product.product', string='Giftwrap Product')
    giftwrap_tax_rate = fields.Float(string='Giftwrap Tax Rate', tracking=True)

    product_id_1 = fields.Many2one('product.product', string='Product1')
    product_id_2 = fields.Many2one('product.product', string='Product2')
    product_id_3 = fields.Many2one('product.product', string='Product3')
    product_id_4 = fields.Many2one('product.product', string='Product4')
    product_id_0 = fields.Many2one('product.product', string='Product for 0 price', help='Product to consider when All Prices are zero')
    
    product_tax_code = fields.Char(string='Product Tax Code', tracking=True)
    jurisdiction_name = fields.Char(string='Jurisdiction Name', tracking=True)
    product_tax_code = fields.Boolean(string='Product Tax Code')

    amazon_config_tax_code_lines = fields.One2many('amazon.config.tax.code', 'import_config_amazon_id', string='Tax Code Lines')


class AmazonConfigTaxCode(models.Model):
    _name = 'amazon.config.tax.code'
    _description = 'Amazon Config Tax Codes'

    product_tax_code = fields.Char(string='Product Tax code', required=True)
    product_id = fields.Many2one('product.product', string='Generic Product')
    import_config_amazon_id = fields.Many2one('import.config.amazon', string='Amazon Config')
