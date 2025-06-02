from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CancelSalesConfiguration(models.Model):
    _name = 'cancel.sales.configuration'
    _description = 'Cancel Sales Configuration'

    enable_feature = fields.Boolean(
        string="Enable Cancel Sales for Users",
        default=True,
        help="Enable or disable cancel functionalities for non-admin users."
    )

    default_reason = fields.Char(
        string="Default Cancellation Reason",
        help="Specify a default reason for cancellations."
    )

    @api.model
    def create(self, vals):
        """
        Ensure no duplicate records are created. If a record exists, update it.
        """
        existing = self.search([], limit=1)
        if existing:
            existing.write(vals)
            return existing
        return super(CancelSalesConfiguration, self).create(vals)

    @api.constrains('enable_feature')
    def _check_singleton(self):
        """
        Ensure only one configuration record exists.
        """
        if self.search_count([]) > 1:
            raise ValidationError(_("Only one Cancel Sales Configuration record can exist!"))

    @api.model
    def toggle_feature(self):
        """
        Toggle the 'enable_feature' field and update related user permissions.
        """
        config = self.search([], limit=1)
        if not config:
            config = self.create({'enable_feature': False})

        # Toggle the feature
        config.enable_feature = not config.enable_feature

    @api.model
    def get_current_state(self):
        """
        Retrieve the current state of the 'enable_feature' field.
        """
        config = self.search([], limit=1)
        return config.enable_feature if config else False

    @api.model
    def get_default_configuration(self):
        """
        Retrieve or create the single configuration record.
        """
        config = self.search([], limit=1)
        if not config:
            config = self.create({'enable_feature': True})
        return config
