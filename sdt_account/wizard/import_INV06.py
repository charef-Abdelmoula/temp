# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import base64

import xlrd
from xlrd import open_workbook
from datetime import datetime
from dateutil.parser import parse

import logging

try:
    from itertools import imap
except ImportError:
    # Python 3...
    imap=map
# from boto.mashups import order

_logger = logging.getLogger(__name__)

class ImportInv06(models.TransientModel):
    _name = 'import.inv06'
    _description = 'Import INV06'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id, help="""
    * ZL = SDT.DE
    * DE = SDT.DE
    * BE = SDT.BE
    * NL = SDT.NL
    """)
    venice_system = fields.Selection([('Germany','Germany'),
                                      ('Belgium','Belgium'),
                                      ('Netherlands','Netherlands')], 'Venice System')
    product1_id = fields.Many2one('product.product', string='Product1', help="Product VAT-1")
    product2_id = fields.Many2one('product.product', string='Product2', help="Product VAT-2")
    product3_id = fields.Many2one('product.product', string='Product3', help="Product VAT-3")
    product4_id = fields.Many2one('product.product', string='Product4', help="Product VAT-4")
    journal_id = fields.Many2one('account.journal', string='Invoice Journal', help="""
    * Vendor INV11 (DS/DE) à Linked to Country = ZL and DE
    * Vendor INV12 (DS/BE) à Linked to Country = BE
    * Vendor INV13 (DS/BE) à Linked to Country = NL""")

    file = fields.Binary('File')
    import_warning = fields.Text('Import Summary', readonly='1')

    @api.multi
    def do_import_inv06(self):

        partner_pool = self.env['res.partner']
        invoice_pool = self.env['account.invoice']

        book = open_workbook(file_contents=base64.decodestring(self.file))
        sheet = book.sheet_by_index(0)

        skip_rows = 1
        col_map = {}

        log_map = []
        count = 0
        inv_create_count = 0
        inv_update_count = 0
        refund_create_count = 0
        refund_update_count = 0
        customer_count = 0
        partner_ids = partner_pool.search([])

# Country    Book    Document type    Document number    sales order no.    purchase order no.    purchase invoice no    Document date
# Customer number    Customer Name    Customer VAT-ID    Remark        inv amount ex-VAT (VAT rate #1)
# inv amount ex-VAT (VAT rate #2)    VAT amount #2    inv amount ex-VAT (VAT rate #3)    VAT amount #3    
# inv amount ex-VAT (VAT rate #4)    VAT amount #4    inv amount ex VAT total    VAT total    document total                   
# check Amount by supplier document    Expiry date    cash discount rate in %    cash discount ex-VAT (VAT rate #1)
# VAT amount cash discount #1    cash discount ex-VAT (VAT rate #2)    VAT amount cash discount #2    cash discount ex-VAT (VAT rate #3)
# VAT amount cash discount #3    cash discount ex-VAT (VAT rate #4)    VAT amount cash discount #4    total cash discount ex VAT    
# total cash VAT discount    Cash discount expiry date    IC_Input    IC_Output

        for row in imap(sheet.row, range(sheet.nrows)):
            company_code = self.company_id.name[:2]
            if count == 0:
                col_index = 0
                for col in row:
                    col_map[col.value.replace(" ", "").lower()] = col_index
                    col_index += 1

                if 'customernumber' not in col_map:
                    raise except_orm('No customer number column found', 'Please upload valid file with customer number column in first row')

            count += 1
            if count <= skip_rows:
                continue
            customernumber = str(int(row[col_map['customernumber']].value))

            Country = row[col_map['country']].value.strip()
            if company_code == 'DE' and Country == 'ZL':
                Country = 'DE'
            if company_code != Country:
                raise except_orm('Data of the selected file is not for selected company. Please switch to proper company then try again!')



            Book = row[col_map['book']].value
# customer invoice
            CustomerName = row[col_map['customername']].value.strip()
            customer_vat = row[col_map['customervat-id']].value.strip()
            reference = row[col_map['remark']].value


            invoice_number = row[col_map['remark']].value
            if isinstance(invoice_number, float):
                invoice_number = str(int(invoice_number))
#             if not invoice_number:
#                 continue

            inv_date_invoice = row[col_map['documentdate']].value
            inv_date_due = row[col_map['expirydate']].value

            fiscal_year = ''
            if inv_date_invoice and inv_date_invoice != 'NULL':
                inv_date_invoice = xlrd.xldate_as_tuple(inv_date_invoice, book.datemode)
                fiscal_year = str(inv_date_invoice[0])
                inv_date_invoice = str(inv_date_invoice[2]) + '-' + str(inv_date_invoice[1]) + '-' + str(inv_date_invoice[0])
                inv_date_invoice = parse(inv_date_invoice, dayfirst=True)
                inv_date_invoice = datetime.strftime(inv_date_invoice, DEFAULT_SERVER_DATE_FORMAT)

            if inv_date_due and inv_date_due != 'NULL':
                inv_date_due = xlrd.xldate_as_tuple(inv_date_due, book.datemode)
                inv_date_due = str(inv_date_due[2]) + '-' + str(inv_date_due[1]) + '-' + str(inv_date_due[0])
                inv_date_due = parse(inv_date_due, dayfirst=True)
                inv_date_due = datetime.strftime(inv_date_due, DEFAULT_SERVER_DATE_FORMAT)

            inv_doc_number = str(row[col_map['documentnumber']].value)
#             if inv_doc_number and len(inv_doc_number) < 5:
#                 prefix = 5 - len(inv_doc_number)
#                 if prefix == 1:
#                     add = '0'
#                 elif prefix == 2:
#                     add = '00'
#                 elif prefix == 3:
#                     add = '000'
#                 else:
#                     add = '0000'
#                 inv_doc_number = add + inv_doc_number
            invoice_name = fiscal_year + '-' + inv_doc_number

# Here the rule regarding the VAT is this one if column H and colmun I are equals then "PInvVatSystemDsc" is "Europese Unie" with O% EU M as Tax description AND the fiscal position will be : "Regime Intra-Communautaire"
# Otherwhise it it "Binnenland Normaal" with 21% M as Tax Account AND the fiscal position will be: "Regime National"
# and we follow exaclty the same logic as we did for the DS report with the invoice.sales.line

#             col_H = row[col_map['Totaalbedrag-BTWdocumentmunt']].value
#             col_I = row[col_map['Totaalbedragdocumentmunt']].value
# 
# 
# #             VatSystemDsc = row[col_map['PInvVatSystemDsc']].value.strip()
#             fiscal_position = False
#             imd = self.env['ir.model.data']
# #             if VatSystemDsc == 'Europese Unie':
#             if col_H == col_I:
#                 if self.venice_system == 'Belgium':
#                     fiscal_position = imd.xmlid_to_res_id('l10n_be.1_fiscal_position_template_3')
#                 if self.venice_system == 'Netherlands':
#                     fiscal_position = imd.xmlid_to_res_id('l10n_nl.3_fiscal_position_template_eu')
# #             if VatSystemDsc == 'Binnenland normaal':
#             else:
#                 if self.venice_system == 'Belgium':
#                     fiscal_position = imd.xmlid_to_res_id('l10n_be.1_fiscal_position_template_1')
#                 if self.venice_system == 'Netherlands':
#                     fiscal_position = imd.xmlid_to_res_id('l10n_nl.3_fiscal_position_template_national')

            venice_system = False
            if self.venice_system == 'Belgium':
                venice_system = 'Belgium'
                customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == 'Belgium'])
            elif self.venice_system == 'Netherlands':
                venice_system = 'Netherlands'
                customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == 'Netherlands'])
            else:
                customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == False])

            po_number = row[col_map['purchaseorderno.']].value
            so_number = row[col_map['salesorderno.']].value
            purchase_inv_no = row[col_map['purchaseinvoiceno.']].value

            invoice_data = {
                'name': invoice_name,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'date_invoice': inv_date_invoice,
                'date_due': inv_date_due,
                'venice_docnum': inv_doc_number,
#                 'fiscal_position_id': fiscal_position,
                'type': 'out_invoice',
                'reference': invoice_number,
                'venice_customername': CustomerName,
                'venice_pinvremark': reference,
                'venice_sinvoiceaccyear': fiscal_year,
                'venice_porderdocnumber': po_number,
                'venice_sorderdocnumber': so_number,
                'venice_pinvoicedocnum': purchase_inv_no,
#                'clientfiscalposition': fiscal_position and self.env['account.fiscal.position'].browse(fiscal_position).name or '',
                'import_wizard': True,
            }

            if customernumber not in customer_map:
                if customernumber and customernumber != '0' and customernumber not in customer_map:
                    customer_id = partner_pool.create({'name': CustomerName,
                                                                        'venice_nummer' : customernumber,
                                                                        'sinv_creation' : True,
                                                                        'sdt_section' : 'distrismart',
                                                                        'customer': True,
                                                                        'supplier': False,
                                                                        'venice_system': venice_system,
                                                                        'vat': customer_vat,
                                                                         })
                    customer_map[customernumber] = customer_id.id
                    customer_count += 1
                    partner_ids |= customer_id
            else:
                if venice_system:
                    customer_map[customernumber] = partner_pool.search([('venice_nummer','=',customernumber), ('venice_system','=',venice_system)]).id
                else:
                    customer_map[customernumber] = partner_pool.search([('venice_nummer','=',customernumber), ('venice_system','=',False)]).id
            invoice_data['partner_id'] = customer_map[customernumber]
            invoice_data['venice_customernumber'] = customernumber
#             if vendornumber != '0':
#     #             DS006/BE
#                 if vendornumber and len(vendornumber) < 3:
#                     prefix = 3 - len(vendornumber)
#                     if prefix == 1:
#                         add = '0'
#                     else:
#                         add = '00'
#                     vendornumber = add+vendornumber
#                 product_ref_initial = 'DS' + vendornumber
#                 product_internal_ref = product_ref_initial+'/'+company_code
#                 if company_code == 'BE':
#                     product_id = product_pool.search([('ds_ref_be','=',product_internal_ref)])
#                 if company_code == 'DE':
#                     product_id = product_pool.search([('ds_ref_de','=',product_internal_ref)])
#                 if company_code == 'NL':
#                     product_id = product_pool.search([('ds_ref_nl','=',product_internal_ref)])
#                 if company_code == 'FR':
#                     product_id = product_pool.search([('ds_ref_fr','=',product_internal_ref)])
#                 if not product_id:
#                     raise UserError(_('No Product found with reference  %s.') % (product_internal_ref))
            product1_price_unit = row[col_map['invamountex-vat(vat-rate#1)']].value
            product2_price_unit = row[col_map['invamountex-vat(vat-rate#2)']].value
            product3_price_unit = row[col_map['invamountex-vat(vat-rate#3)']].value
            product4_price_unit = row[col_map['invamountex-vat(vat-rate#4)']].value

            def create_invoice_lines(invoice_id, product_id, customer_invoice_line_data):
                invoice_line_ids = self.env['account.invoice.line'].search([('product_id','=',product_id.id),('invoice_id','=',invoice_id.id)])
                sale_price_unit = customer_invoice_line_data.get('price_unit', 0)
                if invoice_line_ids:
                    invoice_line_ids[0].write(customer_invoice_line_data)
                    invoice_line_ids[0]._onchange_product_id()
                    invoice_line_ids[0].write({'price_unit': sale_price_unit})
                else:
                    customer_invoice_line = self.env['account.invoice.line'].create(customer_invoice_line_data)
                    customer_invoice_line._onchange_product_id()
                    customer_invoice_line.write({'price_unit': sale_price_unit})
                invoice_id._onchange_invoice_line_ids()

            if Book == 'SLS':
                invoice_id = invoice_pool.search([('name','=',invoice_name),('type','=','out_invoice')])
                _logger.warning( "partner_id '%s' and partner name '%s'.", invoice_data['partner_id'], invoice_data['name'])
                if invoice_id:
                    invoice_id.write(invoice_data)
                    inv_update_count += 1
                else:
                    invoice_id = invoice_pool.create(invoice_data)
                    inv_create_count += 1

                customer_invoice_line_data = {
                    'quantity': 1,
                    'invoice_id': invoice_id.id,
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'name': 'import'
                }

                if product1_price_unit != 0 and self.product1_id:
                    customer_invoice_line_data.update({
                                                    'product_id': self.product1_id.id,
                                                    'price_unit': product1_price_unit,
                                                        })
                    create_invoice_lines(invoice_id, self.product1_id, customer_invoice_line_data)

                if product2_price_unit != 0 and self.product2_id:
                    customer_invoice_line_data.update({
                                                    'product_id': self.product2_id.id,
                                                    'price_unit': product2_price_unit,
                                                        })
                    create_invoice_lines(invoice_id, self.product2_id, customer_invoice_line_data)

                if product3_price_unit != 0 and self.product3_id:
                    customer_invoice_line_data.update({
                                                    'product_id': self.product3_id.id,
                                                    'price_unit': product3_price_unit,
                                                        })
                    create_invoice_lines(invoice_id, self.product3_id, customer_invoice_line_data)

                if product4_price_unit != 0 and self.product4_id:
                    customer_invoice_line_data.update({
                                                    'product_id': self.product4_id.id,
                                                    'price_unit': product4_price_unit,
                                                        })
                    create_invoice_lines(invoice_id, self.product4_id, customer_invoice_line_data)

            if Book == 'SCN':
                invoice_data['type'] = 'out_refund'
                invoice_id = invoice_pool.search([('name','=',invoice_name),('type','=','out_refund')])
                if invoice_id:
                    invoice_id.write(invoice_data)
                    refund_update_count += 1
                else:
                    invoice_id = invoice_pool.create(invoice_data)
                    refund_create_count += 1

                customer_invoice_line_data = {
                    'quantity': 1,
                    'invoice_id': invoice_id.id,
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'name': 'import'
                }

                if product1_price_unit != 0 and self.product1_id:
                    customer_invoice_line_data.update({
                                                    'product_id': self.product1_id.id,
                                                    'price_unit': product1_price_unit,
                                                        })
                    create_invoice_lines(invoice_id, self.product1_id, customer_invoice_line_data)

                if product2_price_unit != 0 and self.product2_id:
                    customer_invoice_line_data.update({
                                                    'product_id': self.product2_id.id,
                                                    'price_unit': product2_price_unit,
                                                        })
                    create_invoice_lines(invoice_id, self.product2_id, customer_invoice_line_data)

                if product3_price_unit != 0 and self.product3_id:
                    customer_invoice_line_data.update({
                                                    'product_id': self.product3_id.id,
                                                    'price_unit': product3_price_unit,
                                                        })
                    create_invoice_lines(invoice_id, self.product3_id, customer_invoice_line_data)

                if product4_price_unit != 0 and self.product4_id:
                    customer_invoice_line_data.update({
                                                    'product_id': self.product4_id.id,
                                                    'price_unit': product4_price_unit,
                                                        })
                    create_invoice_lines(invoice_id, self.product4_id, customer_invoice_line_data)


            if count % 100 == 0:
                _logger.info(count)
                self._cr.commit()

        Warning_msg = ("All Lines imported successfully.\nTotal Lines in xlsx File: %s\
                        \nNumber of Invoice Created                : %s\
                        \nNumber of Invoice Updated               : %s\
                        \nNumber of New Customer Created      : %s\
                        \nNumber of Refunds Created          : %s\
                        \nNumber of Refunds Updated        : %s")%(count-1,
                                                                   inv_create_count,
                                                                   inv_update_count,
                                                                   customer_count,
                                                                   refund_create_count,
                                                                   refund_update_count)
        import_id = self.env['import.inv06'].create({'import_warning': Warning_msg,
                                                     'warning': True})
        return {
            'name': 'INV06 Import',
            'view_mode': 'form',
            'res_id': import_id.id,
            'res_model': 'import.inv06',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
