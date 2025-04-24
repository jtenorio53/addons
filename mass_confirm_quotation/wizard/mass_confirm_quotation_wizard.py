# -*- coding: utf-8 -*-
# Copyright (C) Quocent Pvt. Ltd.
# All Rights Reserved

from odoo import models, fields

class MassConfirmQuotation(models.TransientModel):
    _name = 'mass.confirm.quotation'
    _description = 'Mass Confirm Quotation'

    def confirm(self):
        quotations = self.env['sale.order'].browse(self.env.context.get('active_ids', []))

        for quotation in quotations:
            if quotation.state not in ("cancel", "done"):
                quotation.action_confirm()
