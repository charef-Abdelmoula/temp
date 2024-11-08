# -*- coding: utf-8 -*-
# coding: utf-8

from odoo import models, api, fields, exceptions, _
from io import BytesIO
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import base64
import xlsxwriter

class InvoiceBillsExport(models.TransientModel):
	_name = 'invoice.bills.export'
	_description = 'Invoice Bills Export'

	filename = fields.Char('File Name', size=128, default="Report XLS")
	excel_file = fields.Binary('Download Excel File')
	fname = fields.Char('Report XLS', default = 'Report XLS')

	@api.multi
	def generate_report(self):
		active_ids = self._context.get('active_ids')
		if len(active_ids)>1:
				raise exceptions.Warning(
					_('Please select any one record to generate this report!'))
		payment_ids = self.env['account.payment'].browse(active_ids)
		fp = BytesIO()
		workbook = xlsxwriter.Workbook(fp)
		worksheet = workbook.add_worksheet('Payment Details')
		worksheet.set_column('B:B', 15)

		company = self.env['res.users'].browse(self.env.uid).company_id
		if company.logo:
			filename = 'company_logo.png'
			image_data = BytesIO(base64.b64decode(company.logo))
			worksheet.insert_image('H1', filename, {'image_data': image_data, 'x_scale':3, 'y_scale': 3.5})

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
		text_format = workbook.add_format({
			'text_wrap': True,
			'font_size' : 13,
			'align' : 'left',
			'font_name' : 'Times New Roman',
		})

		company_initials = company.name[0:2]

		worksheet.merge_range('A4:H4', payment_ids[0].name, company_heading)
		worksheet.write(4, 0, 'Payment Type :', name1)
		worksheet.merge_range('B5:D5', payment_ids[0].payment_type.capitalize(), name)
		worksheet.write(5, 0, 'Partner Type :', name1)
		worksheet.merge_range('B6:D6', payment_ids[0].partner_type.capitalize(), name)
		worksheet.write(6, 0, 'Partner :', name1)
		worksheet.merge_range('B7:D7', payment_ids[0].partner_id.name, name)
		worksheet.write(7, 0, 'Payment Amount :', name1)
		worksheet.merge_range('B8:D8', payment_ids[0].amount, name)
		worksheet.write(8, 0, 'Payment Journal :', name1)
		worksheet.merge_range('B9:D9', payment_ids[0].journal_id.name, name)
		worksheet.write(9, 0, 'Payment Mode :', name1)
		worksheet.merge_range('B10:D10', '', name)

		worksheet.write(4, 4, 'Payment Date :', name1)
		payment_date = datetime.strftime(payment_ids[0].payment_date, "%m/%d/%Y")
		worksheet.merge_range('F5:H5', payment_date, name)
		worksheet.write(5, 4, 'Memo :', name1)
		worksheet.merge_range('F6:H10', payment_ids[0].communication, text_format)
		worksheet.write(10, 4, 'Company :', name1)
		worksheet.merge_range('F11:H11', company.name, text_format)
		bank_account = ''
		memo = payment_ids[0].communication.replace(" ", "")
		print ("memo", memo)
		if 'IBAN:' in memo and 'BIC:' in memo:
			memo1 = memo.split('IBAN:')
			memo2 = memo1[1].split('BIC:')
			bank_account = memo2[0].strip()
		worksheet.write(10, 0, 'Your Account Number :', name1)
		worksheet.merge_range('B11:D11', bank_account, name)

		row = 12
		col = 0
		
		worksheet.write(row, col, "Details :", name_head1)

		row += 2
		worksheet.set_column('A15:A15', len(payment_ids[0].partner_id.name)+3)
		worksheet.write(row, col, 'Vendor', name_head1)
		col += 1
		worksheet.set_column('B15:B15', len('Bill Date')+1)
		worksheet.write(row, col, 'Bill Date', name_head1)
		col += 1
		worksheet.set_column('C15:C15', len('Payment Ref.')+1)
		worksheet.write(row, col, 'Payment Ref.', name_head1)
		col += 1
		worksheet.set_column('D15:D15', len('Description')+3)
		worksheet.write(row, col, 'Description', name_head1)
		col += 1
		worksheet.set_column('E15:E15', len('Due Date')+3)
		worksheet.write(row, col, 'Due Date', name_head1)
		col += 1
		worksheet.set_column('F15:F15', len('Tax Exclued')+1)
		worksheet.write(row, col, 'Tax Exclued', name_head1)
		col += 1
		worksheet.set_column('G15:G15', len('Tax')+9)
		worksheet.write(row, col, 'Tax', name_head1)
		col += 1
		worksheet.set_column('H15:H15', len('Total')+7)
		worksheet.write(row, col, 'Total', name_head1)
		
		row += 1
		total_untaxed = total_tax = total_amount = 0
		for invoice in payment_ids.reconciled_invoice_ids:
			
			col = 0
			worksheet.write(row, col, invoice.partner_id.name, name)
			col += 1
			invoice_date = ''
			if invoice.date_invoice:
				invoice_date = datetime.strftime(invoice.date_invoice, "%m/%d/%Y")
			worksheet.write(row, col, invoice_date, name)
			col += 1
			worksheet.write(row, col, invoice.reference, name)
			col += 1
			worksheet.write(row, col, invoice.name, name)
			col += 1
			due_date = ''
			if invoice.date_due:
				due_date = datetime.strftime(invoice.date_due, "%m/%d/%Y")
			worksheet.write(row, col, due_date, name)
			col += 1
			worksheet.write(row, col, invoice.amount_untaxed, name)
			total_untaxed += invoice.amount_untaxed
			col += 1
			worksheet.write(row, col, invoice.amount_tax, name)
			total_tax += invoice.amount_tax
			col += 1
			worksheet.write(row, col, invoice.amount_total, name)
			total_amount += invoice.amount_total
			row += 1
		col = 4

		worksheet.write(row, col, 'Total', name_head1)
		worksheet.write(row, col+1, total_untaxed, name_head1)
		worksheet.write(row, col+2, total_tax, name_head1)
		worksheet.write(row, col+3, total_amount, name_head1)
# 
		workbook.close()
		filename = 'SDT.%s - %s %s (%d) Bills.xlsx'%(company_initials, payment_ids[0].partner_id.name, payment_date, payment_ids[0].amount)
		export_id = self.env['invoice.bills.export'].create({'excel_file': base64.encodestring(fp.getvalue()), 'filename': filename})
		fp.close()
		
		return {
			'name': 'Invoice Bills Report',
			'view_mode': 'form',
			'res_id': export_id.id,
			'res_model': 'invoice.bills.export',
			'view_type': 'form',
			'type': 'ir.actions.act_window',
			'target': 'new'
		}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: