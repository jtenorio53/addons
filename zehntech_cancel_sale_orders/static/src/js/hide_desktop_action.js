odoo.define('zehntech_cancel_sale_orders_v16.hide_restore_action', function (require) {
    "use strict";
    const domReady = require('web.dom_ready');
    const $ = require('web.jquery');

    function toggleRestoreActionVisibility() {
        // This selector finds <li> or <a> containing the text "Restore Selected"
        // (case-sensitive). Adjust if your text is different or has extra spaces.
        const restoreItems = $("li.o_menu_entry_bs, a.o_menu_entry_bs").filter(function() {
            return $(this).text().trim() === "Restore Selected";
        });

        if (restoreItems.length) {
            if ($(window).width() >= 768) {
                // On desktop, hide
                restoreItems.hide();
            } else {
                // On mobile, show
                restoreItems.show();
            }
        }
    }

    // Run after DOM is ready
    if (!domReady.isReady()) {
        domReady.ready(function () {
            toggleRestoreActionVisibility();
            $(window).on('resize', toggleRestoreActionVisibility);
        });
    } else {
        toggleRestoreActionVisibility();
        $(window).on('resize', toggleRestoreActionVisibility);
    }
});
