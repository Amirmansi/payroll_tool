import frappe
from frappe.model.document import Document
from frappe import _

class PayrollDetailsView(Document):
    def validate(self):
        """التحقق من صحة البيانات قبل الحفظ"""
        if self.payroll_entry:
            # تحميل بيانات الموظفين (Draft و Submitted)
            self.load_employee_data()
    
    def load_employee_data(self):
        """تحميل بيانات الموظفين من كشوف الرواتب"""
        # مسح البيانات القديمة
        self.employees = []
        
        # جلب جميع Salary Slips المرتبطة (Draft + Submitted)
        salary_slips = frappe.get_all(
            "Salary Slip",
            filters={
                "payroll_entry": self.payroll_entry,
                "docstatus": ["in", [0, 1]]  # 0 = Draft, 1 = Submitted
            },
            fields=["name", "docstatus"],
            order_by="employee_name asc"
        )
        
        if not salary_slips:
            frappe.msgprint(
                _("لا توجد كشوف رواتب لهذا الـ Payroll Entry"),
                alert=True,
                indicator="orange"
            )
            return
        
        # معالجة كل كشف راتب
        for slip in salary_slips:
            salary_slip = frappe.get_doc("Salary Slip", slip.name)
            
            # استخراج بيانات الموظف
            employee_data = self.extract_employee_data(salary_slip)
            
            # إضافة صف جديد للموظف
            self.append("employees", employee_data)
        
        # عرض رسالة نجاح
        draft_count = sum(1 for s in salary_slips if s.docstatus == 0)
        submitted_count = sum(1 for s in salary_slips if s.docstatus == 1)
        
        frappe.msgprint(
            _("تم تحميل بيانات {0} موظف ({1} مرحل، {2} مسودة)").format(
                len(self.employees), submitted_count, draft_count
            ),
            alert=True,
            indicator="green"
        )
    
    def extract_employee_data(self, salary_slip):
        """استخراج بيانات الموظف من كشف الراتب"""
        
        # الحصول على معلومات البنك من Employee
        employee_doc = frappe.get_doc("Employee", salary_slip.employee)
        bank_account_no = ""
        bank_name = ""
        
        if employee_doc.bank_ac_no:
            bank_account_no = employee_doc.bank_ac_no
        if employee_doc.bank_name:
            bank_name = employee_doc.bank_name
        
        # خريطة المكونات -ربط اسم المكون بالحقل
        component_mapping = {
            # الاستحقاقات
            "الراتب الاساسي - تشغيلي": "basic_salary_operational",
            "الراتب الأساسي - تشغيلي": "basic_salary_operational",
            "بدلات أخرى تشغيلى": "other_allowances_operational",
            "بدل السكن - تشغيلي": "housing_allowance_operational",
            "بدل نقل - تشغيلي": "transport_allowance_operational",
            "بدلات أخرى تشغيلي": "other_operational_allowances",
            "الراتب الاساسي - اداري": "basic_salary_admin",
            "الراتب الأساسي - اداري": "basic_salary_admin",
            "استحقاقات اخرى - تشغيلى": "other_earnings_operational",
            "بدل السكن - اداري": "housing_allowance_admin",
            "بدل نقل - اداري": "transport_allowance_admin",
            "بدلات أخرى إدارى": "other_allowances_admin",
            "استحقاقات اخرى - ادارى": "other_earnings_admin",
            
            # المستقطعات
            "خصم سلفة": "loan_deduction",
            "خصم غياب - تشغيلي": "absence_deduction_operational",
            "خصم تامينات اجتماعية": "social_insurance_deduction",
            "تأمينات إجتماعيه تشغيلى": "social_insurance_deduction",
            "جزاءات إداريه - تشغيلي": "administrative_penalties_operational",
            "خصم اخرى -تشغيلى": "other_deduction_operational",
            "خصم أخرى اداري": "other_deduction_admin",
            "خصم اخرى - ادارى": "other_deduction_admin",
            "سداد القروض": "loan_repayment",
            "خصم غياب - اداري": "absence_deduction_admin",
            "غياب إدارى": "absence_deduction_admin",
            "جزاءات إداريه - اداري": "administrative_penalties_admin",
            "جزاءات إداريه  - اداري": "administrative_penalties_admin",
        }
        
        # تهيئة البيانات
        employee_row = {
            "employee": salary_slip.employee,
            "employee_name": salary_slip.employee_name,
            "bank_account_no": bank_account_no,
            "bank_name": bank_name,
            "department": salary_slip.department,
            "designation": salary_slip.designation,
            "gross_pay": salary_slip.gross_pay,
            "total_deduction": salary_slip.total_deduction,
            "net_pay": salary_slip.net_pay,
            "payment_days": salary_slip.payment_days or 0,
            "leave_without_pay": salary_slip.leave_without_pay or 0,
            "absent_days": salary_slip.absent_days or 0,
            "salary_slip_ref": salary_slip.name,
        }
        
        # معالجة الاستحقاقات
        if salary_slip.earnings:
            for earning in salary_slip.earnings:
                component_name = earning.salary_component
                if component_name in component_mapping:
                    field_name = component_mapping[component_name]
                    employee_row[field_name] = earning.amount
        
        # معالجة المستقطعات
        if salary_slip.deductions:
            for deduction in salary_slip.deductions:
                component_name = deduction.salary_component
                if component_name in component_mapping:
                    field_name = component_mapping[component_name]
                    employee_row[field_name] = deduction.amount
        
        return employee_row


@frappe.whitelist()
def refresh_employee_data(docname):
    """تحديث بيانات الموظفين يدوياً"""
    doc = frappe.get_doc("Payroll Details View", docname)
    doc.load_employee_data()
    doc.save()
    return {
        "message": _("تم تحديث البيانات بنجاح"), 
        "employees_count": len(doc.employees)
    }


@frappe.whitelist()
def export_to_excel(docname):
    """تصدير البيانات إلى Excel"""
    from frappe.utils.xlsxutils import make_xlsx
    
    doc = frappe.get_doc("Payroll Details View", docname)
    
    # إعداد البيانات للتصدير
    data = []
    
    # العناوين
    headers = [
        "الموظف", "اسم الموظف", "Bank A/C No.", "Bank Name", "المناصب",
        "الراتب الأساسي - تشغيلي", "بدلات أخرى تشغيلى", "بدل السكن - تشغيلي",
        "بدل نقل - تشغيلي", "بدلات أخرى تشغيلي", "الراتب الأساسي - اداري",
        "استحقاقات اخرى - تشغيلى", "إجمالي الأجور",
        "خصم سلفة", "خصم غياب - تشغيلي", "خصم تامينات اجتماعية",
        "جزاءات إداريه - تشغيلي", "خصم اخرى -تشغيلى", "خصم أخرى اداري",
        "سداد القروض", "مجموع الخصم", "صافي الراتب", "ملاحظات"
    ]
    data.append(headers)
    
    # البيانات
    for emp in doc.employees:
        row = [
            emp.employee,
            emp.employee_name,
            emp.bank_account_no or "",
            emp.bank_name or "",
            emp.designation or "",
            emp.basic_salary_operational or 0,
            emp.other_allowances_operational or 0,
            emp.housing_allowance_operational or 0,
            emp.transport_allowance_operational or 0,
            emp.other_operational_allowances or 0,
            emp.basic_salary_admin or 0,
            emp.other_earnings_operational or 0,
            emp.gross_pay or 0,
            emp.loan_deduction or 0,
            emp.absence_deduction_operational or 0,
            emp.social_insurance_deduction or 0,
            emp.administrative_penalties_operational or 0,
            emp.other_deduction_operational or 0,
            emp.other_deduction_admin or 0,
            emp.loan_repayment or 0,
            emp.total_deduction or 0,
            emp.net_pay or 0,
            emp.notes or ""
        ]
        data.append(row)
    
    # إنشاء ملف Excel
    xlsx_file = make_xlsx(data, "Payroll Details")
    
    frappe.response['filename'] = f'payroll_details_{docname}.xlsx'
    frappe.response['filecontent'] = xlsx_file.getvalue()
    frappe.response['type'] = 'binary'
ENDOFPYTHON
