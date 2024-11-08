# -*- coding: utf-8 -*-
# coding: utf-8

from odoo import models, api, fields, exceptions, _
from io import BytesIO
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

import base64
import xlsxwriter
import os
import tempfile

class InvoicePaymentExport(models.TransientModel):
	_name = 'invoice.payment.export'
	_description = 'Invoice Payment Export'

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

		header = 'Payment advice from ' + company.name
		company_initials = company.name[0:2]

		worksheet.merge_range('A3:G3', header, company_heading)
		worksheet.merge_range('A4:C4', 'Our Customer Number in Your System :', name1)
		supnum = payment_ids[0].partner_id and payment_ids[0].partner_id.venice_supnum
		worksheet.merge_range('D4:G4', supnum, name)
		worksheet.merge_range('A5:C5', 'Payment Date :', name1)
		payment_date = datetime.strftime(payment_ids[0].payment_date, "%m/%d/%Y")
		worksheet.merge_range('D5:G5', payment_date, name)
		worksheet.merge_range('A6:C6', 'Payment Amount :', name1)
		worksheet.merge_range('D6:G6', payment_ids[0].amount, name)
		bank_account = ''
		memo = payment_ids[0].communication.replace(" ", "")
		print ("memo", memo)
		if 'IBAN:' in memo and 'BIC:' in memo:
			memo1 = memo.split('IBAN:')
			memo2 = memo1[1].split('BIC:')
			bank_account = memo2[0].strip()
		worksheet.merge_range('A7:C7', 'Your Account Number :', name1)
		worksheet.merge_range('D7:G7', bank_account, name)
		worksheet.merge_range('A8:C8', 'Cash Discount within X Days :', name1)
		worksheet.merge_range('D8:G8', '', name)
		worksheet.merge_range('A9:C9', 'Cash Discount x% :', name1)
		worksheet.merge_range('D9:G9', '', name)
		row = 11
		col = 0
		
		worksheet.write(row, col, "Details :", name_head1)

		row += 2
		worksheet.set_column('A14:A14', len('Invoice Nr')+1)
		worksheet.write(row, col, 'Invoice Nr', name_head1)
		col += 1
		worksheet.set_column('B14:B14', len('Our Doc Nr')+1)
		worksheet.write(row, col, 'Our Doc Nr', name_head1)
		col += 1
		worksheet.set_column('C14:C14', len('Invoice Date')+1)
		worksheet.write(row, col, 'Invoice Date', name_head1)
		col += 1
		worksheet.set_column('D14:D14', len('Due Date')+3)
		worksheet.write(row, col, 'Due Date', name_head1)
		col += 1
		worksheet.set_column('E14:E14', len('Invoice Amount')+1)
		worksheet.write(row, col, 'Invoice Amount', name_head1)
		col += 1
		worksheet.set_column('F14:F14', len('Cash Discount(EUR)')+1)
		worksheet.write(row, col, 'Cash Discount(EUR)', name_head1)
		col += 1
		worksheet.set_column('G14:G14', len('Paid Amount')+1)
		worksheet.write(row, col, 'Paid Amount', name_head1)
		
		row += 1
# Invoice Nr	Our Doc Nr	Invoice Date	Due Date	Invoice Amount	Cash discount EUR	Paid amount
		total_amount = total_paid_amount = total_discount = 0
# 		print ("paymnet)ids", payment_ids, payment_ids[0].invoice_ids)
		for invoice in payment_ids.reconciled_invoice_ids:
			col = 0
			discount_amount = 0
			paid_amount = invoice.amount_total - discount_amount
			worksheet.write(row, col , invoice.reference, name)
			col += 1
			worksheet.write(row, col , invoice.name, name)
			col += 1
			invoice_date = ''
			if invoice.date_invoice:
				invoice_date = datetime.strftime(invoice.date_invoice, "%m/%d/%Y")
			worksheet.write(row, col , invoice_date, name)
			col += 1
			due_date = ''
			if invoice.date_due:
				due_date = datetime.strftime(invoice.date_due, "%m/%d/%Y")
			worksheet.write(row, col , due_date, name)
			col += 1
			worksheet.write(row, col , invoice.amount_total, name)
			total_amount += invoice.amount_total
			col += 1
			worksheet.write(row, col , discount_amount, name)
			total_discount += discount_amount
			col += 1
			worksheet.write(row, col , paid_amount, name)
			total_paid_amount += paid_amount
			row += 1
		col = 3

		worksheet.write(row, col , 'Total', name_head1)
		worksheet.write(row, col+1 , total_amount, name_head1)
		worksheet.write(row, col+2 , total_discount, name_head1)
		worksheet.write(row, col+3 , total_paid_amount, name_head1)
# 
		workbook.close()
# 		SDT.BE - Maul 190310 (4567) Payment
		filename = 'SDT.%s - %s %s (%d) Payment.xlsx'%(company_initials, payment_ids[0].partner_id.name, payment_date, payment_ids[0].amount)
		export_id = self.env['invoice.payment.export'].create({'excel_file': base64.encodestring(fp.getvalue()), 'filename': filename})
		fp.close()
		
		return {
			'name': 'Invoice Payment Report',
			'view_mode': 'form',
			'res_id': export_id.id,
			'res_model': 'invoice.payment.export',
			'view_type': 'form',
			'type': 'ir.actions.act_window',
			'target': 'new'
		}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: