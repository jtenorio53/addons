from odoo import models, fields, api, _
from odoo.exceptions import UserError


class CancelSalesDataHistory(models.Model):
    _name = 'cancel.sales.data.history'
    _description = 'Cancel Sales Data History'

    name = fields.Char(string="Record Name", required=True)
    model = fields.Char(string="Model", default='sale.order')
    record_id = fields.Integer(string="Record ID", required=True)
    user_id = fields.Many2one('res.users', string="Performed By", default=lambda self: self.env.user, required=True)
    action_type = fields.Selection(
        [('cancel', 'Cancel'), ('delete', 'Delete'), ('reset_to_draft', 'Reset to Draft')],
        string="Action Type",
        required=True
    )
    associated_data = fields.Text(string="Associated Data", help="Serialized data for related fields")
    timestamp = fields.Datetime(string="Timestamp", default=fields.Datetime.now)
    state = fields.Selection([
        ('archived', 'Deleted'),
        ('restored', 'Restored'),
        ('reset_to_draft', 'Reset to Draft'),
        ('cancelled', 'Cancelled'),
    ], default='archived', string="State")
    def restore_data(self):
        """Restore a sale order from data history by unarchiving it, including associated records."""
        if not self.env.user.has_group('base.group_system'):
            raise UserError(_("Only administrators can restore data history."))

        for record in self:
            if record.state != 'archived':
                raise UserError(_("Only deleted records can be restored."))

            # Deserialize associated data
            associated_data = eval(record.associated_data or '{}')
            pickings = associated_data.get('pickings', [])
            invoices = associated_data.get('invoices', [])

            # Locate the archived sale order using the record_id
            sale_order = self.env['sale.order'].search([('id', '=', record.record_id), ('active', '=', False)])
            
            if not sale_order:
                raise UserError(_("The sale order record could not be found or is already active."))

            # Restore the sale order by unarchiving
            sale_order.write({'active': True, 'state': 'draft'})
            sale_order.message_post(body=_("The sale order has been restored from the archive."))

            # Restore associated pickings (delivery orders)
            for picking_id in pickings:
                picking = self.env['stock.picking'].browse(picking_id)
                if picking.exists() and not picking.active:
                    picking.write({'active': True, 'state': 'draft'})
                    picking.message_post(body=_("This delivery order was restored along with the sale order."))

            # Restore associated invoices
            for invoice_id in invoices:
                invoice = self.env['account.move'].browse(invoice_id)
                if invoice.exists() and not invoice.active:
                    invoice.write({'active': True, 'state': 'draft'})
                    invoice.message_post(body=_("This invoice was restored along with the sale order."))

            # Update the state in history to 'restored'
            record.write({'state': 'restored'})

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('The sale order and associated records have been restored successfully.'),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'reload'},

            },
        }
