# from odoo import models, fields

# class CancelSalesUserAccess(models.Model):
#     _name = 'cancel.sales.user.access'
#     _description = 'Cancel Sales User Access'

#     user_id = fields.Many2one('res.users', string="User", required=True)
#     allow_access = fields.Boolean(string="Allow Access", default=False)
#     config_id = fields.Many2one(
#         'cancel.sales.configuration',
#         string="Configuration",
#         required=True
#     )
