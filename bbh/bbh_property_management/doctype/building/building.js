// Copyright (c) 2024, Codevative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Building', {
	refresh(frm) {
		if (!frm.is_new()) {
			frm.add_custom_button(__('Create Floors'), function () {
				let dialog = new frappe.ui.Dialog({
					title: __("Create Floors"),
					fields: [
						{ fieldname: 'no_of_floors', label: __('Number of Floors'), fieldtype: 'Int' },
						{ fieldname: 'col_brk', fieldtype: 'Column Break' },
						{ fieldname: 'total_area', label: __('Total Area Sq. M'), fieldtype: 'Float' },
					],
					primary_action_label: __('Create'),
					primary_action(values) {
						frappe.call({
							method: 'bbh.utils.create_floors_for_buildings',
							args: { building: frm.doc.name, data: values },
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
