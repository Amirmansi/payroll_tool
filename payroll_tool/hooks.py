# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "payroll_tool"
app_title = "Payroll Tool"
app_publisher = "Your Company Name"
app_description = "Advanced Payroll Details Viewer with comprehensive salary breakdown"
app_icon = "octicon octicon-file-directory"
app_color = "grey"
app_email = "your-email@company.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/payroll_tool/css/payroll_tool.css"
app_include_js = "/assets/payroll_tool/js/payroll_tool_common.js"

# include js in doctype views
doctype_js = {
    "Payroll Details View": "payroll_tool/doctype/payroll_details_view/payroll_details_view.js",
    "Payroll Details Employee": "payroll_tool/doctype/payroll_details_employee/payroll_details_employee.js"
}

# Document Events
# ---------------
# احذف أو علق هذا القسم لأن الدوال موجودة في validate method مباشرة
# doc_events = {
#     "Payroll Details View": {
#         "validate": "payroll_tool.payroll_tool.doctype.payroll_details_view.payroll_details_view.validate_payroll_entry",
#     }
# }

# Fixtures
fixtures = []