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


class ImportVendorBills(models.TransientModel):
    _name = 'import.vendor.bills'
    _description = 'Import Vendor Bills'

    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    bill_journal_id = fields.Many2one('account.journal', string='Bill Journal')
    invoice_journal_id = fields.Many2one('account.journal', string='Invoice Journal')
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
        inv_create_count = 0
        inv_update_count = 0
        customer_count = 0


        partner_ids = partner_pool.search([])

        for row in imap(sheet.row, range(sheet.nrows)):
            if count == 0:
                col_index = 0
                for col in row:
                    col_map[col.value.replace(" ", "").lower()] = col_index
                    col_index += 1
                if 'suppnum' not in col_map:
                    raise except_orm('No supnum column found', 'Please upload valid file with sup number column in first row')

            count += 1
            if count <= skip_rows:
                continue

            vendor_map = dict([(vendor.venice_supnum, vendor.id) for vendor in partner_ids])

            PInvoiceBook = row[col_map['pinvoicebook']].value
            SInvoiceBook = row[col_map['sinvoicebook']].value

# # Sales Order
            SorderDocNumber = row[col_map['sorderdocnumber']].value
            if isinstance(SorderDocNumber, float):
                SorderDocNumber = str(int(SorderDocNumber))
            SOrderAccYear = row[col_map['sorderaccyear']].value
            if isinstance(SOrderAccYear, float):
                SOrderAccYear = str(int(SOrderAccYear))
            SOrdDocAmountVatEx = row[col_map['sorddocamountvatex']].value
            if SOrdDocAmountVatEx == 'NULL':
                SOrdDocAmountVatEx = 0
            so_number = SorderDocNumber
            if so_number and len(so_number) < 5:
                prefix = 5 - len(so_number)
                if prefix == 1:
                    add = '0'
                elif prefix == 2:
                    add = '00'
                elif prefix == 3:
                    add = '000'
                else:
                    add = '0000'
                so_number = add + so_number 
            so_name = ''
            if str(so_number) != '00000':
                so_name = so_number
                if str(SOrderAccYear) != '0':
                    so_name = SOrderAccYear + '-' + so_number

# # Purchase Order
            POrderDocNumber = row[col_map['porderdocnumber']].value
            if isinstance(POrderDocNumber, float):
                POrderDocNumber = str(int(POrderDocNumber))
            POrderAccYear = row[col_map['porderaccyear']].value
            if isinstance(POrderAccYear, float):
                POrderAccYear = str(int(POrderAccYear))
            POrderAmountVatEx = row[col_map['porderamountvatex']].value
            if POrderAmountVatEx == 'NULL':
                POrderAmountVatEx = 0
            po_number = POrderDocNumber
            if po_number and len(po_number) < 5:
                prefix = 5 - len(po_number)
                if prefix == 1:
                    add = '0'
                elif prefix == 2:
                    add = '00'
                elif prefix == 3:
                    add = '000'
                else:
                    add = '0000'
                po_number = add + po_number
            po_name = ''
            if str(po_number) != '00000':
                po_name = po_number
                if str(POrderAccYear) != '0':
                    po_name = POrderAccYear + '-' + po_number

# Vendor Bill
            SuppName = row[col_map['suppname']].value
            PInvoiceDocNum = row[col_map['pinvoicedocnum']].value
            if isinstance(PInvoiceDocNum, float):
                SInvoiceDocNum = str(int(PInvoiceDocNum))
            PInvoiceAmount = row[col_map['pinvoiceamount']].value
            PInvRemark = row[col_map['pinvremark']].value

# Client Invoice
            SInvoiceAmountVatEx = row[col_map['sinvoiceamountvatex']].value
            if SInvoiceAmountVatEx == 'NULL':
                SInvoiceAmountVatEx = 0
#             invoice_name = SInvoiceAccYear + '-' + SInvoiceDocNum
            SInvoiceAmount = row[col_map['sinvoiceamount']].value
            SInvoiceAmount = row[col_map['sinvoiceamount']].value

# Client Information
            CustomerName = row[col_map['customername']].value
            CustomerNumber = row[col_map['customernumber']].value
            if isinstance(CustomerNumber, float):
                CustomerNumber = str(int(CustomerNumber))
            CustomerSubNumber = row[col_map['customersubnumber']].value
            if isinstance(CustomerSubNumber, float):
                CustomerSubNumber = str(int(CustomerSubNumber))
            SInvRemark = row[col_map['sinvremark']].value
            DeliveryName = row[col_map['deliveryname']].value
            DeliveryNumber = row[col_map['deliverynumber']].value
            if isinstance(DeliveryNumber, float):
                DeliveryNumber = str(int(DeliveryNumber))
            DeliverySubNumber = row[col_map['deliverysubnumber']].value
            if isinstance(DeliverySubNumber, float):
                DeliverySubNumber = str(int(DeliverySubNumber))

            bill_number = row[col_map['pinvremark']].value
            if isinstance(bill_number, float):
                bill_number = str(int(bill_number))
#             if not bill_number:
#                 continue

            invoice_number = row[col_map['sinvremark']].value
            if isinstance(invoice_number, float):
                invoice_number = str(int(invoice_number))
#             if not invoice_number:
#                 continue

            PInvoiceDate = row[col_map['pinvoicedate']].value
#             if PInvoiceDate != 'NULL':
#                 PInvoiceDate = datetime.strftime(datetime.strptime(PInvoiceDate, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 invoice_data['venice_porderdate'] = PInvoiceDate
#                 bill_data['venice_porderdate'] = PInvoiceDate
            pinvoice_year = ''
            if PInvoiceDate != 'NULL':
                PInvoiceDate = xlrd.xldate_as_tuple(PInvoiceDate, book.datemode)
                pinvoice_year = str(PInvoiceDate[0])
                PInvoiceDate = str(PInvoiceDate[2]) + '-' + str(PInvoiceDate[1]) + '-' + str(PInvoiceDate[0])
                PInvoiceDate = parse(PInvoiceDate, dayfirst=True)
                PInvoiceDate = datetime.strftime(PInvoiceDate, DEFAULT_SERVER_DATE_FORMAT)

            fiscal_year = row[col_map['sinvoiceaccyear']].value
            if isinstance(fiscal_year, float):
                fiscal_year = str(int(fiscal_year))

#             fiscal_year = str(int(row[col_map['SInvoiceAccYear']].value))
            if not fiscal_year or fiscal_year == '0':
                if pinvoice_year:
                    fiscal_year = pinvoice_year

            bill_doc_number = str(int(row[col_map['pinvoicedocnum']].value))
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

            inv_doc_number = row[col_map['sinvoicedocnum']].value
            if isinstance(inv_doc_number, float):
                inv_doc_number = str(int(inv_doc_number))

#             inv_doc_number = str(int(row[col_map['SInvoiceDocNum']].value))
            if inv_doc_number and len(inv_doc_number) < 5:
                prefix = 5 - len(inv_doc_number)
                if prefix == 1:
                    add = '0'
                elif prefix == 2:
                    add = '00'
                elif prefix == 3:
                    add = '000'
                else:
                    add = '0000'
                inv_doc_number = add + inv_doc_number 
            inv_name = fiscal_year + '-' + inv_doc_number

            VatSystemDsc = row[col_map['pinvvatsystemdsc']].value.strip()
            fiscal_position = False
            imd = self.env['ir.model.data']
            country = row[col_map['repcountry']].value
            venice_system = False
            if country == 'SDT.BE':
                venice_system = 'Belgium'
                customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == 'Belgium'])
            elif country == 'SDT.NL':
                venice_system = 'Netherlands'
                customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == 'Netherlands'])
            else:
                customer_map = dict([(customer.venice_nummer, customer.id) for customer in partner_ids if customer.venice_system == False])
            if VatSystemDsc == 'Europese Unie':
                if country == 'SDT.BE':
                    fiscal_position = imd.xmlid_to_res_id('l10n_be.1_fiscal_position_template_3')
                if country == 'SDT.NL':
                    fiscal_position = imd.xmlid_to_res_id('l10n_nl.3_fiscal_position_template_eu')
            if VatSystemDsc == 'Binnenland normaal':
                if country == 'SDT.BE':
                    fiscal_position = imd.xmlid_to_res_id('l10n_be.1_fiscal_position_template_1')
                if country == 'SDT.NL':
                    fiscal_position = imd.xmlid_to_res_id('l10n_nl.3_fiscal_position_template_national')

            invoice_data = {
                'name' : inv_name,
                'journal_id' : self.invoice_journal_id.id,
                'company_id': self.company_id.id,
#                 'date_invoice' : inv_date_invoice,
#                 'date_due' : inv_date_due,
                'venice_docnum' : inv_doc_number,
                'fiscal_position_id': fiscal_position,
                'type': 'out_invoice',
                'reference': invoice_number,
                'venice_pinvoicebook': PInvoiceBook,
                'venice_sinvoicebook': SInvoiceBook,
                'venice_sorderdocnumber': SorderDocNumber,
#                 'venice_sorderdate': SOrderDate,
                'venice_sorderaccyear': SOrderAccYear,
                'venice_sorddocamountvatex': SOrdDocAmountVatEx,
                'so_name': so_name,
                'venice_porderdocnumber': POrderDocNumber,
#                 'venice_porderdate': POrderDate,
                'venice_porderaccyear': POrderAccYear,
                'venice_porderamountvatex': POrderAmountVatEx,
                'po_name': po_name,
                'venice_suppname': SuppName,
                'venice_pinvoicedocnum': PInvoiceDocNum,
                'venice_pinvoiceamount': PInvoiceAmount,
                'venice_pinvremark': PInvRemark,
                'venice_sinvoicedocnumber': SInvoiceDocNum,
                'venice_pinvvatsystemdsc': VatSystemDsc,
#                 'venice_sinvoicedate': SInvoiceDate,
                'venice_sinvoiceaccyear': fiscal_year,
                'venice_sinvoiceamountvatex': SInvoiceAmountVatEx,
                'inv_name': inv_name,
                'venice_sinvoiceamount': SInvoiceAmount,
#                 'venice_sinvexpirationdate': SInvExpirationDate,
                'clientfiscalposition': fiscal_position and self.env['account.fiscal.position'].browse(fiscal_position).name or '',
                'venice_customername': CustomerName,
                'venice_customernumber': CustomerNumber,
                'venice_customersubnumber': CustomerSubNumber,
                'venice_sinvremark': SInvRemark,
                'venice_deliveryname': DeliveryName,
                'venice_deliverynumber': DeliveryNumber,
                'venice_deliverysubnumber': DeliverySubNumber,
                'dropshipping': True if SorderDocNumber != '0' else False,
                'import_wizard': True,
            }

            bill_data = {
                'name' : bill_name,
                'journal_id' : self.bill_journal_id.id,
                'company_id': self.company_id.id,
#                 'date_invoice' : bill_date_invoice,
#                 'date_due' : bill_date_due,
                'venice_docnum' : bill_doc_number,
                'fiscal_position_id': fiscal_position,
                'type': 'in_invoice',
                'reference': bill_number,
                'venice_pinvoicebook': PInvoiceBook,
                'venice_sinvoicebook': SInvoiceBook,
                'venice_sorderdocnumber': SorderDocNumber,
#                 'venice_sorderdate': SOrderDate,
                'venice_sorderaccyear': SOrderAccYear,
                'venice_sorddocamountvatex': SOrdDocAmountVatEx,
                'so_name': so_name,
                'venice_porderdocnumber': POrderDocNumber,
#                 'venice_porderdate': POrderDate,
                'venice_porderaccyear': POrderAccYear,
                'venice_porderamountvatex': POrderAmountVatEx,
                'po_name': po_name,
                'venice_suppname': SuppName,
                'venice_pinvoicedocnum': PInvoiceDocNum,
                'venice_pinvoiceamount': PInvoiceAmount,
                'venice_pinvremark': PInvRemark,
                'venice_sinvoicedocnumber': SInvoiceDocNum,
                'venice_pinvvatsystemdsc': VatSystemDsc,
#                 'venice_sinvoicedate': SInvoiceDate,
                'venice_sinvoiceaccyear': fiscal_year,
                'venice_sinvoiceamountvatex': SInvoiceAmountVatEx,
                'inv_name': inv_name,
                'venice_sinvoiceamount': SInvoiceAmount,
#                 'venice_sinvexpirationdate': SInvExpirationDate,
                'clientfiscalposition': fiscal_position and self.env['account.fiscal.position'].browse(fiscal_position).name or '',
                'venice_customername': CustomerName,
                'venice_customernumber': CustomerNumber,
                'venice_customersubnumber': CustomerSubNumber,
                'venice_sinvremark': SInvRemark,
                'venice_deliveryname': DeliveryName,
                'venice_deliverynumber': DeliveryNumber,
                'venice_deliverysubnumber': DeliverySubNumber,
                'dropshipping': True if SorderDocNumber != '0' else False,
                'import_wizard': True,
            }

            SOrderDate = row[col_map['sorderdate']].value
#             if SOrderDate != 'NULL':
#                 SOrderDate = datetime.strftime(datetime.strptime(SOrderDate, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 invoice_data['venice_sorderdate'] = SOrderDate
#                 bill_data['venice_sorderdate'] = SOrderDate
            if SOrderDate != 'NULL':
                SOrderDate = xlrd.xldate_as_tuple(SOrderDate, book.datemode)
                SOrderDate = str(SOrderDate[2]) + '-' + str(SOrderDate[1]) + '-' + str(SOrderDate[0])
                SOrderDate = parse(SOrderDate, dayfirst=True)
                SOrderDate = datetime.strftime(SOrderDate, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['venice_sorderdate'] = SOrderDate
                bill_data['venice_sorderdate'] = SOrderDate

            POrderDate = row[col_map['porderdate']].value
#             if POrderDate != 'NULL':
#                 POrderDate = datetime.strftime(datetime.strptime(POrderDate, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 invoice_data['venice_porderdate'] = POrderDate
#                 bill_data['venice_porderdate'] = POrderDate
            if POrderDate != 'NULL':
                POrderDate = xlrd.xldate_as_tuple(POrderDate, book.datemode)
                POrderDate = str(POrderDate[2]) + '-' + str(POrderDate[1]) + '-' + str(POrderDate[0])
                POrderDate = parse(POrderDate, dayfirst=True)
                POrderDate = datetime.strftime(POrderDate, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['venice_porderdate'] = POrderDate
                bill_data['venice_porderdate'] = POrderDate

            if PInvoiceDate != 'NULL':
                invoice_data['venice_pinvoicedate'] = PInvoiceDate
                bill_data['venice_pinvoicedate'] = PInvoiceDate
                invoice_data['venice_pinvoiceaccyear'] = pinvoice_year
                bill_data['venice_pinvoiceaccyear'] = pinvoice_year

            PInvExpirationDate = row[col_map['pinvexpirationdate']].value
#             if PInvExpirationDate != 'NULL':
#                 PInvExpirationDate = datetime.strftime(datetime.strptime(PInvExpirationDate, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 invoice_data['venice_sinvexpirationdate'] = PInvExpirationDate
#                 bill_data['venice_sinvexpirationdate'] = PInvExpirationDate
            if PInvExpirationDate != 'NULL':
                PInvExpirationDate = xlrd.xldate_as_tuple(PInvExpirationDate, book.datemode)
                PInvExpirationDate = str(PInvExpirationDate[2]) + '-' + str(PInvExpirationDate[1]) + '-' + str(PInvExpirationDate[0])
                PInvExpirationDate = parse(PInvExpirationDate, dayfirst=True)
                PInvExpirationDate = datetime.strftime(PInvExpirationDate, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['venice_pinvexpirationDate'] = PInvExpirationDate
                bill_data['venice_pinvexpirationDate'] = PInvExpirationDate

            SInvoiceDate = row[col_map['sinvoicedate']].value
#             if SInvoiceDate != 'NULL':
#                 SInvoiceDate = datetime.strftime(datetime.strptime(SInvoiceDate, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 invoice_data['venice_sinvoicedate'] = SInvoiceDate
#                 bill_data['venice_sinvoicedate'] = SInvoiceDate
            if SInvoiceDate != 'NULL':
                SInvoiceDate = xlrd.xldate_as_tuple(SInvoiceDate, book.datemode)
                SInvoiceDate = str(SInvoiceDate[2]) + '-' + str(SInvoiceDate[1]) + '-' + str(SInvoiceDate[0])
                SInvoiceDate = parse(SInvoiceDate, dayfirst=True)
                SInvoiceDate = datetime.strftime(SInvoiceDate, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['venice_sinvoicedate'] = SInvoiceDate
                bill_data['venice_sinvoicedate'] = SInvoiceDate

            SInvExpirationDate = row[col_map['sinvexpirationdate']].value
#             if SInvExpirationDate != 'NULL':
#                 SInvExpirationDate = datetime.strftime(datetime.strptime(SInvExpirationDate, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 invoice_data['venice_sinvexpirationdate'] = SInvExpirationDate
#                 bill_data['venice_sinvexpirationdate'] = SInvExpirationDate
            if SInvExpirationDate != 'NULL':
                SInvExpirationDate = xlrd.xldate_as_tuple(SInvExpirationDate, book.datemode)
                SInvExpirationDate = str(SInvExpirationDate[2]) + '-' + str(SInvExpirationDate[1]) + '-' + str(SInvExpirationDate[0])
                SInvExpirationDate = parse(SInvExpirationDate, dayfirst=True)
                SInvExpirationDate = datetime.strftime(SInvExpirationDate, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['venice_sinvexpirationdate'] = SInvExpirationDate
                bill_data['venice_sinvexpirationdate'] = SInvExpirationDate

            bill_date_invoice = row[col_map['pinvoicedate']].value
            inv_date_invoice = row[col_map['sinvoicedate']].value

            bill_date_due = row[col_map['pinvexpirationdate']].value
            inv_date_due = row[col_map['sinvexpirationdate']].value
#             if bill_date_invoice != 'NULL':
#                 bill_date_invoice = datetime.strftime(datetime.strptime(bill_date_invoice, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 bill_data['date_invoice'] = bill_date_invoice
            if bill_date_invoice != 'NULL':
                bill_date_invoice = xlrd.xldate_as_tuple(bill_date_invoice, book.datemode)
                bill_date_invoice = str(bill_date_invoice[2]) + '-' + str(bill_date_invoice[1]) + '-' + str(bill_date_invoice[0])
                bill_date_invoice = parse(bill_date_invoice, dayfirst=True)
                bill_date_invoice = datetime.strftime(bill_date_invoice, DEFAULT_SERVER_DATE_FORMAT)
                bill_data['date_invoice'] = bill_date_invoice


#             if inv_date_invoice != 'NULL':
#                 inv_date_invoice = datetime.strftime(datetime.strptime(inv_date_invoice, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 invoice_data['date_invoice'] = inv_date_invoice
            if inv_date_invoice != 'NULL':
                inv_date_invoice = xlrd.xldate_as_tuple(inv_date_invoice, book.datemode)
                inv_date_invoice = str(inv_date_invoice[2]) + '-' + str(inv_date_invoice[1]) + '-' + str(inv_date_invoice[0])
                inv_date_invoice = parse(inv_date_invoice, dayfirst=True)
                inv_date_invoice = datetime.strftime(inv_date_invoice, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['date_invoice'] = inv_date_invoice


#             if bill_date_due != 'NULL':
#                 bill_date_due = datetime.strftime(datetime.strptime(bill_date_due, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 bill_data['date_due'] = bill_date_due
            if bill_date_due != 'NULL':
                bill_date_due = xlrd.xldate_as_tuple(bill_date_due, book.datemode)
                bill_date_due = str(bill_date_due[2]) + '-' + str(bill_date_due[1]) + '-' + str(bill_date_due[0])
                bill_date_due = parse(bill_date_due, dayfirst=True)
                bill_date_due = datetime.strftime(bill_date_due, DEFAULT_SERVER_DATE_FORMAT)
                bill_data['date_due'] = bill_date_due


#             if inv_date_due != 'NULL':
#                 inv_date_due = datetime.strftime(datetime.strptime(inv_date_due, '%Y-%m-%d'), DEFAULT_SERVER_DATE_FORMAT)
#                 invoice_data['date_due'] = inv_date_due
            if inv_date_due != 'NULL':
                inv_date_due = xlrd.xldate_as_tuple(inv_date_due, book.datemode)
                inv_date_due = str(inv_date_due[2]) + '-' + str(inv_date_due[1]) + '-' + str(inv_date_due[0])
                inv_date_due = parse(inv_date_due, dayfirst=True)
                inv_date_due = datetime.strftime(inv_date_due, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['date_due'] = inv_date_due


            if 'suppnum' in col_map:
                vendornumber = str(int(row[col_map['suppnum']].value))
                if vendornumber != '0':
                    if vendornumber and vendornumber not in vendor_map:
                        raise UserError(_('No vendor found with SupNum  %s.') % (vendornumber))
                    else:
                        vendor_map[vendornumber] = partner_pool.search([('venice_supnum','=',vendornumber)]).id
                    bill_data['partner_id'] = vendor_map[vendornumber]
                    bill_data['venice_suppnum'] = vendornumber
                    invoice_data['venice_suppnum'] = vendornumber

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
                if country == 'SDT.BE' or company_code == 'BE':
                    product_id = product_pool.search([('ds_ref_be','=',product_internal_ref)])
                if country == 'SDT.DE' or company_code == 'DE':
                    product_id = product_pool.search([('ds_ref_de','=',product_internal_ref)])
                if country == 'SDT.NL' or company_code == 'NL':
                    product_id = product_pool.search([('ds_ref_nl','=',product_internal_ref)])
                if country == 'SDT.FR' or company_code == 'FR':
                    product_id = product_pool.search([('ds_ref_fr','=',product_internal_ref)])
                if not product_id:
                    raise UserError(_('No Product found with reference  %s.') % (product_internal_ref))
            if SInvoiceBook == 'VER':
                if 'customernumber' in col_map:
                    customernumber = str(int(row[col_map['customernumber']].value))
                    customer_name = row[col_map['customername']].value
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
                invoice_id = invoice_pool.search([('name','=',inv_name),('type','=','out_invoice')])
                if invoice_id:
                    invoice_id.write(invoice_data)
                    inv_update_count += 1 
                else:
                    invoice_id = invoice_pool.create(invoice_data)
                    inv_create_count += 1

                sale_price_unit = row[col_map['sinvoiceamountvatex']].value
                customer_invoice_line_data = {
                    'quantity': 1,
                    'price_unit': sale_price_unit,
                    'invoice_id': invoice_id.id,
                    'account_id': self.invoice_journal_id.default_debit_account_id.id,
                    'name': 'import'
                }
                if vendornumber == '0':
                    customer_invoice_line_data['name'] = 'Various Invoice'
#                     customer_invoice_line_data['account_id'] = self.invoice_journal_id.default_debit_account_id.id
                else:
                    customer_invoice_line_data['product_id'] = product_id.id
#                     customer_invoice_line_data['account_id'] = product_id.property_account_income_id.id
                if vendornumber == '0':
                    inv_line_ids = self.env['account.invoice.line'].search([('name','=','Various Invoice'),('invoice_id','=',invoice_id.id)])
                else:
                    inv_line_ids = self.env['account.invoice.line'].search([('product_id','=',product_id.id),('invoice_id','=',invoice_id.id)])
                if inv_line_ids:
                    inv_line_ids[0].write(customer_invoice_line_data)
                    if vendornumber != '0':
                        inv_line_ids[0]._onchange_product_id()
                    inv_line_ids[0].write({'price_unit': sale_price_unit})
                else:
                    customer_invoice_line = self.env['account.invoice.line'].create(customer_invoice_line_data)
                    if vendornumber == '0':
                        customer_invoice_line._onchange_product_id()
                    customer_invoice_line.write({'price_unit': sale_price_unit})
                invoice_id._onchange_invoice_line_ids()

            if PInvoiceBook == 'AAN':
                bill_id = invoice_pool.search([('name','=',bill_name),('type','=','in_invoice')])
                if bill_id:
                    bill_id.write(bill_data)
                    bill_update_count += 1
                else:
                    print ("Bill Data", bill_data)
                    bill_id = invoice_pool.create(bill_data)
                    bill_create_count += 1

                purchase_price_unit = row[col_map['pinvoiceamount']].value
                supplier_invoice_line_data = {
                    'product_id': product_id.id,
                    'quantity': 1,
                    'price_unit': purchase_price_unit,
                    'invoice_id': bill_id.id,
#                     'account_id': product_id.property_account_expense_id.id,
                    'account_id': self.bill_journal_id.default_credit_account_id.id,
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
                        \nNumber of New Customer Created      : %s\
                        \nNumber of Invoice Created          : %s\
                        \nNumber of Invoice Updated        : %s")%(count-1,
                                                                   bill_create_count,
                                                                   bill_update_count,
                                                                   customer_count,
                                                                   inv_create_count,
                                                                   inv_update_count)
        import_id = self.env['import.vendor.bills'].create({'import_warning': Warning_msg,
                                                            'warning': True})

        return {
            'name': 'Import Vendor Bills',
            'view_mode': 'form',
            'res_id': import_id.id,
            'res_model': 'import.vendor.bills',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
