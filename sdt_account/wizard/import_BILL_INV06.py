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

class ImportBillInv06(models.TransientModel):
    _name = 'import.bill.inv06'
    _description = 'Import Bill INV06'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id, help="""
    * ZL = SDT.DE
    * DE = SDT.DE
    * BE = SDT.BE
    * NL = SDT.NL
    """)
    product1_id = fields.Many2one('product.product', string='Product1', help="Product VAT-1")
    product2_id = fields.Many2one('product.product', string='Product2', help="Product VAT-2")
    product3_id = fields.Many2one('product.product', string='Product3', help="Product VAT-3")
    product4_id = fields.Many2one('product.product', string='Product4', help="Product VAT-4")
    journal_id = fields.Many2one('account.journal', string='Bill Journal', help="""
    * Vendor BILLS11 (DS/DE) Ã  Linked to Country = ZL and DE
    * Vendor BILLS12 (DS/BE) Ã  Linked to Country = BE
    * Vendor BILLS13 (DS/BE) Ã  Linked to Country = NL""")

    file = fields.Binary('File')
    import_warning = fields.Text('Import Summary', readonly='1')

    @api.multi
    def do_import_bill_inv06(self):

        partner_pool = self.env['res.partner']
        invoice_pool = self.env['account.invoice']
        product_pool = self.env['product.product']

        book = open_workbook(file_contents=base64.decodestring(self.file))
        sheet = book.sheet_by_index(0)

        skip_rows = 1
        col_map = {}

        log_map = []
        count = 0
        bill_create_count = 0
        bill_update_count = 0
        refund_create_count = 0
        refund_update_count = 0
        supplier_count = 0
# Country    Book    Document type    Document number    purchase order no.    sales order no.    Document date
# Supplier number    Supplier Name    Remark (vendor invoice number)    VAT system    amount ex-VAT (VAT rate #1)
# VAT amount #1    amount ex-VAT (VAT rate #2)    VAT amount #2    amount ex-VAT (VAT rate #3)    VAT amount #3    
# amount ex-VAT (VAT rate #4)    VAT amount #4    amount ex VAT total    VAT total    document total                   
# check Amount by supplier document    Expiry date    cash discount rate in %    cash discount ex-VAT (VAT rate #1)
# VAT amount cash discount #1    cash discount ex-VAT (VAT rate #2)    VAT amount cash discount #2    cash discount ex-VAT (VAT rate #3)
# VAT amount cash discount #3    cash discount ex-VAT (VAT rate #4)    VAT amount cash discount #4    total cash discount ex VAT    
# total cash VAT discount    Cash discount expiry date    IC_Input    IC_Output

        partner_ids = partner_pool.search([])
        vendor_map = dict([(vendor.venice_supnum, vendor.id) for vendor in partner_ids])

        for row in imap(sheet.row, range(sheet.nrows)):
            company_code = self.company_id.name[:2]
            if count == 0:
                col_index = 0
                for col in row:
                    col_map[col.value.replace(" ", "").lower()] = col_index
                    col_index += 1

                if 'suppliernumber' not in col_map:
                    raise except_orm('No supplier number column found', 'Please upload valid file with supplier number column in first row')

            count += 1
            if count <= skip_rows:
                continue

            Country = row[col_map['country']].value.strip()
            if company_code == 'DE' and Country == 'ZL':
                Country = 'DE'
            if company_code != Country:
                raise except_orm('Data of the selected file is not for selected company. Please switch to proper company then try again!')

            Book = row[col_map['book']].value
# Vendor Bill
            SuppName = row[col_map['suppliername']].value
            reference = row[col_map['remark(vendorinvoicenumber)']].value


            bill_number = row[col_map['remark(vendorinvoicenumber)']].value
            if isinstance(bill_number, float):
                bill_number = str(int(bill_number))
#             if not bill_number:
#                 continue

            bill_date_invoice = row[col_map['documentdate']].value
            bill_date_due = row[col_map['expirydate']].value

            fiscal_year = ''
            if bill_date_invoice and bill_date_invoice != 'NULL':
                bill_date_invoice = xlrd.xldate_as_tuple(bill_date_invoice, book.datemode)
                fiscal_year = str(bill_date_invoice[0])
                bill_date_invoice = str(bill_date_invoice[2]) + '-' + str(bill_date_invoice[1]) + '-' + str(bill_date_invoice[0])
                bill_date_invoice = parse(bill_date_invoice, dayfirst=True)
                bill_date_invoice = datetime.strftime(bill_date_invoice, DEFAULT_SERVER_DATE_FORMAT)

            if bill_date_due and bill_date_due != 'NULL':
                bill_date_due = xlrd.xldate_as_tuple(bill_date_due, book.datemode)
                bill_date_due = str(bill_date_due[2]) + '-' + str(bill_date_due[1]) + '-' + str(bill_date_due[0])
                bill_date_due = parse(bill_date_due, dayfirst=True)
                bill_date_due = datetime.strftime(bill_date_due, DEFAULT_SERVER_DATE_FORMAT)

            bill_doc_number = str(row[col_map['documentnumber']].value)
#             if bill_doc_number and len(bill_doc_number) < 5:
#                 prefix = 5 - len(bill_doc_number)
#                 if prefix == 1:
#                     add = '0'
#                 elif prefix == 2:
#                     add = '00'
#                 elif prefix == 3:
#                     add = '000'
#                 else:
#                     add = '0000'
#                 bill_doc_number = add + bill_doc_number
            bill_name = fiscal_year + '-' + bill_doc_number

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

            po_number = row[col_map['purchaseorderno.']].value
            so_number = row[col_map['salesorderno.']].value

            bill_data = {
                'name': bill_name,
                'journal_id': self.journal_id.id,
                'company_id': self.company_id.id,
                'date_invoice': bill_date_invoice,
                'date_due': bill_date_due,
                'venice_docnum': bill_doc_number,
#                 'fiscal_position_id': fiscal_position,
                'type': 'in_invoice',
                'reference': bill_number,
                'venice_suppname': SuppName,
                'venice_pinvremark': reference,
                'venice_sinvoiceaccyear': fiscal_year,
                'venice_porderdocnumber': po_number,
                'venice_sorderdocnumber': so_number,
#                'clientfiscalposition': fiscal_position and self.env['account.fiscal.position'].browse(fiscal_position).name or '',
                'import_wizard': True,
            }

            if 'suppliernumber' in col_map:
                vendornumber = str(int(row[col_map['suppliernumber']].value))
                if vendornumber != '0':
                    if vendornumber and vendornumber not in vendor_map:
                        raise UserError(_('No vendor found with SupNum  %s.') % (vendornumber))
                    else:
                        vendor_map[vendornumber] = partner_pool.search([('venice_supnum','=',vendornumber)]).id
                    bill_data['partner_id'] = vendor_map[vendornumber]
                    bill_data['venice_suppnum'] = vendornumber

            if vendornumber != '0':
    #             DS006/BE
                if vendornumber and len(vendornumber) < 3:
                    prefix = 3 - len(vendornumber)
                    if prefix == 1:
                        add = '0'
                    else:
                        add = '00'
                    vendornumber = add+vendornumber
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

            product1_price_unit = row[col_map['amountex-vat(vatrate#1)']].value
            product2_price_unit = row[col_map['amountex-vat(vatrate#2)']].value
            product3_price_unit = row[col_map['amountex-vat(vatrate#3)']].value
            product4_price_unit = row[col_map['amountex-vat(vatrate#4)']].value

            def create_invoice_lines(bill_id, product_id, supplier_invoice_line_data):
                bill_line_ids = self.env['account.invoice.line'].search([('product_id','=',product_id.id),('invoice_id','=',bill_id.id)])
                if bill_line_ids:
                    bill_line_ids[0].write(supplier_invoice_line_data)
                    bill_line_ids[0]._onchange_product_id()
                else:
                    supplier_invoice_line = self.env['account.invoice.line'].create(supplier_invoice_line_data)
                    supplier_invoice_line._onchange_product_id()
                bill_id._onchange_invoice_line_ids()

            if Book == 'PUR':
                bill_id = invoice_pool.search([('name','=',bill_name),('type','=','in_invoice')])
                _logger.warning( "partner_id '%s' and partner name '%s'.", bill_data['partner_id'], bill_data['venice_suppname'])
                if bill_id:
                    bill_id.write(bill_data)
                    bill_update_count += 1
                else:
                    bill_id = invoice_pool.create(bill_data)
                    bill_create_count += 1

                supplier_invoice_line_data = {
                    'quantity': 1,
                    'invoice_id': bill_id.id,
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'name': 'import'
                }

                if product1_price_unit != 0 and self.product1_id:
                    supplier_invoice_line_data.update({
                                                    'product_id': self.product1_id.id,
                                                    'price_unit': product1_price_unit,
                                                        })
                    create_invoice_lines(bill_id, self.product1_id, supplier_invoice_line_data)

                if product2_price_unit != 0 and self.product2_id:
                    supplier_invoice_line_data.update({
                                                    'product_id': self.product2_id.id,
                                                    'price_unit': product2_price_unit,
                                                        })
                    create_invoice_lines(bill_id, self.product2_id, supplier_invoice_line_data)

                if product3_price_unit != 0 and self.product3_id:
                    supplier_invoice_line_data.update({
                                                    'product_id': self.product3_id.id,
                                                    'price_unit': product3_price_unit,
                                                        })
                    create_invoice_lines(bill_id, self.product3_id, supplier_invoice_line_data)

                if product4_price_unit != 0 and self.product4_id:
                    supplier_invoice_line_data.update({
                                                    'product_id': self.product4_id.id,
                                                    'price_unit': product4_price_unit,
                                                        })
                    create_invoice_lines(bill_id, self.product4_id, supplier_invoice_line_data)

            if Book == 'PCN':
                bill_data['type'] = 'in_refund'
                bill_id = invoice_pool.search([('name','=',bill_name),('type','=','in_refund')])
                if bill_id:
                    bill_id.write(bill_data)
                    refund_update_count += 1
                else:
                    bill_id = invoice_pool.create(bill_data)
                    refund_create_count += 1

                supplier_invoice_line_data = {
                    'quantity': 1,
                    'invoice_id': bill_id.id,
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'name': 'import'
                }

                if product1_price_unit != 0 and self.product1_id:
                    supplier_invoice_line_data.update({
                                                    'product_id': self.product1_id.id,
                                                    'price_unit': product1_price_unit,
                                                        })
                    create_invoice_lines(bill_id, self.product1_id, supplier_invoice_line_data)

                if product2_price_unit != 0 and self.product2_id:
                    supplier_invoice_line_data.update({
                                                    'product_id': self.product2_id.id,
                                                    'price_unit': product2_price_unit,
                                                        })
                    create_invoice_lines(bill_id, self.product2_id, supplier_invoice_line_data)

                if product3_price_unit != 0 and self.product3_id:
                    supplier_invoice_line_data.update({
                                                    'product_id': self.product3_id.id,
                                                    'price_unit': product3_price_unit,
                                                        })
                    create_invoice_lines(bill_id, self.product3_id, supplier_invoice_line_data)

                if product4_price_unit != 0 and self.product4_id:
                    supplier_invoice_line_data.update({
                                                    'product_id': self.product4_id.id,
                                                    'price_unit': product4_price_unit,
                                                        })
                    create_invoice_lines(bill_id, self.product4_id, supplier_invoice_line_data)


            if count % 100 == 0:
                _logger.info(count)
                self._cr.commit()

        Warning_msg = ("All Lines imported successfully.\nTotal Lines in xlsx File: %s\
                        \nNumber of Bills Created                : %s\
                        \nNumber of Bills Updated               : %s\
                        \nNumber of New Vendor Created      : %s\
                        \nNumber of Refunds Created          : %s\
                        \nNumber of Refunds Updated        : %s")%(count-1,
                                                                   bill_create_count,
                                                                   bill_update_count,
                                                                   supplier_count,
                                                                   refund_create_count,
                                                                   refund_update_count)
        import_id = self.env['import.bill.inv06'].create({'import_warning': Warning_msg,
                                                            'warning': True})
        return {
            'name': 'BILL06 Import',
            'view_mode': 'form',
            'res_id': import_id.id,
            'res_model': 'import.bill.inv06',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
