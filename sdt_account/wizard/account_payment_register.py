# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    # cashdiscount_total = fields.Monetary(currency_field='currency_id', store=True, readonly=False,
        # compute='_compute_cashdiscount_total')
    cashdiscount_total = fields.Monetary(currency_field='currency_id', string='Total CD')
    cashdiscount_notes = fields.Char(string='Internal Notes', compute='_compute_cashdiscount_notes', store=True)
    # -------------------------------------------------------------------------
    # BUSINESS METHODS
    # -------------------------------------------------------------------------

    @api.model
    def _get_batch_communication(self, batch_result):
        ''' Helper to compute the communication based on the batch.
        :param batch_result:    A batch returned by '_get_batches'.
        :return:                A string representing a communication to be set on payment.
        '''
        labels = set(line.move_id.payment_reference or line.move_id.ref or line.move_id.name for line in batch_result['lines'])
        return self.company_id.name[:2]+ ' - ' + ' '.join(sorted(labels))

    @api.depends('company_id', 'cashdiscount_total')
    def _compute_cashdiscount_notes(self):
        for wizard in self:
            if wizard.cashdiscount_total>0:
                wizard.cashdiscount_notes = wizard.company_id.name[:2]+ ' - ' + 'CD'

    # @api.model
    # def default_get(self, fields_list):
        # # OVERRIDE
        # res = super().default_get(fields_list)
        #
        # if 'cashdiscount_total' in fields_list:
        #
            # # Retrieve moves to pay from the context.
            #
            # if self._context.get('active_model') == 'account.move':
                # res['cashdiscount_total'] = self.env['account.move'].browse(self._context.get('active_ids', [])).cashdiscount_total
                #
        # return res

    # def _create_payment_vals_from_wizard(self):
        # res = super()._create_payment_vals_from_wizard()
        # print ("res?????????", res)
        # res.update({'cashdiscount_notes': self.cashdiscount_notes})
        # print ("res1111", res)
        # xxxxx
        # return res