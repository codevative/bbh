// Copyright (c) 2024, Codevative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Floor', {

	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Create Units'), function () {
				let dialog = new frappe.ui.Dialog({
					title: __("Create Units"),
					fields: [
						{ fieldname: 'unit_type', label: __('Unit Type'), fieldtype: 'Link', options: 'Unit Type' },
						{ fieldname: 'num_units', label: __('Number of Units'), fieldtype: 'Int' },
						{ fieldname: 'col_brk', fieldtype: 'Column Break' },
						{ fieldname: 'unit_size_sq_m', label: __('Unit Size Sq. M'), fieldtype: 'Float' },
						{ fieldname: 'price', label: __('Price'), fieldtype: 'Currency' },
					],
					primary_action_label: __('Create'),
					primary_action(values) {
						frappe.call({
							method: 'bbh.utils.create_units_for_floor',
							args: { floor: frm.doc.name, data: values },
							callback: function (r) {
								dialog.hide();
							}
						});
					}
				});

				dialog.show();
			});
		}
	}
});
