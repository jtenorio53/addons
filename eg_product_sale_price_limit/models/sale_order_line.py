from odoo import models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    # out_of_range = fields.Boolean(string="Out Of Range", readonly=True)
    min_price_limit = fields.Float(String="Min Price Limit")
    max_price_limit = fields.Float(String="Max Price Limit")
    confirm_order = fields.Boolean(string='Confirm order')

    # @api.onchange("price_unit")
    # def onchange_on_price_unit_for_validation_price(self):
    #     # group_id = self.env.ref("eg_product_sale_price_limit.group_confirm_sale_price")
    #     if self.env.user.has_group("eg_product_sale_price_limit.group_confirm_sale_price"):
    #         if self.max_price_limit or self.min_price_limit:
    #             if not (self.min_price_limit <= self.price_unit <= self.max_price_limit):
    #                 self.out_of_range = True
    #             else:
    #                 self.out_of_range = False
    #         else:
    #             self.out_of_range = False

    @api.onchange("product_id")
    def onchange_on_product_id_for_set_min_max_price(self):
        if self.product_id:
            currency_id = self.product_id.currency_id
            if currency_id != self.order_id.pricelist_id.currency_id:
                min_price_limit = currency_id._convert(self.product_id.min_price_limit
                                                       , self.order_id.pricelist_id.currency_id,
                                                       self.order_id.company_id or self.env.company,
                                                       self.order_id.date_order or fields.Date.today())
                max_price_limit = currency_id._convert(self.product_id.max_price_limit
                                                       , self.order_id.pricelist_id.currency_id,
                                                       self.order_id.company_id or self.env.company,
                                                       self.order_id.date_order or fields.Date.today())
            else:
                min_price_limit = self.product_id.min_price_limit
                max_price_limit = self.product_id.max_price_limit
            self.min_price_limit = min_price_limit
            self.max_price_limit = max_price_limit
            # self.onchange_on_price_unit_for_validation_price()
        else:
            self.min_price_limit = 0
            self.max_price_limit = 0
