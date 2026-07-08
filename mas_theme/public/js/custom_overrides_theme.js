frappe.ready(function() {
    // Hide sidebar by default
    frappe.ui.toolbar.toggle_sidebar(false);
    
    // Optional: Save preference for all pages
    frappe.boot.sidebar_hidden = true;
});