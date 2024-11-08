# -*- coding: utf-8 -*-

import logging
import tempfile
import xlrd
import datetime
# from ftplib import FTP
import ftplib
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

_logger = logging.getLogger(__name__)


class FTPSync(models.Model):
    _name = 'ftp.sync'
    _description = "FTP Syncing"

    name = fields.Char('Name', required=True)
    type = fields.Selection([('sinvoice', 'SInvoice'), ('pinvoice', 'PInvoice')], default="pinvoice",
                            string="Invoice Type", required=True)
    is_verified = fields.Boolean('Verified ?')
    ftp_url = fields.Char('URL', default='ftp.distri-smart.com')
    ftp_username = fields.Char('Username', default='sdt.odoo')
    ftp_password = fields.Char('Password', default='jDrDY8Q+U')
    read_file_from = fields.Char(string="Read From Directory", default="/PInvoices/DE")
    move_file_to = fields.Char(string="Move to Directory", default="/PInvoices/PUR_ODOO/DE_OK")
    active = fields.Boolean('Active', default=True)

    def action_check_ftp_connection(self):
        title = ""
        message = ""
        with ftplib.FTP(self.ftp_url) as ftp:
            try:
                ftp.login(self.ftp_username, self.ftp_password)
                has_failed = False
                title = _("Connection Test Succeeded!")
                message = _("Everything seems properly set up!")
                _logger.critical('Connection Succeeded with FTP ')
            except ftplib.all_errors as e:
                has_failed = True
                _logger.critical('Issue in Connection with FTP!')
                self.with_context({'is_check_connection_from_write': True}).write({'is_verified': False})
                title = _("Issue in Connection!")
                message = _(e)
        if has_failed:
            # raise Warning(title + '\n\n' + message + "%s" % str(e))
            raise UserError(_(title + '\n\n' + message + "%s" % str(e)))
        else:
            # raise Warning(title + '\n\n' + message)
            raise UserError(_(title + '\n\n' + message))

    def ftp_syning_import_invoice_cron(self):
        """
        @dbuuid: we don't want to fetch ftp data to other backup database so put this restriction based on database uuid
        you can find the dbuuid on system parameters.
        """
        dbuuid = self.env['ir.config_parameter'].sudo().get_param('database.uuid')
        if dbuuid == '02125f86-40b4-11ec-8acf-9d52c6117f09':
            for record in self.search([('active', '=', True)]):
                record.ftp_syncing_import_invoice()

    def ftp_syncing_import_invoice(self):
        # try:
        ftp_data = self.env['ftp.data']
        for ftp_record in self:
            with ftplib.FTP(ftp_record.ftp_url) as ftp:
                try:
                    # ftp = FTP(ftp_record.ftp_url)
                    ftp.login(ftp_record.ftp_username, ftp_record.ftp_password)
                    read_path = ftp_record.read_file_from
                    ftp.cwd(read_path)
                    file_list = ftp.nlst()
                    #count = 0
                    for file_name in file_list:
                        if file_name.lower().endswith('.xlsx'):
                            file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
                            ftp.retrbinary("RETR " + file_name, open(file.name, 'wb').write)
                            book = xlrd.open_workbook(file.name)
                            sheet = book.sheets()[0]
                            for row in range(sheet.nrows):
                                if row > 0 and ftp_record.type == 'pinvoice':
                                    document_date = False
                                    expiry_date = False
                                    cash_expiry_date = False
                                    if sheet.cell(row, 6).ctype is xlrd.XL_CELL_DATE:
                                        is_datetime = sheet.cell(row, 6).value % 1 != 0.0
                                        dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(sheet.cell(row, 6).value, book.datemode))
                                        document_date = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if is_datetime else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        
                                    if sheet.cell(row, 23).ctype is xlrd.XL_CELL_DATE:
                                        is_datetime = sheet.cell(row, 23).value % 1 != 0.0
                                        dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(sheet.cell(row, 23).value, book.datemode))
                                        expiry_date = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if is_datetime else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
        
                                    if sheet.cell(row, 35).ctype is xlrd.XL_CELL_DATE:
                                        is_datetime = sheet.cell(row, 35).value % 1 != 0.0
                                        dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(sheet.cell(row, 35).value, book.datemode))
                                        cash_expiry_date = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if is_datetime else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                                    document_number = sheet.cell(row, 3).value
                                    purchase_order_no = sheet.cell(row, 4).value
                                    sales_order_no = sheet.cell(row, 5).value
                                    remarks_vendor_inv_no = sheet.cell(row, 9).value
                                    mapping_dict = {
                                        'country': sheet.cell(row, 0).value,
                                        'book': sheet.cell(row, 1).value,
                                        'document_type': sheet.cell(row, 2).value,
                                        'document_number': isinstance(document_number, float) and str(int(document_number)) or document_number,
                                        'purchase_order_no': isinstance(purchase_order_no, float) and str(int(purchase_order_no)) or purchase_order_no,
                                        'sales_order_no': isinstance(sales_order_no, float) and str(int(sales_order_no)) or sales_order_no,
                                        'document_date': document_date,
                                        'supplier_number': sheet.cell(row, 7).value,
                                        'supplier_name': sheet.cell(row, 8).value,
                                        'remarks_vendor_inv_no': isinstance(remarks_vendor_inv_no, float) and str(int(remarks_vendor_inv_no)) or remarks_vendor_inv_no,
                                        'vat_system': sheet.cell(row, 10).value,
                                        'vat_rate_1': sheet.cell(row, 11).value,
                                        'vat_amount_1': sheet.cell(row, 12).value,
                                        'vat_rate_2': sheet.cell(row, 13).value,
                                        'vat_amount_2': sheet.cell(row, 14).value,
                                        'vat_rate_3': sheet.cell(row, 15).value,
                                        'vat_amount_3': sheet.cell(row, 16).value,
                                        'vat_rate_4': sheet.cell(row, 17).value,
                                        'vat_amount_4': sheet.cell(row, 18).value,
                                        'vat_rate_total': sheet.cell(row, 19).value,
                                        'vat_total': sheet.cell(row, 20).value,
                                        'document_total': sheet.cell(row, 21).value,
                                        'check_amount_by_sup_document': sheet.cell(row, 22).value,
                                        'expiry_date': expiry_date,
                                        'cash_discount_rate_percentage': sheet.cell(row, 24).value,
                                        'cash_discount_vat_rate_1': sheet.cell(row, 25).value,
                                        'cash_discount_vat_amount_1': sheet.cell(row, 26).value,
                                        'cash_discount_vat_rate_2': sheet.cell(row, 27).value,
                                        'cash_discount_vat_amount_2': sheet.cell(row, 28).value,
                                        'cash_discount_vat_rate_3': sheet.cell(row, 29).value,
                                        'cash_discount_vat_amount_3': sheet.cell(row, 30).value,
                                        'cash_discount_vat_rate_4': sheet.cell(row, 31).value,
                                        'cash_discount_vat_amount_4': sheet.cell(row, 32).value,
                                        'total_cash_discount': sheet.cell(row, 33).value,
                                        'total_cash_vat_discount': sheet.cell(row, 34).value,
                                        'cash_discount_expiry_date': cash_expiry_date,
                                        'ic_input': sheet.cell(row, 36).value,
                                        'ic_output': sheet.cell(row, 37).value,
                                        'import_filename': file_name,
                                    }
                                    ftp_data_id = ftp_data.create(mapping_dict)
                                    self._cr.commit()
        
                                elif row > 0 and ftp_record.type == 'sinvoice':
                                    document_date = False
                                    expiry_date = False
                                    cash_expiry_date = False
                                    if sheet.cell(row, 7).ctype is xlrd.XL_CELL_DATE:
                                        is_datetime = sheet.cell(row, 7).value % 1 != 0.0
                                        dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(sheet.cell(row, 7).value, book.datemode))
                                        document_date = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if is_datetime else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                                        
                                    if sheet.cell(row, 25).ctype is xlrd.XL_CELL_DATE:
                                        is_datetime = sheet.cell(row, 25).value % 1 != 0.0
                                        dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(sheet.cell(row, 25).value, book.datemode))
                                        expiry_date = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if is_datetime else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                                        
                                    if sheet.cell(row, 37).ctype is xlrd.XL_CELL_DATE:
                                        is_datetime = sheet.cell(row, 37).value % 1 != 0.0
                                        dt = datetime.datetime(*xlrd.xldate.xldate_as_tuple(sheet.cell(row, 37).value, book.datemode))
                                        cash_expiry_date = dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT) if is_datetime else dt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                                    document_number = sheet.cell(row, 3).value
                                    sales_order_no = sheet.cell(row, 4).value
                                    purchase_order_no = sheet.cell(row, 5).value
                                    purchase_invoice_no = sheet.cell(row, 6).value
                                    mapping_dict = {
                                        'country': sheet.cell(row, 0).value,
                                        'book': sheet.cell(row, 1).value,
                                        'document_type': sheet.cell(row, 2).value,
                                        'document_number': isinstance(document_number, float) and str(int(document_number)) or document_number,
                                        'sales_order_no': isinstance(sales_order_no, float) and str(int(sales_order_no)) or sales_order_no,
                                        'purchase_order_no': isinstance(purchase_order_no, float) and str(int(purchase_order_no)) or purchase_order_no,
                                        'purchase_invoice_no': isinstance(purchase_invoice_no, float) and str(int(purchase_invoice_no)) or purchase_invoice_no,
                                        'document_date': document_date,
                                        'customer_number': sheet.cell(row, 8).value,
                                        'customer_name': sheet.cell(row, 9).value,
                                        'customer_vat_id': sheet.cell(row, 10).value,
                                        'customer_group': sheet.cell(row, 11).value,
                                        'remark': sheet.cell(row, 12).value,
                                        'vat_system': sheet.cell(row, 13).value,
                                        'inv_vat_rate_1': sheet.cell(row, 14).value,
                                        'vat_amount_1': sheet.cell(row, 15).value,
                                        'inv_vat_rate_2': sheet.cell(row, 16).value,
                                        'vat_amount_2': sheet.cell(row, 17).value,
                                        'inv_vat_rate_3': sheet.cell(row, 18).value,
                                        'vat_amount_3': sheet.cell(row, 19).value,
                                        'inv_vat_rate_4': sheet.cell(row, 20).value,
                                        'vat_amount_4': sheet.cell(row, 21).value,
                                        'total_vat_amount': sheet.cell(row, 22).value,
                                        'document_total_ex_vat': sheet.cell(row, 23).value,
                                        'document_total_inc_vat': sheet.cell(row, 24).value,
                                        'expiry_date': expiry_date,
                                        'cd_cash_discount_vat_rate_1': sheet.cell(row, 26).value,
                                        'cd_vat_amount_on_discount_1': sheet.cell(row, 27).value,
                                        'cd_cash_discount_vat_rate_2': sheet.cell(row, 28).value,
                                        'cd_vat_amount_on_discount_2': sheet.cell(row, 29).value,
                                        'cd_cash_discount_vat_rate_3': sheet.cell(row, 30).value,
                                        'cd_vat_amount_on_discount_3': sheet.cell(row, 31).value,
                                        'cd_cash_discount_vat_rate_4': sheet.cell(row, 32).value,
                                        'cd_vat_amount_on_discount_4': sheet.cell(row, 33).value,
                                        'cd_total_vat_amount': sheet.cell(row, 34).value,
                                        'cd_document_total_ex_vat': sheet.cell(row, 35).value,
                                        'cd_document_total_inc_vat': sheet.cell(row, 36).value,
                                        'cd_cash_discount_expiry_date': cash_expiry_date,
                                        'import_filename': file_name,
                                    }
                                    ftp_data_id = ftp_data.create(mapping_dict)
                                    self._cr.commit()
        
                            source_path = read_path + '/' + file_name
                            dest_path = ftp_record.move_file_to + '/' + file_name
                            ftp.rename(source_path, dest_path)
                        else:
                            _logger.error(_("No File Found !!"))
                    #_logger.info(">>>>>>>>>>>>>>>: {}".format(count))
                    ftp.quit()
                except Exception as e:
                    _logger.error(_("Error: %s" % e))