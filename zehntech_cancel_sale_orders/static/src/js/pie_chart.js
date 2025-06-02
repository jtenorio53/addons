odoo.define('cancel_sales_dashboard.chart', function (require) {
    "use strict";

    const AbstractAction = require('web.AbstractAction');
    const core = require('web.core');
    const QWeb = core.qweb;

    const CancelSalesChart = AbstractAction.extend({
        template: 'CancelSalesDashboardChart',

        init: function (parent, action) {
            this._super(parent, action);
            this.dashboardData = action.dashboardData || [];
        },

        start: function () {
            this._renderChart();
        },

        _renderChart: function () {
            const ctx = this.$el.find('#chart')[0].getContext('2d');
            const labels = this.dashboardData.map(data => data.reason);
            const values = this.dashboardData.map(data => data.count);

            new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Cancellation Reasons',
                        data: values,
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
                    }],
                },
            });
        },
    });

    core.action_registry.add('cancel_sales_chart', CancelSalesChart);
    return CancelSalesChart;
});
