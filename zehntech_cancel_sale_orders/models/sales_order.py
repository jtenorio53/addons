from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cancel_associated_records = fields.Boolean(
        string="Cancel Associated Records",
        help="Cancel associated delivery orders and invoices when canceling the sale order."
    )
    active = fields.Boolean(string='Active', default=True)  # soft delete flag

    def open_cancel_wizard(self):
        """Open the cancel wizard."""
        self._check_access()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cancel Order',
            'res_model': 'sale.order.cancel.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_option': 'cancel_only'},
        }

    def action_cancel_only(self):
        """Cancel the sale order."""
        self._check_access()
        for order in self:
            if order.state not in ['cancel']:
                order.write({'state': 'cancel'})
                order.message_post(body=_("The sale order has been marked as 'Cancelled'."))

                self.env['cancel.sales.data.history'].create({
                    'name': order.name,
                    'model': self._name,
                    'record_id': order.id,
                    'action_type': 'cancel',
                    'associated_data': str({'pickings': order.picking_ids.ids, 'invoices': order.invoice_ids.ids}),
                    'timestamp': fields.Datetime.now(),
                    'user_id': self.env.user.id,
                    'state': 'cancelled',
                })

                if order.cancel_associated_records:
                    self._cancel_associated_records(order)

    def action_reset_to_draft(self):
        """Reset the sale order to draft."""
        self._check_access()
        for order in self:
            if order.state not in ['cancel']:
                # Cancel the order first if it is not already canceled
                order.write({'state': 'cancel'})
                order.message_post(body=_("The sale order has been canceled."))
            order.write({'state': 'draft'})
            associated_data = {
                'pickings': order.picking_ids.ids,
                'invoices': order.invoice_ids.ids,
            }
            self.env['cancel.sales.data.history'].create({
                'name': order.name,
                'model': self._name,
                'record_id': order.id,
                'action_type': 'reset_to_draft',
                'associated_data': str(associated_data),
                'timestamp': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'state': 'reset_to_draft',
            })

            if order.cancel_associated_records:
                self._reset_associated_records(order)

            order.message_post(body=_("The sale order and associated records have been reset to Quotation State."))

    def action_cancel_and_delete(self):
        """Cancel and archive the sale order."""
        self._check_access()
        for order in self:
            if order.state != 'cancel':
                order.write({'state': 'cancel'})
            associated_data = {
                'name': order.name,
                'partner_id': order.partner_id.id,
                'order_line': [(0, 0, {'product_id': line.product_id.id, 'product_uom_qty': line.product_uom_qty})
                               for line in order.order_line],
                'state': 'draft',
            }
            self.env['cancel.sales.data.history'].create({
                'name': order.name,
                'record_id': order.id,
                'action_type': 'delete',
                'associated_data': str(associated_data),
                'timestamp': fields.Datetime.now(),
                'user_id': self.env.user.id,
                'state': 'archived',
            })
            order.message_post(body=_("The sale order has been archived to data history."))
            order.write({'active': False})

    def action_bulk_cancel_only(self):
        """Bulk cancel sale orders."""
        self._check_access()
        if self.env.context.get('dashboard_mode'):
            raise UserError(_("Bulk cancel actions are not allowed from the Dashboard."))
        self.action_cancel_only()

    def action_bulk_reset_to_draft(self):
        """Bulk reset sale orders to draft."""
        self._check_access()
        if self.env.context.get('dashboard_mode'):
            raise UserError(_("Bulk cancel actions are not allowed from the Dashboard."))
        self.action_reset_to_draft()

    def action_bulk_cancel_and_delete(self):
        """Bulk cancel and delete sale orders."""
        self._check_access()
        if self.env.context.get('dashboard_mode'):
            raise UserError(_("Bulk cancel actions are not allowed from the Dashboard."))
        self.action_cancel_and_delete()

    def _cancel_associated_records(self, order):
        """Cancel associated delivery orders and invoices."""
        # Process delivery orders
        for picking in order.picking_ids:
            if picking.state not in ['done', 'cancel']:
                picking.action_cancel()
                picking.message_post(body=_("This transfer was canceled along with the sale order."))
            elif picking.state == 'done':
                order.message_post(body=_("Delivery order %s is already done and cannot be canceled." % picking.name))

        # Process invoices
        for invoice in order.invoice_ids:
            # Only process the invoice if it is in draft (cancelable)
            if invoice.state == 'draft':
                invoice.button_cancel()
                invoice.message_post(body=_("This invoice was canceled along with the sale order."))
            else:
                order.message_post(body=_("Invoice %s is posted/paid and was not canceled." % invoice.name))

    def _reset_associated_records(self, order):
        """Reset associated delivery orders and invoices to draft."""
        for picking in order.picking_ids:
            # For any picking that is not done, force it to cancel first.
            if picking.state != 'done':
                # If not already canceled, cancel it.
                if picking.state != 'cancel':
                    picking.action_cancel()
                # After ensuring it is canceled, reset it to draft.
                if picking.state == 'cancel':
                    picking.write({'state': 'draft'})
                    picking.do_unreserve()  # Unreserve the stock
                    move_field = 'move_lines' if hasattr(picking, 'move_lines') else 'move_ids_without_package'
                    for move in getattr(picking, move_field, []):
                        if move.state == 'cancel':
                            move.write({'state': 'draft'})
                    picking.message_post(body=_("This transfer was reset to draft along with the sale order."))
            else:
                order.message_post(body=_("Delivery order %s is already done and cannot be reset to draft." % picking.name))

        # Process invoices: only reset invoices that are in cancel state (the rest remain posted)
        for invoice in order.invoice_ids:
            if invoice.state == 'cancel':
                invoice.button_draft()
            else:
                order.message_post(body=_("Invoice %s is posted/paid and was not reset to draft." % invoice.name))

    def _delete_associated_records(self, order):
        """Delete associated delivery orders and invoices."""
        for picking in order.picking_ids:
            if picking.state != 'cancel':
                picking.action_cancel()
            picking.unlink()
            order.message_post(body=_("The delivery order %s was deleted along with the sale order." % picking.name))
        for invoice in order.invoice_ids:
            if invoice.state != 'cancel':
                invoice.button_cancel()
            invoice.unlink()

    def _check_access(self):
        # Admins bypass restrictions
        if self.env.user.has_group('base.group_system'):
            return
        enable_cancel_sales = self.env['ir.config_parameter'].sudo().get_param('cancel_sales.enable_feature', default='False')
        if enable_cancel_sales != 'True':
            raise UserError(_("Cancel functionality is globally disabled for regular users. Please contact your administrator."))

    def action_restore_order(self):
        """Restore the sale order (unarchive)."""
        if not self.active:
            self.write({'active': True, 'state': 'draft'})
            self.message_post(body=_("The sale order has been restored from the archive."))
        else:
            raise UserError(_("The sale order is already active and does not need restoration."))
