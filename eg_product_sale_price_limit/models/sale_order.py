from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    confirm_order = fields.Boolean(string='Confirm order')

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.env.user.has_group("eg_product_sale_price_limit.group_confirm_sale_price"):
            for order_line_id in self.order_line:
                if order_line_id.min_price_limit or order_line_id.max_price_limit:
                    if not (order_line_id.min_price_limit <= order_line_id.price_unit <= order_line_id.max_price_limit):
                        raise ValidationError(
                            "Product Sale price should be under the range of defined product minimum and maximum price limit.")

        return res
