// Copyright (c) 2024, Codevative and contributors
// For license information, please see license.txt


// Copyright (c) 2020, 9T9IT and contributors
// For license information, please see license.txt

 {% include 'bbh/bbh property management/doctype/unit maintenance/unit maintenance dialog.js' %}

frappe.ui.form.on("Unit Maintenance", {
    	refresh(frm) {
        _set_custom_buttons(frm);

            // Make fields read-only if the document is submitted
            if (frm.doc.docstatus === 0 && !frm.is_new()) {
                frm.set_df_property('project', 'read_only', 1);
                frm.set_df_property('building', 'read_only', 1);
                frm.set_df_property('floor', 'read_only', 1);
                frm.set_df_property('unit', 'read_only', 1);
            }
    
            frm.set_query("building", function () {
                let project = "";
                if (frm.doc.project) {
                    project = frm.doc.project;
                }
                return {
                    filters: {
                        project: project,
                        has_floors: 1,
                    },
                };
            });
    
            frm.set_query("floor", function () {
                let building = "";
                if (frm.doc.building) {
                    building = frm.doc.building;
                }
                return {
                    filters: {
                        project: frm.doc.project,
                        building: building,
                        has_units: 1,
                    },
                };
            });
    
            frm.set_query("unit", function () {
                let floor_no = "";
                if (frm.doc.floor) {
                    floor_no = frm.doc.floor;
                }
                return {
                    filters: {
                        floor_no: floor_no,
                        building: frm.doc.building,
                        project: frm.doc.project,
                        status: "Available",
                    },
                };
            });
        },
	
	tenant: function(frm) {
        _set_tenant_details(frm);
	}
});

function _set_custom_buttons(frm) {
    if (frm.doc.__islocal) {
        return;
    }
    frm.add_custom_button(__('Close'), async function() {
        await frm.call('close_issue');
        frm.savesubmit();
    });
    frm.add_custom_button(__('Log'), async function() {
        const { datetime, status, description } = await prompt_log();
        await frm.call('log_history', { datetime, status, description });
        frm.save();
    });

    // Add
    frm.add_custom_button(__('Expense Claim'), function() {
        frappe.route_options = {
            'custom_unit_maintenance': frm.doc.name, 
            'employee': frm.doc.assigned_to,
        };
        frappe.new_doc('Expense Claim');
    }, __('Add'));
    frm.add_custom_button(__('Material Request'), function() {
        frappe.route_options = {
            'custom_unit_maintenance': frm.doc.name,
            'requested_by': frm.doc.assigned_to,
        };
        frappe.new_doc('Material Request');
    }, __('Add'));
    frm.add_custom_button(__('Asset Repair'), function() {
        frappe.route_options = {
            'custom_unit_maintenance': frm.doc.name,
            'assign_to': frm.doc.created_by,
        };
        frappe.new_doc('Asset Repair');
    }, __('Add'));
}

async function _set_tenant_details(frm) {
    const tenant = await frappe.db.get_doc('Tenant', frm.doc.tenant);
    frm.set_value('tenant_name', `${tenant.first_name} ${tenant.last_name}`);
    frm.set_value('email', tenant.email);
}
