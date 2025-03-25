{
    "name": "Product Sale Price Limit",

    'version': "16.0.2.0",

    'summary': 'Set and manage minimum and maximum sale prices for products, with user-specific price adjustments. set max price on product, price, limit, price limits, sale limit, product sale price, product sale price',
    'description': """
    Product Sale Price Limit in Odoo

    The Product Sale Price Limit app allows businesses to set minimum and maximum sale price boundaries for their products, ensuring that pricing remains within a defined range. This app provides flexibility by enabling specific users to override these limits based on their roles and permissions. Ideal for maintaining pricing control, this app ensures compliance with business policies while offering flexibility where needed.

    Key Features:
    - Minimum and Maximum Price Limits: Set both minimum and maximum sale price limits for each product variant, preventing pricing from going beyond acceptable thresholds.
    - User-Specific Price Overrides: Users with the appropriate access rights can override the defined sale price limits, providing flexibility in price adjustments while maintaining control over pricing policies.
    - Validation for Price Compliance: If a user attempts to enter a price outside the defined limits, the system displays a validation error, ensuring that prices are within the acceptable range.
    - Quotation View with Price Limits: In the quotation view, users can enter a unit price, which will automatically show the minimum and maximum price limits for reference. This ensures that the user is aware of the price constraints while creating or confirming a quotation.
    - Access Control for Price Changes: Users with the “Confirm Product Sale Price” access right can bypass the price limits, enabling them to set custom prices without facing validation errors.
    - Seamless Integration with Odoo Sales: Fully integrated with Odoo’s Sales module, ensuring a smooth workflow for sales quotations, price entry, and validation.

    How It Works:
    1. Go to Sales -> Products -> Product Variants to add the minimum and maximum price for each product variant.
    2. In the Quotation view, when a user enters a unit price that exceeds the set limits, the system will show the minimum and maximum price limits for the product.
    3. If a user tries to confirm a quotation with a price outside the defined limits, the system will raise a validation error.
    4. Users with the “Confirm Product Sale Price” permission can override these limits and set prices freely without receiving validation warnings.
    5. Easily manage and enforce price limits within your business policies while offering flexibility for specific roles in your team.

    This app ensures that product pricing is controlled according to company guidelines, with flexibility for users who need to make exceptions. Whether you want to enforce pricing consistency or allow for custom adjustments by certain users, the Product Sale Price Limit app offers a robust solution to manage your sales pricing effectively.

    For more details, guidance, or support, visit our website at https://inkerp.com or contact us via email at team@inkerp.com.
    """,

    'author': 'INKERP',
    
    'website': "http://www.inkerp.com",

    "depends": ["product", "sale"],

    "data": [
        "views/product_product_view.xml",
        "security/security.xml",
        "views/sale_order_view.xml",
    ],

    'images': ['static/description/banner.gif'],
    'license': "OPL-1",
    'installable': True,
    'application': True,
    'auto_install': False,

}
