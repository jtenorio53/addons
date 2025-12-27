# -*- coding: utf-8 -*-
# Part of Creyox technologies.

{
    "name": "Sale Multi Warehouse | Multi Warehouse | MultiWarehouse",
    "summary": """Sale Multi Warehouse""",
    "description": """Sale Multi Warehouse""",
    "category": "Sales",
    "author": "Creyox Technologies",
    "website": "https://creyox.com",
    "depends": ["base", "stock", "sale_management"],
    "vesion": "16.0",
    "price": 0,
    "currency": "USD",
    "license": "AGPL-3",
    "images": ["static/description/banner.png"],
    "data": [
        "views/sale_order_views.xml",
        "views/product_template_view.xml",
        "views/product_product_view.xml",
        "views/sale_config_settings_views.xml",
    ],
    "installable": True,
    "application": True,
    "auto_install": False,
}
