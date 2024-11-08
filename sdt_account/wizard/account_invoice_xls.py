# -*- coding: utf-8 -*-
# coding: utf-8

from odoo import models, api, fields, _
from odoo.exceptions import UserError
from io import BytesIO
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import base64
import xlsxwriter
import os
import tempfile

class AccountInvoiceExport(models.TransientModel):
	_name = 'account.invoice.export'
	_description = 'Account Invoice Export'

	filename = fields.Char('File Name', size=128, default="Report XLS")
	excel_file = fields.Binary('Download Excel File')
	fname = fields.Char('Report XLS', default = 'Report XLS')

	@api.multi
	def generate_report(self):
		active_ids = self._context.get('active_ids')
		invoice_ids = self.env['account.invoice'].browse(active_ids)
		fp = BytesIO()
		workbook = xlsxwriter.Workbook(fp)
		worksheet = workbook.add_worksheet('Invoice Details')

		company = self.env['res.users'].browse(self.env.uid).company_id
		if company.logo:
			filename = 'company_logo.png'
			image_data = BytesIO(base64.b64decode(company.logo))
			worksheet.insert_image('G1', filename, {'image_data': image_data, 'x_scale':3, 'y_scale': 3.5})

		company_heading = workbook.add_format({
			'bold' : 1,
			'font_size' : 15,
			'align' : 'left',
			'font_name' : 'Times New Roman',
		})
		name = workbook.add_format({
			'font_size' : 13,
			'align' : 'left',
			'font_name' : 'Times New Roman',
		})
		name1 = workbook.add_format({
			'bold' : 1,
			'font_size' : 13,
			'align' : 'left',
			'font_name' : 'Times New Roman',
		})
		name_head1 = workbook.add_format({
			'bold' : 1,
			'font_size' : 13,
			'bg_color' : '#909090',
			'align' : 'left',
			'font_name' : 'Times New Roman',
		})

		company_initials = company.name[0:2]
# - date_invoice
# - partner_id
# - reference
# - amount_untaxed
# - amount_tax
# - amount_total
# - statut
		row = 2
		col = 0
		
		worksheet.write(row, col, "Invoice Details :", name_head1)

		row += 2
		worksheet.set_column('A5:A5', len('Invoice Date')+1)
		worksheet.write(row, col, 'Invoice Date', name_head1)
		col += 1
		worksheet.set_column('B5:B5', len('Partner')+15)
		worksheet.write(row, col, 'Partner', name_head1)
		col += 1
		worksheet.set_column('C5:C5', len('Reference')+5)
		worksheet.write(row, col, 'Reference', name_head1)
		col += 1
		worksheet.set_column('D5:D5', len('Tax Excluded')+1)
		worksheet.write(row, col, 'Tax Excluded', name_head1)
		col += 1
		worksheet.set_column('E5:E5', len('Tax')+9)
		worksheet.write(row, col, 'Tax', name_head1)
		col += 1
		worksheet.set_column('F5:F5', len('Total')+7)
		worksheet.write(row, col, 'Total', name_head1)
		col += 1
		worksheet.set_column('G5:G5', len('Status')+3)
		worksheet.write(row, col, 'Status', name_head1)
# - fiscal_position_id
# - due_date
# - payment_term_id
# - vat_declaration
		col += 1
		worksheet.set_column('H5:H5', len('Fiscal Position')+3)
		worksheet.write(row, col, 'Fiscal Position', name_head1)
		col += 1
		worksheet.set_column('I5:I5', len('Due Date')+2)
		worksheet.write(row, col, 'Due Date', name_head1)
		col += 1
		worksheet.set_column('J5:J5', len('Payment Terms')+3)
		worksheet.write(row, col, 'Payment Terms', name_head1)
		col += 1
		worksheet.set_column('K5:K5', len('VAT Declaration')+3)
		worksheet.write(row, col, 'VAT Declaration', name_head1)
# - vat_period_id
# - bill_type
# - accounting_date
# - company_id
# - journal_id
# - user_id
# - analytic_product
		col += 1
		worksheet.set_column('M5:M5', len('VAT Period')+2)
		worksheet.write(row, col, 'VAT Period', name_head1)
		col += 1
		worksheet.set_column('N5:N5', len('BILL Type')+2)
		worksheet.write(row, col, 'BILL Type', name_head1)
		col += 1
		worksheet.set_column('O5:O5', len('Accounting Date')+5)
		worksheet.write(row, col, 'Accounting Date', name_head1)
		col += 1
		worksheet.set_column('P5:P5', 40)
		worksheet.write(row, col, 'Company', name_head1)
		col += 1
		worksheet.set_column('Q5:Q5', len('Journal')+10)
		worksheet.write(row, col, 'Journal', name_head1)
		col += 1
		worksheet.set_column('R5:R5', len('Salesperson')+5)
		worksheet.write(row, col, 'Salesperson', name_head1)
		col += 1
		worksheet.set_column('L5:L5', len('Analytic Product'))
		worksheet.write(row, col, 'Analytic Product', name_head1)
		row += 1
		total_untaxed = total_tax = total_amount = 0
		for invoice in invoice_ids:
# - date_invoice
# - partner_id
# - reference
# - amount_untaxed
# - amount_tax
# - amount_total
# - statut
			col = 0
			invoice_date = ''
			if invoice.date_invoice:
				invoice_date = datetime.strftime(invoice.date_invoice, "%m/%d/%Y")
			worksheet.write(row, col, invoice_date, name)
			col += 1
			worksheet.write(row, col, invoice.partner_id.name, name)
			col += 1
			worksheet.write(row, col, invoice.reference, name)
			col += 1
			worksheet.write(row, col, invoice.amount_untaxed, name)
			total_untaxed += invoice.amount_untaxed
			col += 1
			worksheet.write(row, col, invoice.amount_tax, name)
			total_tax += invoice.amount_tax
			col += 1
			worksheet.write(row, col, invoice.amount_total, name)
			total_amount += invoice.amount_total
			col += 1
			worksheet.write(row, col, invoice.state.capitalize(), name)
# - fiscal_position_id
# - due_date
# - payment_term_id
# - vat_declaration
			fiscal_position = invoice.fiscal_position_id and invoice.fiscal_position_id.name or ''
			col += 1
			worksheet.write(row, col, fiscal_position, name)
			col += 1
			due_date = ''
			if invoice.date_due:
				due_date = datetime.strftime(invoice.date_due, "%m/%d/%Y")
			worksheet.write(row, col, due_date, name)
			col += 1
			payment_term = invoice.payment_term_id and invoice.payment_term_id.name or ''
			worksheet.write(row, col, payment_term, name)
			col += 1
			vat_declaration = ''
			if invoice.vat_declaration == 'to_do':
				vat_declaration = 'To DO'
			else:
				vat_declaration = invoice.vat_declaration and invoice.vat_declaration.capitalize() or ''
			worksheet.write(row, col, vat_declaration, name)
# - vat_period_id
# - bill_type
# - accounting_date
# - company_id
# - journal_id
# - user_id
# - analytic_product
			col += 1
			vat_period = invoice.vat_period_id and invoice.vat_period_id.name or ''
			worksheet.write(row, col, vat_period, name)
			col += 1
			if invoice.bill_type == 'ic_acquisitions':
				bill_type = 'IC Acquisitions'
			if invoice.bill_type == 'purchased_services_eu':
				bill_type = 'Purchased Services EU'
			if invoice.bill_type == 'input_vat':
				bill_type = 'Input VAT'
			if invoice.bill_type == 'import_vat':
				bill_type = 'Import VAT'
			else:
				bill_type = ''
			worksheet.write(row, col, bill_type, name)
			col += 1
			worksheet.write(row, col, '', name) # No idea about accounting_date field
			col += 1
			worksheet.write(row, col, company.name, name)
			col += 1
			worksheet.write(row, col, invoice.journal_id.name, name)
			col += 1
			user = invoice.user_id and invoice.user_id.name or ''
			worksheet.write(row, col, user, name)
			col += 1
			if invoice.analytic_product == True:
				analytic_product = 'Yes'
			else:
				analytic_product = 'No'
			worksheet.write(row, col, analytic_product, name)
			row += 1
		col = 2

		worksheet.write(row, col, 'Total', name_head1)
		worksheet.write(row, col+1, total_untaxed, name_head1)
		worksheet.write(row, col+2, total_tax, name_head1)
		worksheet.write(row, col+3, total_amount, name_head1)
# 
		workbook.close()
		filename = 'SDT Invoice.xlsx'
		export_id = self.env['account.invoice.export'].create({'excel_file': base64.encodestring(fp.getvalue()), 'filename': filename})
		fp.close()
		
		return {
			'name': 'Invoice Report',
			'view_mode': 'form',
			'res_id': export_id.id,
			'res_model': 'account.invoice.export',
			'view_type': 'form',
			'type': 'ir.actions.act_window',
			'target': 'new'
		}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: