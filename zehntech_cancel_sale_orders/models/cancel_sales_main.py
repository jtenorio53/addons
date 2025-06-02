from odoo import models, fields

class CancelSalesMain(models.Model):
    _name = 'cancel.sales.main'
    _description = 'Cancel Sales Main Page'

    name = fields.Char(string="Name", default="Cancel Sales")
    description = fields.Text(string="Description")
