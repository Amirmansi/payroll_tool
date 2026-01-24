from frappe import _

def get_data():
    return [
        {
            "label": _("Payroll"),
            "items": [
                {
                    "type": "doctype",
                    "name": "Payroll Details View",
                    "description": _("View detailed payroll information for employees"),
                    "onboard": 1,
                }
            ]
        }
    ]
