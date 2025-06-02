odoo.define('odoo_cancel_sale_orders_v16.popup_notification', function (require) {
    "use strict";

    const NotificationManager = require('web.NotificationManager');

    NotificationManager.include({
        notify_success: function (title, message) {
            this.add(
                title || "Success",
                message || "Operation completed successfully!",
                { type: 'success', sticky: false }
            );
        },
        notify_error: function (title, message) {
            this.add(
                title || "Error",
                message || "Something went wrong!",
                { type: 'danger', sticky: true }
            );
        },
    });
});
