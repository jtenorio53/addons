from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderConfirmDeleteWizard(models.TransientModel):
    _name = 'sale.order.confirm.delete.wizard'
    _description = 'Sale Order Confirm Delete Wizard'

    confirmation_message = fields.Char(
        string=_('Confirmation Message'),
        readonly=True
    )

    def confirm_delete_action(self):
        """Delete the sale order, show success toast, then open the original Quotations onboarding page."""
        active_id = self.env.context.get('active_id')
        sale_order = self.env['sale.order'].browse(active_id)

        if not sale_order.exists():
            # The sale order no longer exists, show a warning
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning'),
                    'message': _('The sale order no longer exists.'),
                    'type': 'warning',
                    'sticky': False,
                },
            }

        # 1) Delete/cancel the sale order
        sale_order.action_cancel_and_delete()

        # 2) Load the standard Quotation onboarding action
        #    This is the same action used by Odoo's "Quotations" menu with the big steps
        quotations_action = self.env.ref('sale.action_quotations_with_onboarding').sudo().read()[0]
        quotations_action['target'] = 'current'  # Open in current window

        # 3) Return a success notification with a "next" action that triggers the original Quotation pipeline
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('The sale order has been successfully deleted.'),
                'type': 'success',
                'sticky': False,
                'next': quotations_action,  # This references the standard Quotation page
            },
        }
