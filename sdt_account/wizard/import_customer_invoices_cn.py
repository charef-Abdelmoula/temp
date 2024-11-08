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


class ImportCustomerInvoicesCN(models.TransientModel):
    _name = 'import.customer.invoices.cn'
    _description = 'Import Customer Invoices and Credit Notes'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    product_id = fields.Many2one('product.product', string='Product')
    journal_id = fields.Many2one('account.journal', string='Invoice Journal')
    venice_system = fields.Selection([('Germany','Germany'),
                                      ('Belgium','Belgium'),
                                      ('Netherlands','Netherlands')], 'Venice System')
    file = fields.Binary('File')
    import_warning = fields.Text('Import Summary', readonly='1')

    @api.multi
    def do_import_customer_invoices(self):

        partner_pool = self.env['res.partner']
        invoice_pool = self.env['account.invoice']
#         product_pool = self.env['product.product']

        book = open_workbook(file_contents=base64.decodestring(self.file))
        sheet = book.sheet_by_index(0)

        skip_rows = 1
        col_map = {}

#         log_map = []
        count = 0
        invoice_create_count = 0
        invoice_update_count = 0
        refund_create_count = 0
        refund_update_count = 0
        customer_count = 0

        partner_ids = partner_pool.search([])
#Required Columns of sample file
# Dagboek (1)    Documentnummer (2)    Documentdatum    Nummer klant    Firmanaam    Firmanaam2    
# Opmerking    Totaal bedrag-BTW documentmunt     Totaal bedrag documentmunt    Vervaldatum
#Optional Columns
# Toevoeging: datum    Toevoeging: tijdstip    Wijziging: datum    Wijziging: tijdstip

        for row in imap(sheet.row, range(sheet.nrows)):
            if count == 0:
                col_index = 0
                for col in row:
                    col_map[col.value.replace(" ", "").lower()] = col_index
                    col_index += 1
                if 'nummerklant' not in col_map:
                    raise except_orm('No nummer klant column found', 'Please upload valid file with nummer klant column in first row.')

            count += 1
            if count <= skip_rows:
                continue

#             customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids])

            dagboek = row[col_map['dagboek(1)']].value
# customer Bill
            Opmerking = row[col_map['opmerking']].value


            invoice_number = row[col_map['opmerking']].value
            if isinstance(invoice_number, float):
                invoice_number = str(int(invoice_number))
#             if not invoice_number:
#                 continue

            date_invoice = row[col_map['documentdatum']].value
            invoice_date_due = row[col_map['vervaldatum']].value

            fiscal_year = ''
            if date_invoice != 'NULL':
                date_invoice = xlrd.xldate_as_tuple(date_invoice, book.datemode)
                fiscal_year = str(date_invoice[0])
                date_invoice = str(date_invoice[2]) + '-' + str(date_invoice[1]) + '-' + str(date_invoice[0])
                date_invoice = parse(date_invoice, dayfirst=True)
                date_invoice = datetime.strftime(date_invoice, DEFAULT_SERVER_DATE_FORMAT)

            if invoice_date_due != 'NULL':
                invoice_date_due = xlrd.xldate_as_tuple(invoice_date_due, book.datemode)
                invoice_date_due = str(invoice_date_due[2]) + '-' + str(invoice_date_due[1]) + '-' + str(invoice_date_due[0])
                invoice_date_due = parse(invoice_date_due, dayfirst=True)
                invoice_date_due = datetime.strftime(invoice_date_due, DEFAULT_SERVER_DATE_FORMAT)

            invoice_doc_number = str(int(row[col_map['documentnummer(2)']].value))
            if invoice_doc_number and len(invoice_doc_number) < 5:
                prefix = 5 - len(invoice_doc_number)
                if prefix == 1:
                    add = '0'
                elif prefix == 2:
                    add = '00'
                elif prefix == 3:
                    add = '000'
                else:
                    add = '0000'
                invoice_doc_number = add + invoice_doc_number 
            inv_name = fiscal_year + '-' + invoice_doc_number

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

            venice_system = False
            if self.venice_system == 'Belgium':
                venice_system = 'Belgium'
                customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == 'Belgium'])
            elif self.venice_system == 'Netherlands':
                venice_system = 'Netherlands'
                customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == 'Netherlands'])
            else:
                customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == False])

            invoice_data = {
                'name' : inv_name,
                'journal_id' : self.journal_id.id,
                'company_id': self.company_id.id,
                'date_invoice' : date_invoice,
                'date_due' : invoice_date_due,
                'venice_docnum' : invoice_doc_number,
                'fiscal_position_id': fiscal_position,
                'type': 'out_invoice',
                'reference': invoice_number,
                'venice_sinvremark': Opmerking,
                'venice_sinvoiceaccyear': fiscal_year,
                'clientfiscalposition': fiscal_position and self.env['account.fiscal.position'].browse(fiscal_position).name or '',
                'import_wizard': True,
            }

#         if 'Nummerklant' in col_map:
#         if SInvoiceBook == 'VER':

            if 'nummerklant' in col_map:
                customernumber = str(int(row[col_map['nummerklant']].value))
                customer_name = row[col_map['firmanaam']].value
                if customernumber and customernumber != '0' and customernumber not in customer_map:
                    customer_id = partner_pool.create({'name': customer_name,
                                                                         'venice_nummer' : customernumber,
                                                                         'sinv_creation' : True,
                                                                         'sdt_section' : 'distrismart',
                                                                         'customer': True,
                                                                         'supplier': False,
                                                                         'venice_system': venice_system,
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
            sale_price_unit = row[col_map['totaalbedrag-btwdocumentmunt']].value
            if dagboek == 'VER':
                invoice_id = invoice_pool.search([('name','=',inv_name),('type','=','out_invoice')])
                if invoice_id:
                    invoice_id.write(invoice_data)
                    invoice_update_count += 1 
                else:
                    invoice_id = invoice_pool.create(invoice_data)
                    invoice_create_count += 1

                customer_invoice_line_data = {
                    'product_id': self.product_id.id,
                    'quantity': 1,
                    'price_unit': sale_price_unit,
                    'invoice_id': invoice_id.id,
                    'account_id': self.journal_id.default_debit_account_id.id,
                    'name': 'Various Invoice'
                }
                inv_line_ids = self.env['account.invoice.line'].search([('name','=','Various Invoice'),('invoice_id','=',invoice_id.id)])
                if inv_line_ids:
                    inv_line_ids[0].write(customer_invoice_line_data)
#                     if vendornumber != '0':
                    inv_line_ids[0]._onchange_product_id()
                    inv_line_ids[0].write({'price_unit': sale_price_unit})
                else:
                    customer_invoice_line = self.env['account.invoice.line'].create(customer_invoice_line_data)
#                     if vendornumber == '0':
                    customer_invoice_line._onchange_product_id()
                    customer_invoice_line.write({'price_unit': sale_price_unit})
                invoice_id._onchange_invoice_line_ids()

            if dagboek == 'KNV':
                invoice_data['type'] = 'out_refund'
                cn_id = invoice_pool.search([('name','=',inv_name),('type','=','out_refund')])
                if cn_id:
                    cn_id.write(invoice_data)
                    refund_update_count += 1
                else:
                    cn_id = invoice_pool.create(invoice_data)
                    refund_create_count += 1

                cn_invoice_line_data = {
                    'product_id': self.product_id.id,
                    'quantity': 1,
                    'price_unit': -sale_price_unit,
                    'invoice_id': cn_id.id,
#                     'account_id': product_id.property_account_expense_id.id,
                    'account_id': self.journal_id.default_credit_account_id.id,
                    'name': 'Various Invoice'
                }
                cn_line_ids = self.env['account.invoice.line'].search([('product_id','=',self.product_id.id),('invoice_id','=',cn_id.id)])
                if cn_line_ids:
                    cn_line_ids[0].write(cn_invoice_line_data)
                    cn_line_ids[0]._onchange_product_id()
                    cn_line_ids[0].write({'price_unit': -sale_price_unit})
                else:
                    customer_invoice_line = self.env['account.invoice.line'].create(cn_invoice_line_data)
                    customer_invoice_line._onchange_product_id()
                    customer_invoice_line.write({'price_unit': -sale_price_unit})
                cn_id._onchange_invoice_line_ids()

            if count % 100 == 0:
                _logger.info(count)
                self._cr.commit()

        Warning_msg = ("All Lines imported successfully.\nTotal Lines in xlsx File: %s\
                        \nNumber of Invoices Created                : %s\
                        \nNumber of Invoices Updated               : %s\
                        \nNumber of New Customer Created      : %s\
                        \nNumber of Credit Notes Created          : %s\
                        \nNumber of Credit Notes Updated        : %s")%(count-1,
                                                                   invoice_create_count,
                                                                   invoice_update_count,
                                                                   customer_count,
                                                                   refund_create_count,
                                                                   refund_update_count)
        import_id = self.env['import.customer.invoices.cn'].create({'import_warning': Warning_msg,
                                                            'warning': True})

        return {
            'name': 'Import Invoices and Credit Notes',
            'view_mode': 'form',
            'res_id': import_id.id,
            'res_model': 'import.customer.invoices.cn',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
