# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import base64

import xlrd
from xlrd import open_workbook
from datetime import datetime, timedelta
from dateutil.parser import parse

import logging

try:
    from itertools import imap
except ImportError:
    # Python 3...
    imap=map
# from boto.mashups import order

_logger = logging.getLogger(__name__)


class ImportVendorBillsCN(models.TransientModel):
    _name = 'import.vendor.bills.cn'
    _description = 'Import Vendor Bills and Credit Notes'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    journal_id = fields.Many2one('account.journal', string='Bills Journal')
    venice_system = fields.Selection([('Germany','Germany'),
                                      ('Belgium','Belgium'),
                                      ('Netherlands','Netherlands')], 'Venice System')
    file = fields.Binary('File')
    import_warning = fields.Text('Import Summary', readonly='1')

    @api.multi
    def do_import_vendor_bills(self):

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
        customer_count = 0
#Required Columns of sample file
# Dagboek (1)    Documentnummer (2)    Documentdatum    Nummer leverancier    Firmanaam    Firmanaam2    
# Opmerking    Totaal bedrag-BTW documentmunt     Totaal bedrag documentmunt    Vervaldatum
#Optional Columns
# Toevoeging: datum    Toevoeging: tijdstip    Wijziging: datum    Wijziging: tijdstip

        partner_ids = partner_pool.search([])
        vendor_map = dict([(vendor.venice_supnum, vendor.id) for vendor in partner_ids])

        for row in imap(sheet.row, range(sheet.nrows)):
            if count == 0:
                col_index = 0
                for col in row:
                    col_map[col.value.replace(" ", "").lower()] = col_index
                    col_index += 1
                if 'nummerleverancier' not in col_map:
                    raise except_orm('No nummer leverancier column found', 'Please upload valid file with nummer leverancier column in first row.')

            count += 1
            if count <= skip_rows:
                continue

            dagboek = row[col_map['dagboek(1)']].value
# Vendor Bill
            SuppName = row[col_map['firmanaam']].value
            Opmerking = row[col_map['opmerking']].value


            bill_number = row[col_map['opmerking']].value
            if isinstance(bill_number, float):
                bill_number = str(int(bill_number))
#             if not bill_number:
#                 continue

            bill_date_invoice = row[col_map['documentdatum']].value
            bill_date_due = row[col_map['vervaldatum']].value

            fiscal_year = ''
            if bill_date_invoice != 'NULL':
                bill_date_invoice = xlrd.xldate_as_tuple(bill_date_invoice, book.datemode)
                fiscal_year = str(bill_date_invoice[0])
                bill_date_invoice = str(bill_date_invoice[2]) + '-' + str(bill_date_invoice[1]) + '-' + str(bill_date_invoice[0])
                bill_date_invoice = parse(bill_date_invoice, dayfirst=True)
                bill_date_invoice = datetime.strftime(bill_date_invoice, DEFAULT_SERVER_DATE_FORMAT)

            if bill_date_due != 'NULL':
                bill_date_due = xlrd.xldate_as_tuple(bill_date_due, book.datemode)
                bill_date_due = str(bill_date_due[2]) + '-' + str(bill_date_due[1]) + '-' + str(bill_date_due[0])
                bill_date_due = parse(bill_date_due, dayfirst=True)
                bill_date_due = datetime.strftime(bill_date_due, DEFAULT_SERVER_DATE_FORMAT)

            bill_doc_number = str(int(row[col_map['documentnummer(2)']].value))
            if bill_doc_number and len(bill_doc_number) < 5:
                prefix = 5 - len(bill_doc_number)
                if prefix == 1:
                    add = '0'
                elif prefix == 2:
                    add = '00'
                elif prefix == 3:
                    add = '000'
                else:
                    add = '0000'
                bill_doc_number = add + bill_doc_number 
            bill_name = fiscal_year + '-' + bill_doc_number

# Here the rule regarding the VAT is this one if column H and colmun I are equals then "PInvVatSystemDsc" is "Europese Unie" with O% EU M as Tax description AND the fiscal position will be : "Regime Intra-Communautaire"
# Otherwhise it it "Binnenland Normaal" with 21% M as Tax Account AND the fiscal position will be: "Regime National"
# and we follow exaclty the same logic as we did for the DS report with the invoice.sales.line

            col_H = row[col_map['totaalbedrag-btwdocumentmunt']].value
            col_I = row[col_map['totaalbedragdocumentmunt']].value


#             VatSystemDsc = row[col_map['PInvVatSystemDsc']].value.strip()
            fiscal_position = False
            imd = self.env['ir.model.data']
#             if VatSystemDsc == 'Europese Unie':
            if col_H == col_I:
                if self.venice_system == 'Belgium':
                    fiscal_position = imd.xmlid_to_res_id('l10n_be.1_fiscal_position_template_3')
                if self.venice_system == 'Netherlands':
                    fiscal_position = imd.xmlid_to_res_id('l10n_nl.3_fiscal_position_template_eu')
#             if VatSystemDsc == 'Binnenland normaal':
            else:
                if self.venice_system == 'Belgium':
                    fiscal_position = imd.xmlid_to_res_id('l10n_be.1_fiscal_position_template_1')
                if self.venice_system == 'Netherlands':
                    fiscal_position = imd.xmlid_to_res_id('l10n_nl.3_fiscal_position_template_national')

            bill_data = {
                'name' : bill_name,
                'journal_id' : self.journal_id.id,
                'company_id': self.company_id.id,
                'date_invoice' : bill_date_invoice,
                'date_due' : bill_date_due,
                'venice_docnum' : bill_doc_number,
                'fiscal_position_id': fiscal_position,
                'type': 'in_invoice',
                'reference': bill_number,
                'venice_suppname': SuppName,
                'venice_pinvremark': Opmerking,
                'venice_sinvoiceaccyear': fiscal_year,
                'clientfiscalposition': fiscal_position and self.env['account.fiscal.position'].browse(fiscal_position).name or '',
                'import_wizard': True,
            }

            if 'nummerleverancier' in col_map:
                vendornumber = str(int(row[col_map['nummerleverancier']].value))
                if vendornumber != '0':
                    if vendornumber and vendornumber not in vendor_map:
                        raise UserError(_('No vendor found with SupNum  %s.') % (vendornumber))
                    else:
                        vendor_map[vendornumber] = partner_pool.search([('venice_supnum','=',vendornumber)]).id
                    bill_data['partner_id'] = vendor_map[vendornumber]
                    bill_data['venice_suppnum'] = vendornumber

            if vendornumber != '0':
    #             DS006/BE
                company_code = self.company_id.name[:2]
                if vendornumber and len(vendornumber) < 3:
                    prefix = 3 - len(vendornumber)
                    if prefix == 1:
                        add = '0'
                    else:
                        add = '00'
                    vendornumber = add+vendornumber 
                product_ref_initial = 'DS' + vendornumber
                product_internal_ref = product_ref_initial+'/'+company_code
                if company_code == 'BE':
                    product_id = product_pool.search([('ds_ref_be','=',product_internal_ref)])
                if company_code == 'DE':
                    product_id = product_pool.search([('ds_ref_de','=',product_internal_ref)])
                if company_code == 'NL':
                    product_id = product_pool.search([('ds_ref_nl','=',product_internal_ref)])
                if company_code == 'FR':
                    product_id = product_pool.search([('ds_ref_fr','=',product_internal_ref)])
                if not product_id:
                    raise UserError(_('No Product found with reference  %s.') % (product_internal_ref))

            if dagboek == 'AAN':
                bill_id = invoice_pool.search([('name','=',bill_name),('type','=','in_invoice')])
                _logger.warning( "partner_id '%s' and partner name '%s'.", bill_data['partner_id'], bill_data['venice_suppname'])
                if bill_id:
                    bill_id.write(bill_data)
                    bill_update_count += 1
                else:
                    bill_id = invoice_pool.create(bill_data)
                    bill_create_count += 1

                purchase_price_unit = row[col_map['totaalbedrag-btwdocumentmunt']].value
                supplier_invoice_line_data = {
                    'product_id': product_id.id,
                    'quantity': 1,
                    'price_unit': purchase_price_unit,
                    'invoice_id': bill_id.id,
#                     'account_id': product_id.property_account_expense_id.id,
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'name': 'import'
                }
                bill_line_ids = self.env['account.invoice.line'].search([('product_id','=',product_id.id),('invoice_id','=',bill_id.id)])
                if bill_line_ids:
                    bill_line_ids[0].write(supplier_invoice_line_data)
                    bill_line_ids[0]._onchange_product_id()
                else:
                    supplier_invoice_line = self.env['account.invoice.line'].create(supplier_invoice_line_data)
                    supplier_invoice_line._onchange_product_id()
                bill_id._onchange_invoice_line_ids()

            if dagboek == 'KNA':
                bill_data['type'] = 'in_refund'
                bill_id = invoice_pool.search([('name','=',bill_name),('type','=','in_refund')])
                if bill_id:
                    bill_id.write(bill_data)
                    refund_update_count += 1
                else:
                    bill_id = invoice_pool.create(bill_data)
                    refund_create_count += 1

                purchase_price_unit = row[col_map['totaalbedrag-btwdocumentmunt']].value
                supplier_invoice_line_data = {
                    'product_id': product_id.id,
                    'quantity': 1,
                    'price_unit': purchase_price_unit,
                    'invoice_id': bill_id.id,
#                     'account_id': product_id.property_account_expense_id.id,
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'name': 'import'
                }
                bill_line_ids = self.env['account.invoice.line'].search([('product_id','=',product_id.id),('invoice_id','=',bill_id.id)])
                if bill_line_ids:
                    bill_line_ids[0].write(supplier_invoice_line_data)
                    bill_line_ids[0]._onchange_product_id()
                else:
                    supplier_invoice_line = self.env['account.invoice.line'].create(supplier_invoice_line_data)
                    supplier_invoice_line._onchange_product_id()
                bill_id._onchange_invoice_line_ids()

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
                                                                   customer_count,
                                                                   refund_create_count,
                                                                   refund_update_count)
        import_id = self.env['import.vendor.bills.cn'].create({'import_warning': Warning_msg,
                                                            'warning': True})

        return {
            'name': 'Import Vendor Bills and Refunds',
            'view_mode': 'form',
            'res_id': import_id.id,
            'res_model': 'import.vendor.bills.cn',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
