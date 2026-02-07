// Copyright (c) 2024, Amir Mansi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Details View', {
    refresh: function(frm) {
        if (frm.doc.payroll_entry && !frm.is_new()) {
            // زر التحديث
            frm.add_custom_button(__('تحديث البيانات'), function() {
                frappe.show_alert({
                    message: __('جاري تحديث البيانات...'),
                    indicator: 'blue'
                }, 3);
                
                frm.save().then(() => {
                    frappe.show_alert({
                        message: __('تم تحديث البيانات بنجاح'),
                        indicator: 'green'
                    }, 5);
                    frm.refresh();
                });
            }).addClass('btn-primary');
            
            // زر التصدير إلى Excel
            frm.add_custom_button(__('تصدير إلى Excel'), function() {
                frappe.call({
                    method: 'payroll_tool.payroll_tool.doctype.payroll_details_view.payroll_details_view.export_to_excel',
                    args: {
                        docname: frm.doc.name
                    },
                    callback: function(r) {
                        if (r.message) {
                            frappe.show_alert({
                                message: __('تم التصدير بنجاح'),
                                indicator: 'green'
                            }, 3);
                        }
                    }
                });
            }, __('Actions'));
            
            // زر الطباعة
            frm.add_custom_button(__('طباعة التقرير'), function() {
                window.print();
            }, __('Actions'));
        }
        
        // تخصيص عرض الجدول
        if (frm.doc.employees && frm.doc.employees.length > 0) {
            frm.fields_dict.employees.grid.wrapper.find('.grid-body').css({
                'max-height': 'none'
            });
            
            // إضافة إحصائيات سريعة
            show_summary_stats(frm);
        }
    },
    
    payroll_entry: function(frm) {
        if (frm.doc.payroll_entry) {
            frappe.show_alert({
                message: __('جاري تحميل بيانات الرواتب...'),
                indicator: 'blue'
            }, 3);
            
            frm.save().then(() => {
                let draft_count = 0;
                let submitted_count = 0;
                
                frm.doc.employees.forEach(emp => {
                    // يمكنك إضافة منطق للتمييز بين Draft و Submitted
                });
                
                frappe.show_alert({
                    message: __('تم تحميل {0} موظف بنجاح', [frm.doc.employees.length]),
                    indicator: 'green'
                }, 5);
                frm.refresh();
            });
        }
    },
    
    onload: function(frm) {
        // فلتر Payroll Entry (Draft + Submitted)
        frm.set_query('payroll_entry', function() {
            return {
                filters: {
                    'docstatus': ['in', [0, 1]]
                }
            };
        });
    }
});

// دالة لعرض إحصائيات سريعة
function show_summary_stats(frm) {
    if (!frm.doc.employees || frm.doc.employees.length === 0) return;
    
    let total_gross = 0;
    let total_deductions = 0;
    let total_net = 0;
    
    frm.doc.employees.forEach(emp => {
        total_gross += emp.gross_pay || 0;
        total_deductions += emp.total_deduction || 0;
        total_net += emp.net_pay || 0;
    });
    
    let html = `
        <div style="padding: 15px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; border-radius: 8px; margin: 15px 0;">
            <h4 style="margin: 0 0 10px 0; text-align: center;">📊 ملخص الرواتب</h4>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                <div style="text-align: center;">
                    <div style="font-size: 12px; opacity: 0.9;">عدد الموظفين</div>
                    <div style="font-size: 24px; font-weight: bold;">${frm.doc.employees.length}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 12px; opacity: 0.9;">إجمالي الاستحقاقات</div>
                    <div style="font-size: 24px; font-weight: bold;">${format_currency(total_gross)}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 12px; opacity: 0.9;">إجمالي المستقطعات</div>
                    <div style="font-size: 24px; font-weight: bold;">${format_currency(total_deductions)}</div>
                </div>
                <div style="text-align: center;">
                    <div style="font-size: 12px; opacity: 0.9;">صافي الرواتب</div>
                    <div style="font-size: 24px; font-weight: bold;">${format_currency(total_net)}</div>
                </div>
            </div>
        </div>
    `;
    
    frm.set_df_property('employees', 'description', html);
}

// دالة لتنسيق العملة
function format_currency(value) {
    return frappe.format(value, {fieldtype: 'Currency'});
}

// تخصيص عرض الجدول
frappe.ui.form.on('Payroll Details Employee', {
    employees_add: function(frm, cdt, cdn) {
        // يمكنك إضافة منطق عند إضافة صف جديد
    }
});
