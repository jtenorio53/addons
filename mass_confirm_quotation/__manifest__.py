# -*- coding: utf-8 -*-
# Copyright (C) Quocent Pvt. Ltd.
# All Rights Reserved

{
    "name": "Mass Confirm Sale Quotation",
    "version": "16.0.1.0.0",
    "summary": "This app enables efficient to confirm multiple quotations in bulk, streamlining the process for efficient order management.",
    "category": "Update Tool",
    "license": "LGPL-3",
    "author": "Quocent Pvt. Ltd.",
    "website": "https://www.quocent.com",
    "description": "This app facilitates users to select confirm multiple quotations simultaneously, reducing manual effort and improving efficiency in order processing.",
    "depends": ["base","sale_management","stock"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/mass_confirm_quotation_wizard.xml",
    ],
    "images": [
        "static/description/banner.png",
    ],
    "installable": True,
}
