// Common JavaScript functions for Payroll Tool
// يمكن استخدامها في جميع أنحاء التطبيق

frappe.provide("payroll_tool");

payroll_tool.utils = {
    // دالة لتنسيق العملة
    format_currency: function(value) {
        return frappe.format_value(value, {fieldtype: 'Currency'});
    },
    
    // دالة للحصول على لون حسب القيمة
    get_indicator_color: function(net_pay) {
        if (net_pay > 10000) {
            return 'green';
        } else if (net_pay > 5000) {
            return 'blue';
        } else {
            return 'orange';
        }
    },
    
    // دالة لعرض رسالة نجاح
    show_success: function(message) {
        frappe.show_alert({
            message: __(message),
            indicator: 'green'
        }, 5);
    },
    
    // دالة لعرض رسالة خطأ
    show_error: function(message) {
        frappe.show_alert({
            message: __(message),
            indicator: 'red'
        }, 5);
    },
    
    // دالة لطباعة التقرير
    print_report: function(frm) {
        if (!frm.doc.name) {
            frappe.msgprint(__('الرجاء حفظ المستند أولاً'));
            return;
        }
        
        window.print();
    }
};

// إضافة أيقونة مخصصة للـ DocType في القائمة
$(document).on('app_ready', function() {
    // يمكنك إضافة تخصيصات عامة هنا
});
