from odoo import models, fields, api, _

class SaleOrderCancelWizard(models.TransientModel):
    _name = 'sale.order.cancel.wizard'
    _description = 'Sale Order Cancel Wizard'

    option = fields.Selection([
        ('cancel_only', _('Cancel Only')),
        ('reset_to_draft', _('Cancel and Reset to Quotation State')),
        ('cancel_and_delete', _('Cancel and Delete')),
    ], required=True, string="Cancel Option", default="cancel_only")

    def _display_notification(self, title, message, message_type='success'):
        """Display a notification to the user."""
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': message_type,
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'}  # Automatically close the wizard

            },
        }

    def confirm_cancel_action(self):
        """Execute the selected cancel option."""
        active_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(active_id)

        if self.option == 'cancel_only':
            sale_order.action_cancel_only()
            return self._display_notification(
                title=('Success'),
                message=_('The sale order has been successfully cancelled.'),
            )
        elif self.option == 'reset_to_draft':
            if sale_order.state == 'draft':  # Check if it's already in Quotation state
                return self._display_notification(
                    title=_('Already in Quotation'),
                    message=_('The sale order is already in Quotation state. No changes made.'),
                    message_type='warning',
                )
            sale_order.action_reset_to_draft()
            return self._display_notification(
                title=_('Success'),
                message=_('The sale order and associated records have been reset to Quotation successfully.'),
            )

        elif self.option == 'cancel_and_delete':
            # Open the second confirmation wizard
            return {
                'type': 'ir.actions.act_window',
                'name': _('Confirm Deletion'),
                'res_model': 'sale.order.confirm.delete.wizard',
                'view_mode': 'form',
                'target': 'new',
                        'context': {
            'active_id': sale_order.id,
            'default_confirmation_message': _('Are you sure you want to permanently delete this Sale Order?'),
        },
            }
