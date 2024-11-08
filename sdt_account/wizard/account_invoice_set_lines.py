# -*- coding: utf-8 -*-
from openerp import models, api, fields, _
from openerp.exceptions import UserError


class AccountInvoiceSetLines(models.TransientModel):
    """
    This wizard will allows to select a analytic account, department, HR of Invoice Lines:
    """

    _name = "account.invoice.set.lines"
    _description = "Update Invoice Lines"

    department_id = fields.Many2one('invoice.department', string='Department')
    hr_id = fields.Many2one('invoice.hr', string='HR')

    @api.multi
    def update_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            for line in record.invoice_line_ids:
                if line.product_id:
                    line.account_analytic_id = line.product_id.account_analytic_id.id
                if self.department_id:
                    line.department_id = self.department_id.id
                if self.hr_id:
                    line.hr_id = self.hr_id.id
        return {'type': 'ir.actions.act_window_close'}

class AccountInvoiceSetTaxes(models.TransientModel):
    """
    This wizard will allows to update taxes on lines based on fiscal position selection:
    """

    _name = "account.invoice.set.taxes"
    _description = "Update Invoice Line Taxes"

    fiscal_position_id = fields.Many2one('account.fiscal.position', string='Fiscal Position')

    @api.multi
    def update_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            record.fiscal_position_id = self.fiscal_position_id.id
            for line in record.invoice_line_ids:
                if line.product_id:
                    price = line.price_unit
                    line._onchange_product_id()
                    line.write({'price_unit': price})
                taxes_grouped = record.get_taxes_values()
                tax_lines = record.tax_line_ids.filtered('manual')
                for tax in taxes_grouped.values():
                    tax_lines += tax_lines.new(tax)
                record.tax_line_ids = tax_lines
        return {'type': 'ir.actions.act_window_close'}

class AccountInvoiceSetProduct(models.TransientModel):
    """
    This wizard will allows to update Product on line as selected on wizard.
    """

    _name = "account.invoice.set.product"
    _description = "Update Invoice Line Product"

    product_id = fields.Many2one('product.product', string='Product', required=True)

    @api.multi
    def update_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            for line in record.invoice_line_ids:
                price = line.price_unit
                line.product_id = self.product_id.id
                line._onchange_product_id()
                line.write({'price_unit': price})
                taxes_grouped = record.get_taxes_values()
                tax_lines = record.tax_line_ids.filtered('manual')
                for tax in taxes_grouped.values():
                    tax_lines += tax_lines.new(tax)
                record.tax_line_ids = tax_lines
        return {'type': 'ir.actions.act_window_close'}

class AccountInvoiceLineCreate(models.TransientModel):
    """
    This wizard will create invoice line for selected invoices from papersmart tab information.
    """

    _name = "account.invoice.line.create"
    _description = "Create Invoice Line"

    product_id = fields.Many2one('product.product', string='Product', required=True)

    @api.multi
    def update_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        line_obj = self.env['account.invoice.line']
        tax_obj = self.env['account.tax']
        imd = self.env['ir.model.data']
        for record in self.env['account.invoice'].browse(active_ids):
            if record.state != 'imported':
                raise UserError(_("Invoice must be in imported state in order to create invoice line."))
            if record.ppc_invoice:
                invoice_line_data = {
                    'product_id': self.product_id.id,
                    'quantity': 1,
                    'price_unit': record.ppc_nettotal,
                    'invoice_id': record.id,
                    'account_id': record.journal_id.default_debit_account_id.id,
                    'name': 'import'
                }
                line = line_obj.create(invoice_line_data)
                line._onchange_product_id()
                line.write({'price_unit': record.ppc_nettotal})
                if record.ppc_vat == round(record.ppc_nettotal*0.07, 2):
                    #19% l10n_de_skr04.2_tax_ust_19_skr04
                    #7% l10n_de_skr04.2_tax_ust_7_skr04
                    tax_id = imd.xmlid_to_res_id('l10n_de_skr04.2_tax_ust_7_skr04')
                    line.invoice_line_tax_ids = tax_obj.browse(tax_id)
                taxes_grouped = record.get_taxes_values()
                tax_lines = record.tax_line_ids.filtered('manual')
                for tax in taxes_grouped.values():
                    tax_lines += tax_lines.new(tax)
                record.tax_line_ids = tax_lines
        return {'type': 'ir.actions.act_window_close'}

class AccountInvoiceSetDiscount(models.TransientModel):
    """
    This wizard will allows to select a value for discount on lines:

- Discount in %

In the list view select invoices in draft, and can use the action in order to set up the value.
    """

    _name = "account.invoice.set.discount"
    _description = "Update Discount on selected Invoices"

    discount =  fields.Float(string='Discount in %')

    @api.multi
    def update_invoices(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []

        for record in self.env['account.invoice'].browse(active_ids):
            for line in record.invoice_line_ids:
                line.discount = self.discount
                price = line.price_unit
#                 line.product_id = self.product_id.id
#                 line._onchange_product_id()
                line.write({'price_unit': price})
                taxes_grouped = record.get_taxes_values()
                tax_lines = record.tax_line_ids.filtered('manual')
                for tax in taxes_grouped.values():
                    tax_lines += tax_lines.new(tax)
                record.tax_line_ids = tax_lines
        return {'type': 'ir.actions.act_window_close'}
        return {'type': 'ir.actions.act_window_close'}