# Copyright (c) 2024, Your Company and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class PayrollDetailsView(Document):
    def validate(self):
        """التحقق من صحة البيانات قبل الحفظ"""
        if self.payroll_entry:
            # التحقق من أن Payroll Entry مرحل
            payroll_doc = frappe.get_doc("Payroll Entry", self.payroll_entry)
            if payroll_doc.docstatus != 1:
                frappe.throw(_("الرجاء اختيار Payroll Entry مرحل (Submitted)"))
            
            # تحميل بيانات الموظفين
            self.load_employee_data()
    
    def before_save(self):
        """قبل الحفظ"""
        pass
    
    def on_submit(self):
        """عند الترحيل"""
        pass
    
    def on_cancel(self):
        """عند الإلغاء"""
        pass
    
    def load_employee_data(self):
        """تحميل بيانات الموظفين من كشوف الرواتب"""
        # مسح البيانات القديمة
        self.employees = []
        
        # جلب جميع Salary Slips المرتبطة
        salary_slips = frappe.get_all(
            "Salary Slip",
            filters={
                "payroll_entry": self.payroll_entry,
                "docstatus": 0
            },
            fields=["name"],
            order_by="employee_name asc"
        )
        
        if not salary_slips:
            frappe.msgprint(
                _("لا توجد كشوف رواتب مرحلة لهذا الـ Payroll Entry"),
                alert=True,
                indicator="orange"
            )
            return
        
        # معالجة كل كشف راتب
        for slip in salary_slips:
            salary_slip = frappe.get_doc("Salary Slip", slip.name)
            
            # بناء HTML لعرض التفاصيل
            salary_html = self.build_salary_slip_html(salary_slip)
            
            # إضافة صف جديد للموظف
            self.append("employees", {
                "employee": salary_slip.employee,
                "employee_name": salary_slip.employee_name,
                "department": salary_slip.department,
                "designation": salary_slip.designation,
                "gross_pay": salary_slip.gross_pay,
                "total_deduction": salary_slip.total_deduction,
                "net_pay": salary_slip.net_pay,
                "payment_days": salary_slip.payment_days or 0,
                "leave_without_pay": salary_slip.leave_without_pay or 0,
                "absent_days": salary_slip.absent_days or 0,
                "salary_slip_html": salary_html,
                "salary_slip_ref": salary_slip.name
            })
        
        # عرض رسالة نجاح
        frappe.msgprint(
            _("تم تحميل بيانات {0} موظف بنجاح").format(len(self.employees)),
            alert=True,
            indicator="green"
        )
    
    def build_salary_slip_html(self, salary_slip):
        """بناء HTML احترافي لعرض تفاصيل كشف الراتب"""
        
        html = f"""
        <div style="padding: 15px; background: #f9f9f9; border-radius: 8px; margin: 10px 0; font-family: Arial, sans-serif;">
            <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                <!-- قسم الاستحقاقات -->
                <div style="flex: 1; min-width: 300px;">
                    <h4 style="color: #2e7d32; border-bottom: 2px solid #2e7d32; padding-bottom: 5px; margin: 0 0 10px 0;">
                        💰 الاستحقاقات (Earnings)
                    </h4>
                    <table style="width: 100%; margin-top: 10px; border-collapse: collapse; font-size: 13px;">
                        <thead>
                            <tr style="background: #e8f5e9;">
                                <th style="padding: 8px; text-align: right; border: 1px solid #ddd;">المكون</th>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; width: 120px;">المبلغ</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # إضافة الاستحقاقات
        total_earnings = 0
        if salary_slip.earnings:
            for earning in salary_slip.earnings:
                amount_formatted = frappe.format_value(earning.amount, {'fieldtype': 'Currency'})
                html += f"""
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">
                                    {earning.salary_component}
                                </td>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: left; font-weight: bold;">
                                    {amount_formatted}
                                </td>
                            </tr>
                """
                total_earnings += earning.amount
        else:
            html += """
                            <tr>
                                <td colspan="2" style="padding: 8px; text-align: center; color: #999;">
                                    لا توجد استحقاقات
                                </td>
                            </tr>
            """
        
        total_formatted = frappe.format_value(total_earnings, {'fieldtype': 'Currency'})
        html += f"""
                            <tr style="background: #c8e6c9; font-weight: bold;">
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">الإجمالي</td>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: left;">
                                    {total_formatted}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                
                <!-- قسم المستقطعات -->
                <div style="flex: 1; min-width: 300px;">
                    <h4 style="color: #c62828; border-bottom: 2px solid #c62828; padding-bottom: 5px; margin: 0 0 10px 0;">
                        📉 المستقطعات (Deductions)
                    </h4>
                    <table style="width: 100%; margin-top: 10px; border-collapse: collapse; font-size: 13px;">
                        <thead>
                            <tr style="background: #ffebee;">
                                <th style="padding: 8px; text-align: right; border: 1px solid #ddd;">المكون</th>
                                <th style="padding: 8px; text-align: left; border: 1px solid #ddd; width: 120px;">المبلغ</th>
                            </tr>
                        </thead>
                        <tbody>
        """
        
        # إضافة المستقطعات
        total_deductions = 0
        if salary_slip.deductions:
            for deduction in salary_slip.deductions:
                amount_formatted = frappe.format_value(deduction.amount, {'fieldtype': 'Currency'})
                html += f"""
                            <tr>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">
                                    {deduction.salary_component}
                                </td>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: left; font-weight: bold;">
                                    {amount_formatted}
                                </td>
                            </tr>
                """
                total_deductions += deduction.amount
        else:
            html += """
                            <tr>
                                <td colspan="2" style="padding: 8px; text-align: center; color: #999;">
                                    لا توجد مستقطعات
                                </td>
                            </tr>
            """
        
        deduction_formatted = frappe.format_value(total_deductions, {'fieldtype': 'Currency'})
        html += f"""
                            <tr style="background: #ffcdd2; font-weight: bold;">
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: right;">الإجمالي</td>
                                <td style="padding: 8px; border: 1px solid #ddd; text-align: left;">
                                    {deduction_formatted}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            
            <!-- معلومات الحضور -->
            <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 5px; border: 1px solid #e0e0e0;">
                <h4 style="color: #1565c0; margin: 0 0 10px 0; font-size: 14px;">📅 معلومات الحضور</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; font-size: 13px;">
                    <div>
                        <span style="color: #666;">أيام العمل:</span>
                        <strong style="margin-right: 5px; color: #333;">{salary_slip.payment_days or 0}</strong>
                    </div>
                    <div>
                        <span style="color: #666;">إجازات بدون راتب:</span>
                        <strong style="margin-right: 5px; color: #333;">{salary_slip.leave_without_pay or 0}</strong>
                    </div>
                    <div>
                        <span style="color: #666;">أيام الغياب:</span>
                        <strong style="margin-right: 5px; color: #333;">{salary_slip.absent_days or 0}</strong>
                    </div>
                </div>
            </div>
            
            <!-- الصافي النهائي -->
            <div style="margin-top: 15px; padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        color: white; border-radius: 8px; text-align: center;">
                <h3 style="margin: 0; font-size: 16px; font-weight: normal;">💵 صافي الراتب (Net Pay)</h3>
                <div style="font-size: 28px; font-weight: bold; margin-top: 10px;">
                    {frappe.format_value(salary_slip.net_pay, {'fieldtype': 'Currency'})}
                </div>
            </div>
            
            <!-- رابط كشف الراتب -->
            <div style="margin-top: 15px; text-align: center;">
                <a href="/app/salary-slip/{salary_slip.name}" target="_blank" 
                   style="display: inline-block; padding: 8px 20px; background: #1976d2; color: white; 
                          text-decoration: none; border-radius: 4px; font-size: 13px;">
                    📄 عرض كشف الراتب الكامل
                </a>
            </div>
        </div>
        """
        
        return html


# Whitelisted methods (يمكن استدعاؤها من JavaScript)
@frappe.whitelist()
def refresh_employee_data(docname):
    """تحديث بيانات الموظفين يدوياً"""
    doc = frappe.get_doc("Payroll Details View", docname)
    doc.load_employee_data()
    doc.save()
    return {"message": _("تم تحديث البيانات بنجاح"), "employees_count": len(doc.employees)}
