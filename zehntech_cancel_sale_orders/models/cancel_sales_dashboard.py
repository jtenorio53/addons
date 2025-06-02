from odoo import models, fields, api, _
from datetime import timedelta
import json
import logging

_logger = logging.getLogger(__name__)

TIME_RANGE_SELECTION = [
    ('all_time', 'All Time'),
    ('today', 'Today'),
    ('this_week', 'This Week'),
    ('this_month', 'This Month'),
    ('this_quarter', 'This Quarter'),
    ('this_year', 'This Year'),
    ('custom', 'Custom'),
]

class CancelSalesDashboard(models.Model):
    _name = 'cancel.sales.dashboard'
    _description = 'Cancel Sales Dashboard'

    employee_id = fields.Many2one('res.users', string='User', required=False,     ondelete='cascade',  # <-- add this
)
    color = fields.Char(string="Card Color", default="#000000")

    # Computed counts for each status
    draft_count = fields.Integer(string="Quotation Count", compute="_compute_counts")
    confirmed_count = fields.Integer(string="Sales Order Count", compute="_compute_counts")
    cancelled_count = fields.Integer(string="Cancelled Count", compute="_compute_counts")

    # JSON chart data for a chart widget
    sales_kanban_bar_chart = fields.Text(string="Sales Bar Chart", compute="_compute_chart_json")

    # Simple HTML-based bar graph
    sale_bar_html = fields.Html(string="Colored Bar Graph", compute="_compute_sale_bar_html")

    # Optional color fields
    quotation_color = fields.Char(string="Quotation Color", default="#3498db")
    sales_order_color = fields.Char(string="Sales Order Color", default="#2ecc71")
    cancelled_color = fields.Char(string="Cancelled Color", default="#e74c3c")

    # Fields for date filtering
    time_range = fields.Selection(
        selection=TIME_RANGE_SELECTION,
        string="Time Range",
        default="all_time",
        help="Predefined date filter for the dashboard."
    )
    date_start = fields.Date(string="Start Date")
    date_end = fields.Date(string="End Date")

    icon_image = fields.Binary("Dashboard Image", help="Upload an image to use as the icon for the global dashboard card.", attachment=True)
    record_id_int = fields.Integer(string="Record ID", compute="_compute_record_id_int")

    @api.depends()
    def _compute_record_id_int(self):
        for rec in self:
            rec.record_id_int = rec.id

    @api.model
    def init(self):
        """Ensure a global dashboard record (employee_id=False) exists."""
        self.create_global_dashboard()

    @api.model
    def create_global_dashboard(self):
        global_dashboard = self.search([('employee_id', '=', False)], limit=1)
        if not global_dashboard:
            self.create({'color': "#000000"})
            _logger.info("Global aggregated sales dashboard created.")

    def action_edit_icon(self):
        """Open the form view to edit the global dashboard icon."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Edit Global Dashboard Image'),
            'res_model': 'cancel.sales.dashboard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

    def action_save_icon(self):
        """Save the new icon (already in self.icon_image)."""
        self.ensure_one()
        _logger.info("DEBUG: icon_image size = %s", len(self.icon_image or b''))

        return {'type': 'ir.actions.act_window_close'}
    

    def _get_time_domain(self):
        """
        Build a domain on sale.order.date_order based on time filters.
        Looks at self.time_range, self.date_start, self.date_end, or fallback to context.
        """
        ctx = self.env.context
        time_range = ctx.get('time_range', self.time_range or 'all_time')
        date_start = ctx.get('date_start', self.date_start)
        date_end = ctx.get('date_end', self.date_end)
        domain = []
        today = fields.Date.today()

        if time_range == 'all_time':
            pass
        elif time_range == 'today':
            tomorrow = today + timedelta(days=1)
            domain = [('date_order', '>=', today), ('date_order', '<', tomorrow)]
        elif time_range == 'this_week':
            weekday = today.weekday()  # Monday=0
            start_of_week = today - timedelta(days=weekday)
            end_of_week = start_of_week + timedelta(days=7)
            domain = [('date_order', '>=', start_of_week), ('date_order', '<', end_of_week)]
        elif time_range == 'this_month':
            start_of_month = today.replace(day=1)
            if today.month == 12:
                next_month = today.replace(year=today.year + 1, month=1, day=1)
            else:
                next_month = today.replace(month=today.month + 1, day=1)
            domain = [('date_order', '>=', start_of_month), ('date_order', '<', next_month)]
        elif time_range == 'this_quarter':
            month = today.month
            quarter = (month - 1) // 3 + 1
            start_month = 3 * (quarter - 1) + 1
            start_of_quarter = today.replace(month=start_month, day=1)
            if start_month == 10:
                next_quarter = start_of_quarter.replace(year=start_of_quarter.year + 1, month=1, day=1)
            else:
                next_quarter = start_of_quarter.replace(month=start_month + 3, day=1)
            domain = [('date_order', '>=', start_of_quarter), ('date_order', '<', next_quarter)]
        elif time_range == 'this_year':
            start_of_year = today.replace(month=1, day=1)
            next_year = start_of_year.replace(year=start_of_year.year + 1)
            domain = [('date_order', '>=', start_of_year), ('date_order', '<', next_year)]
        elif time_range == 'custom':
            # Use date_start / date_end
            if date_start:
                domain.append(('date_order', '>=', date_start))
            if date_end:
                domain.append(('date_order', '<=', date_end))

        return domain
    
    def action_open_custom_range_wizard(self):
        self.ensure_one()
        return {
        'type': 'ir.actions.act_window',
        'res_model': 'cancel.sales.date.range.wizard',
        'view_mode': 'form',
        'target': 'new',
        'name': _('Set Custom Date Range'),
        'context': {
            'default_dashboard_id': self.id,
            # If the user has an existing date range, pre-fill it
            'default_start_date': self.date_start,
            'default_end_date': self.date_end,
        },
    }
    @api.depends_context('time_range', 'date_start', 'date_end')
    def _compute_counts(self):
        SaleOrder = self.env['sale.order']
        for record in self:
            # 1) Get the date domain from your custom logic
            date_domain = record._get_time_domain()

            # 2) If there's an employee, add user_id to the domain
            if record.employee_id:
                date_domain.append(('user_id', '=', record.employee_id.id))

            # 3) Use this combined domain to compute each count
            record.draft_count = SaleOrder.search_count(date_domain + [('state', '=', 'draft')])
            record.confirmed_count = SaleOrder.search_count(date_domain + [('state', '=', 'sale')])
            record.cancelled_count = SaleOrder.search_count(date_domain + [('state', '=', 'cancel')])
    def _compute_chart_json(self):
        for record in self:
            data = [
                {"label": _("Quotation"), "value": record.draft_count, "color": record.quotation_color or "#3498db"},
                {"label": _("Sales Order"), "value": record.confirmed_count, "color": record.sales_order_color or "#2ecc71"},
                {"label": _("Cancelled"), "value": record.cancelled_count, "color": record.cancelled_color or "#e74c3c"},
            ]
            chart_data = {
                "values": data,
                "title": _("Sales Order Status Overview"),
                "key": _("Total Orders"),
                "is_sample_data": False,
            }
            record.sales_kanban_bar_chart = json.dumps(chart_data)

    def _compute_sale_bar_html(self):
        for record in self:
            total = record.draft_count + record.confirmed_count + record.cancelled_count
            if total:
                quotation_pct = (record.draft_count / total) * 100
                sales_order_pct = (record.confirmed_count / total) * 100
                cancelled_pct = (record.cancelled_count / total) * 100
            else:
                quotation_pct = sales_order_pct = cancelled_pct = 0
            record.sale_bar_html = f"""
               <div style="display: flex; height: 20px; width: 100%; border: 1px solid #ccc;">
                   <div style="background-color: {'#71639e'}; width: {quotation_pct}%;"></div>
                   <div style="background-color: {record.sales_order_color or '#2ecc71'}; width: {sales_order_pct}%;"></div>
                   <div style="background-color: {record.cancelled_color or '#e74c3c'}; width: {cancelled_pct}%;"></div>
               </div>
               <div style="text-align: center; font-size: 12px; margin-top: 2px;">
                   {_("Quotation")}: {record.draft_count} | {_("Sales Order")}: {record.confirmed_count} | {_("Cancelled")}: {record.cancelled_count}
               </div>
            """

    # (Other action methods for opening records remain unchanged)

    def action_open_draft_records(self):
        domain = self._get_time_domain() + [('state', '=', 'draft')]
        if self.employee_id:
            domain.append(('user_id', '=', self.employee_id.id))
        return {
            'name': _('Quotation Sale Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list',
            'views': [(self.env.ref('zehntech_cancel_sale_orders.view_sale_order_tree_no_bulk_actions').id, 'list')],
            'domain': domain,
            'context': {'create': False, 'dashboard_mode': True},
        }

    def action_open_confirmed_records(self):
        domain = self._get_time_domain() + [('state', '=', 'sale')]
        if self.employee_id:
            domain.append(('user_id', '=', self.employee_id.id))
        return {
            'name': _('Confirmed Sale Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list',
            'views': [(self.env.ref('zehntech_cancel_sale_orders.view_sale_order_tree_no_bulk_actions').id, 'list')],
            'domain': domain,
            'context': {'create': False, 'dashboard_mode': True},
        }

    def action_open_cancelled_records(self):
        domain = self._get_time_domain() + [('state', '=', 'cancel')]
        if self.employee_id:
            domain.append(('user_id', '=', self.employee_id.id))
        return {
            'name': _('Cancelled Sale Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'list',
            'views': [(self.env.ref('zehntech_cancel_sale_orders.view_sale_order_tree_no_bulk_actions').id, 'list')],
            'domain': domain,
            'context': {'create': False, 'dashboard_mode': True},
        }

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model_create_multi
    def create(self, vals_list):
        users = super().create(vals_list)
        dashboards_to_create = []
        for user in users:
            dashboards_to_create.append({
                'employee_id': user.id,
                'color': "#%06x" % (int(user.id) * 56789 % 0xFFFFFF),
            })
        self.env['cancel.sales.dashboard'].create_global_dashboard()
        _logger.info("Creating %s dashboard records for new users.", len(dashboards_to_create))
        self.env['cancel.sales.dashboard'].create(dashboards_to_create)
        return users
    