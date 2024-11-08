# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api
from openerp.exceptions import except_orm
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import base64
try:
    from itertools import imap
except ImportError:
    # Python 3...
    imap=map
import xlrd
from xlrd import open_workbook
from datetime import datetime, timedelta
from dateutil.parser import parse

import logging
# from boto.mashups import order

_logger = logging.getLogger(__name__)


class ImportInv05(models.TransientModel):
    _name = 'import.inv05'
    _description = 'Import INV05'

    file = fields.Binary('File')
    import_warning = fields.Text('Import Summary', readonly='1')

    @api.multi
    def do_import_inv05(self):

        customer_pool = self.env['res.partner']
        invoice_pool = self.env['account.invoice']
        journal_pool = self.env['account.journal']

        book = open_workbook(file_contents=base64.decodestring(self.file))
        sheet = book.sheet_by_index(0)

        customer_ids = customer_pool.search([])
        customer_map = dict([(c.ppc_customernumber, c.id) for c in customer_ids])

        skip_rows = 1
        col_map = {}

        log_map = []
        count = 0
        create_count = 0
        update_count = 0
        for row in imap(sheet.row, range(sheet.nrows)):
            if count == 0:
                col_index = 0
                for col in row:
                    col_map[col.value.replace(" ", "").lower()] = col_index
                    col_index += 1
                if 'customernumber' not in col_map:
                    raise except_orm('No customer number column found', 'Please upload valid file with customer number column in first row')
            invoice_number = row[col_map['invoicenumber']].value.strip()
            if not invoice_number:
                continue

            customernumber = row[col_map['customernumber']].value
#             if not customernumber:
#                 continue

            count += 1
            if count <= skip_rows:
                continue

# Ordering Date    Customer Order    Vendor Order    Customer (Surname)    Customer (First name)    Title    Email    
#     Company    Payment Type    Ordering State    Invoice Number    Invoice Date    Coupon Code    Coupon Value    
# Net Value of Articles    Net Shipment    Rebate    Net Total    VAT    Gross Total    Sales Channel    Agio Payment Provider    
# Paid on    Expected Gross    Payment Provider    Payment Provider TX ID    RefChannel    RefChannel Name    RefChannel Category
# Customer Number

            journal_id = journal_pool.search([('code','=','S5DE')])
            if not journal_id:
                raise except_orm('Journal Not Found!', 'No journal found with sort code INV05')

            customer_order = row[col_map['customerorder']].value.strip()
            vendor_order = row[col_map['vendororder']].value.strip()
            customer_surname = row[col_map['customer(surname)']].value.strip()
            customer_firstname = row[col_map['customer(firstname)']].value.strip()
            title = row[col_map['title']].value.strip()
            email = row[col_map['email']].value.strip()
            company = row[col_map['company']].value.strip()
            payment_type = row[col_map['paymenttype']].value.strip()
            ordering_state = row[col_map['orderingstate']].value.strip()
#             invoice_number = row[col_map['InvoiceNumber']].value.strip()
            name = row[col_map['invoicenumber']].value.strip()

            coupon_code = row[col_map['couponcode']].value.strip()
            coupon_value = row[col_map['couponvalue']].value.strip()
            netvalueofarticles = row[col_map['netvalueofarticles']].value
            if netvalueofarticles:
                netvalueofarticles = float(row[col_map['netvalueofarticles']].value)
            net_shipment = row[col_map['netshipment']].value
            if net_shipment:
                net_shipment = float(row[col_map['netshipment']].value)
            rebate = row[col_map['rebate']].value
            if rebate:
                rebate = float(row[col_map['rebate']].value)
            net_total = row[col_map['nettotal']].value
            if net_total:
                net_total = float(row[col_map['nettotal']].value)
            vat = row[col_map['vat']].value
            if vat:
                vat = float(row[col_map['vat']].value)
            grosstotal = row[col_map['grosstotal']].value
            if grosstotal:
                grosstotal = float(row[col_map['grosstotal']].value)
            agio_payment_provider = row[col_map['agiopaymentprovider']].value
            if agio_payment_provider:
                agio_payment_provider = float(row[col_map['agiopaymentprovider']].value)
            expected_gross = row[col_map['expectedgross']].value
            if expected_gross:
                expected_gross = float(row[col_map['expectedgross']].value)
            sales_channel = row[col_map['saleschannel']].value.strip()

            payment_provider = row[col_map['paymentprovider']].value.strip()
            payment_provider_tx_id = row[col_map['paymentprovidertxid']].value.strip()
            refchannel = row[col_map['refchannel']].value.strip()
            refchannel_name = row[col_map['refchannelname']].value.strip()
            refchannel_category = row[col_map['refchannelcategory']].value.strip()
            invoice_data = {
#                 'ppc_orderingdate' : ordering_date,
                'ppc_customerorder' : customer_order,
                'ppc_vendororde' : vendor_order,
                'ppc_customersurname' : customer_surname,
                'ppc_customerfirstname' : customer_firstname,
                'ppc_title' : title,
                'ppc_email' : email,
                'ppc_company' : company,
                'ppc_paymenttype' : payment_type,
                'ppc_orderingstate' : ordering_state,
                'ppc_invoicenumber' : invoice_number,
                'name' : name,
                'journal_id' : journal_id.id,
#                 'ppc_invoicedate' : invoice_date,
#                 'date_invoice' : invoice_date,
                'ppc_couponcode' : coupon_code,
                'ppc_couponvalue' : coupon_value,
                'ppc_netvalueofarticles' : netvalueofarticles,
                'ppc_netshipment' : net_shipment,
                'ppc_rebate' : rebate,
                'ppc_nettotal' : net_total,
                'ppc_vat' : vat,
                'ppc_grosstotal' : grosstotal,
                'ppc_agiopaymentprovider' : agio_payment_provider,
#                 'ppc_paidon' : paid_on,
                'ppc_expectedgross' : expected_gross,
                'ppc_paymentprovider' : payment_provider,
                'ps_paymentprovidertxid' : payment_provider_tx_id,
                'state': 'imported',
                'ppc_user_imported': True,
                'import_wizard': True,
            }

            ordering_date = row[col_map['orderingdate']].value
            if ordering_date:
                ordering_date = xlrd.xldate_as_tuple(ordering_date, book.datemode)
                ordering_date = str(ordering_date[2]) + '-' + str(ordering_date[1]) + '-' + str(ordering_date[0])
                ordering_date = parse(ordering_date, dayfirst=True)
                ordering_date = datetime.strftime(ordering_date, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['ppc_orderingdate'] = ordering_date

            invoice_date = row[col_map['invoicedate']].value
            if invoice_date:
                invoice_date = xlrd.xldate_as_tuple(invoice_date, book.datemode)
                invoice_date = str(invoice_date[2]) + '-' + str(invoice_date[1]) + '-' + str(invoice_date[0])
                invoice_date = parse(invoice_date, dayfirst=True)
                invoice_date = datetime.strftime(invoice_date, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['ppc_invoicedate'] = invoice_date
                invoice_data['date_invoice'] = invoice_date

            paid_on = row[col_map['paidon']].value
            #Replace all blank date field in sheet with NULL to make it working fine
            if paid_on:
                paid_on = xlrd.xldate_as_tuple(paid_on, book.datemode)
                paid_on = str(paid_on[2]) + '-' + str(paid_on[1]) + '-' + str(paid_on[0])
                paid_on = parse(paid_on, dayfirst=True)
#                 paid_on = parse(paid_on, dayfirst=True)
                paid_on = datetime.strftime(paid_on, DEFAULT_SERVER_DATE_FORMAT)
                invoice_data['ppc_paidon'] = paid_on

            if customernumber not in customer_map:
                name = customer_firstname + ' ' + customer_surname
                company_type = 'person'
                if not customernumber:
                    name = company
                    company_type = 'company'
                customer_id = customer_pool.create({'name': name,
                                                                     'ppc_name' : name,
                                                                     'ppc_vorname' : customer_surname,
                                                                     'ppc_nachname' : customer_firstname,
                                                                     'ppc_anrede' : title,
                                                                     'ppc_email' : email,
                                                                     'email' : email,
                                                                     'ppc_company' : company,
                                                                     'ppc_customernumber' : customernumber,
                                                                     'sdt_section' : 'papersmart',
                                                                     'company_type': company_type
                                                                     })
                customer_map[customernumber] = customer_id.id
                customer_ids |= customer_id
            else:
                customer_map[customernumber] = customer_pool.search([('ppc_customernumber','=',customernumber)]).id

            invoice_data['partner_id'] = customer_map[customernumber]
            invoice_data['ppc_customernumber'] = customernumber

            if invoice_number not in log_map:
                self._cr.execute("SELECT ppc_invoicenumber, id from account_invoice WHERE ppc_invoicenumber='%s'" %invoice_number)
                for rec in self._cr.dictfetchall():
                    log_map.append(rec['ppc_invoicenumber'])
            if invoice_number not in log_map:
                invoice_id = invoice_pool.create(invoice_data)
                create_count += 1
                log_map.append(invoice_id.ppc_invoicenumber)
            else:
                invoice_record = invoice_pool.search([('ppc_invoicenumber','=',invoice_number)])
                invoice_record.write(invoice_data)
                update_count += 1

            if count % 100 == 0:
                _logger.info(count)
                self._cr.commit()

        Warning_msg = ("All Lines imported successfully.\nTotal Lines in xlsx File: %s\nNew Lines                  : %s\nUpdated Lines            : %s")%(count-1, create_count, update_count)
        import_id = self.env['import.inv05'].create({'import_warning': Warning_msg, 'warning': True})

        return {
            'name': 'INV05 Import',
            'view_mode': 'form',
            'res_id': import_id.id,
            'res_model': 'import.inv05',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
