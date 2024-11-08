# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime
import tempfile
import binascii
from datetime import date, datetime
from odoo.exceptions import Warning, UserError
from odoo import models, fields, exceptions, api, _
import logging
_logger = logging.getLogger(__name__)
import io
try:
	import xlrd
except ImportError:
	_logger.debug('Cannot `import xlrd`.')
try:
	import csv
except ImportError:
	_logger.debug('Cannot `import csv`.')
try:
	import xlwt
except ImportError:
	_logger.debug('Cannot `import xlwt`.')
try:
	import cStringIO
except ImportError:
	_logger.debug('Cannot `import cStringIO`.')
try:
	import base64
except ImportError:
	_logger.debug('Cannot `import base64`.')

class ImportMarketAmazon(models.TransientModel):
	_name = "import.market.amazon"
	_description = "Import Market Amazon"

	file_select = fields.Binary(string="Select CSV File")
	name = fields.Char(string='Name of Import')

	
	def import_file(self):

		try:
			csv_data = base64.b64decode(self.file_select)
			data_file = io.StringIO(csv_data.decode("utf-8"))
			data_file.seek(0)
			file_reader = []
			values = {}
			csv_reader = csv.reader(data_file, delimiter=',')
			file_reader.extend(csv_reader)

		except:

			raise UserError(_("Invalid file!"))

		for i in range(len(file_reader)):
			field = list(map(str, file_reader[i]))
			values = {}
			if i == 0:
				continue
			else:
				values.update({
								'marketplace_id' : field[0],
								'merchant_id' : field[1],
								'order_date' : field[2],
								'transaction_type'  : field[3],
								'is_invoice_corrected' : field[4],
								'order_id': field[5],
								'shipment_date' :field[6],
								'shipment_id' :field[7],
								'transaction_id' :field[8],
								'asin' :field[9],
								'sku' :field[10],
								'quantity' :field[11],
								'tax_calculation_date' :field[12],
								'tax_rate' :field[13],
								'product_tax_code' :field[14],
								'currency' :field[15],
								'tax_type' :field[16],

								'tax_calculation_reason_code' :field[17],
								'tax_reporting_scheme' :field[18],
								'tax_collection_responsibility' :field[19],
								'tax_address_role' :field[20],
								'jurisdiction_level' :field[21],
								'jurisdiction_name' :field[22],

								'our_price_tax_inc_selling_price' :field[23],
								'our_price_tax_amount' :field[24],
								'our_price_tax_exc_selling_price' :field[25],
								'our_price_tax_inc_promo_amount' :field[26],
								'our_price_tax_amount_promo' :field[27],
								'our_price_tax_exc_promo_amount' :field[28],

								'shipping_tax_inc_selling_price' :field[29],
								'shipping_tax_amount' :field[30],
								'shipping_tax_exc_selling_price' :field[31],
								'shipping_tax_inc_promo_amount' :field[32],
								'shipping_tax_amount_promo' :field[33],
								'shipping_tax_exc_promo_amount' :field[34],
								'giftwrap_tax_inc_selling_price' :field[35],
								'giftwrap_tax_amount' :field[36],
								'giftwrap_tax_exc_selling_price' :field[37],
								'giftwrap_tax_inc_promo_amount' :field[38],
								'giftwrap_tax_amount_promo' :field[39],
								'giftwrap_tax_exc_promo_amount' :field[40],

								'seller_tax_registration' :field[41],
								'seller_tax_registration_jurisdiction' :field[42],
								'buyer_tax_registration' :field[43],
								'buyer_tax_registration_jurisdiction' :field[44],
								'buyer_tax_tegistration_type' :field[45],
								'buyer_envoice_account_id' :field[46],
								'invoice_level_currency_code' :field[47],
								'invoice_level_exchange_rate' :field[48],
								'invoice_level_exchange_rate_date' :field[49],
								'converted_tax_amount' :field[50],
								'vat_invoice_number' :field[51],

								'invoice_url' :field[52],
								'export_outside_eu' : field[53],
								'ship_from_city' :field[54],
								'ship_from_state' :field[55],
								'ship_from_country' :field[56],
								'ship_from_postal_code' :field[57],
								'ship_from_tax_location_code' :field[58],
								#PSI: Temp deactivated import of these 2 columns as data is with garbage character
								# 'ship_to_city' :field[59],
								# 'ship_to_state' :field[60],
								'ship_to_country' :field[61],
								'ship_to_postal_code' :field[62],

								'ship_to_location_code' :field[63],
								'return_fc_country' :field[64],
								'is_amazon_invoiced' :field[65],
								'original_vat_invoice_number' :field[66],
								'invoice_correction_details' :field[67],
								'sdi_invoice_delivery_status' :field[68],
								'sdi_invoice_error_code' :field[69],
								'sdi_invoice_error_description' :field[70],
								'sdi_invoice_status_last_updated_date' :field[71],
								'einvoice_url' :field[72],
								'record_created_from': self.name,
								})
				res = self.env['market.amazon'].create(values)
		return res
