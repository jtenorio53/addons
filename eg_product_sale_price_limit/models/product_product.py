from odoo import models, fields, api
from odoo.exceptions import Warning


class ProductProduct(models.Model):
    _inherit = 'product.product'

    min_price_limit = fields.Float(String="Min Price Limit")
    max_price_limit = fields.Float(String="Max Price Limit")

    # @api.constrains("min_price_limit", "max_price_limit")
    # def check_validation_for_min_max_price(self):
    #     if self.min_price_limit > self.max_price_limit:
    #         raise Warning("Minimum sale price is less then maximum sale price!!!")
    #     if self.min_price_limit < 0 or self.max_price_limit < 0:
    #         raise Warning("Minimum sale price and maximum sale price should be positive!!!")
