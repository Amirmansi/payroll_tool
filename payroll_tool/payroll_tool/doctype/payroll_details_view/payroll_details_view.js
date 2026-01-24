// Copyright (c) 2024, Your Company and contributors
// For license information, please see license.txt

frappe.ui.form.on('Payroll Details View', {
    refresh: function(frm) {
        // إضافة زر التحديث
        if (frm.doc.payroll_entry && !frm.is_new()) {
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
            
            // زر طباعة مخصص
            frm.add_custom_button(__('طباعة التقرير'), function() {
                window.print();
            }, __('Print'));
        }
        
        // تخصيص عرض الجدول
        if (frm.doc.employees && frm.doc.employees.length > 0) {
            frm.fields_dict.employees.grid.wrapper.find('.grid-body').css({
                'max-height': 'none'
            });
        }
    },
    
    payroll_entry: function(frm) {
        if (frm.doc.payroll_entry) {
            // عرض رسالة تحميل
            frappe.show_alert({
                message: __('جاري تحميل بيانات الرواتب...'),
                indicator: 'blue'
            }, 3);
            
            // حفظ المستند لتحميل البيانات
            frm.save().then(() => {
                frappe.show_alert({
                    message: __('تم تحميل {0} موظف بنجاح', [frm.doc.employees.length]),
                    indicator: 'green'
                }, 5);
                frm.refresh();
            });
        }
    },
    
    onload: function(frm) {
        // تخصيص الفلاتر للـ Payroll Entry
        frm.set_query('payroll_entry', function() {
            return {
                filters: {
                    'docstatus': 1  // فقط المرحلة
                }
            };
        });
    }
});

frappe.ui.form.on('Payroll Details Employee', {
    employee: function(frm, cdt, cdn) {
        // يمكنك إضافة وظائف مخصصة للـ child table هنا
    }
});
