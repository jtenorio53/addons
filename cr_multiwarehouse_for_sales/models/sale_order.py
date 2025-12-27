# -*- coding: utf-8 -*-
# Part of Creyox technologies.

from odoo import models, fields
from odoo.exceptions import UserError
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_multi_warehouse = fields.Boolean(string="Multi Warehouse", default=False)

    def _action_confirm(self):
        res_config = self.env.company
        if res_config.allow_sale_warehouse:
            warehouse_ids = []
            [
                warehouse_ids.append(x.warehouses_id)
                for x in self.order_line
                if x.warehouses_id not in warehouse_ids
            ]
            for warehouses_id in warehouse_ids:
                so_lines = self.env["sale.order.line"].search(
                    [
                        ("warehouses_id", "=", warehouses_id.id),
                        ("order_id", "=", self.id),
                    ]
                )
        super(SaleOrder, self)._action_confirm()
