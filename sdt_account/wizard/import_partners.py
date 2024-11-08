# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import models, fields, api
from openerp.exceptions import except_orm
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import base64
import itertools
from xlrd import open_workbook

import logging
# from boto.mashups import order

_logger = logging.getLogger(__name__)


class ImportPartners(models.TransientModel):
    _name = 'import.partners'
    _description = 'Import Partners'

    file = fields.Binary('File')
    import_warning = fields.Text('Import Summary', readonly='1')

    @api.multi
    def do_import_partners(self):

        customer_pool = self.env['res.partner']

        book = open_workbook(file_contents=base64.decodestring(self.file))
        sheet = book.sheet_by_index(0)

#         customer_ids = customer_pool.search([])
#         customer_map = dict([(c.ppc_customernumber, c.id) for c in customer_ids])

        skip_rows = 1
        col_map = {}

        log_map = []
        count = 0
        create_count = 0
        update_count = 0
        for row in itertools.imap(sheet.row, range(sheet.nrows)):
            if count == 0:
                col_index = 0
                for col in row:
                    col_map[col.value.replace(" ", "").lower()] = col_index
                    col_index += 1
                if 'customerid' not in col_map:
                    raise except_orm('No customer id column found', 'Please upload valid file with customer id column in first row')

            count += 1
            if count <= skip_rows:
                continue

# Customer id    Created at    Updated at    Last sign in at    Email    Anrede    Vorname    Nachname    Name
# Newsletter subscription    Last shopping cart reminder at    Prefered payment type    Cc last digits    Cc expiry
# Credit limt    Tax choice    Business customer?    Private customer?    Company name    Billing address name
# Billing address company    Billing address street    Billing address city    Billing address zip    Billing address country
# Billing address phone    Billing address registration number    Billing address tax number    RefChannel    RefChannel Name
# RefChannel Category
            last_signin = row[col_map['lastsigninat']].value
            if not last_signin or '2018' not in last_signin:
                continue
            customer_number = row[col_map['customerid']].value
            if not customer_number:
                continue
            creation = row[col_map['createdat']].value
            update = row[col_map['updatedat']].value
            email = row[col_map['email']].value.strip()
            title = row[col_map['anrede']].value.strip()
            surname = row[col_map['vorname']].value.strip()
            first_name = row[col_map['nachname']].value.strip()
            full_name = row[col_map['name']].value.strip()
            newsletter = row[col_map['newslettersubscription']].value
            if newsletter == 'true':
                newsletter = True
            else:
                newsletter = False
            last_shopping = row[col_map['lastshoppingcartreminderat']].value
            payment_type = row[col_map['preferedpaymenttype']].value.strip()
            cc_digits = row[col_map['cclastdigits']].value
            cc_expiry = row[col_map['ccexpiry']].value
            cc_limit = row[col_map['creditlimt']].value
            tax_choice = row[col_map['taxchoice']].value
            business = row[col_map['businesscustomer?']].value
            if business == 'true':
                business = True
            else:
                business = False
            private = row[col_map['privatecustomer?']].value
            if private == 'true':
                private = True
            else:
                private = False
            company = row[col_map['companyname']].value.strip()
            bill_name = row[col_map['billingaddressname']].value.strip()
            bill_company = row[col_map['billingaddresscompany']].value.strip()
            bill_street = row[col_map['billingaddressstreet']].value
            bill_city = row[col_map['billingaddresscity']].value.strip()
            bill_zip = row[col_map['billingaddresszip']].value  
            bill_country = row[col_map['billingaddresscountry']].value.strip()
            bill_phone = row[col_map['billingaddressphone']].value
            bill_registration_number = row[col_map['billingaddressregistrationnumber']].value.strip()
            bill_taxnumber = row[col_map['billingaddresstaxnumber']].value.strip()
#             vendor_order = row[col_map['refchannel']].value.strip()
#             vendor_order = row[col_map['refchannelname']].value.strip()
#             vendor_order = row[col_map['refchannelcategory']].value.strip()

            partner_data = {
                'ppc_user_imported': True,
                'name': full_name,
                'sdt_section' : 'papersmart',
                'ppc_created' : creation,
                'ppc_updated' : update,
                'ppc_lastsign' : last_signin,
                'ppc_name' : full_name,
                'ppc_vorname' : surname,
                'ppc_nachname' : first_name,
                'ppc_anrede' : title,
                'ppc_email' : email,
                'ppc_customernumber' : customer_number,
                'ppc_company' : company,
                'ppc_business' : business,
                'ppc_customer' : private,
                'ppc_bill_name' : bill_name,
                'ppc_bill_company' : bill_company,
                'ppc_bill_street' : bill_street,
                'ppc_bill_city' : bill_city,
                'ppc_bill_zip' : bill_zip,
                'ppc_bill_country' : bill_country,
                'ppc_bill_phone' : bill_phone,
                'ppc_bill_registrationnumber' : bill_registration_number,
                'ppc_bill_taxnumber' : bill_taxnumber,
                'ppc_tax_choice' : tax_choice,
                'ppc_newsletter' : newsletter,
                'ppc_lastshopping' : last_shopping,
                'ppc_paymenttype' : payment_type,
                'ppc_cc_digits' : cc_digits,
                'ppc_cc_expiry' : cc_expiry,
                'ppc_cc_limit' : cc_limit,
            }

            if customer_number not in log_map:
                customer_id = customer_pool.search([('ppc_customernumber','=',customer_number)])
#                 for rec in self._cr.dictfetchall():
                if customer_id:
                    log_map.append(customer_number)
            if customer_number not in log_map:
                customer_id = customer_pool.create(partner_data)
                create_count += 1
                log_map.append(customer_number)
            else:
                customer_id = customer_pool.search([('ppc_customernumber','=',customer_number)])
                customer_id.write(partner_data)
                update_count += 1

            if count % 100 == 0:
                _logger.info(count)
                self._cr.commit()

        Warning_msg = ("All Lines imported successfully.\nTotal Lines in xlsx File: %s\nNew Lines                  : %s\nUpdated Lines            : %s")%(count-1, create_count, update_count)
        import_id = self.env['import.partners'].create({'import_warning': Warning_msg, 'warning': True})

        return {
            'name': 'Import Partners',
            'view_mode': 'form',
            'res_id': import_id.id,
            'res_model': 'import.partners',
            'view_type': 'form',
            'type': 'ir.actions.act_window',
            'target': 'new'
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
