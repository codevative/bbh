// Copyright (c) 2024, Codevative and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
        frm.set_query(
            "custom_building",
            "items",
            function (frm, cdt, cdn) {
                return {
                    filters: {
                        project: frm.project,
                        has_floors: 1
                    },
                };
            }
        );

        frm.set_query(
            'custom_floor',
            'items',
            function (doc, cdt, cdn) {
                let d = locals[cdt][cdn];
                return {
                    filters: {
                        project: frm.project,
                        building: d.custom_building,
                        has_units: 1
                    }
                };
            }
        );

        frm.set_query(
            'custom_unit',
            'items',
            function (doc, cdt, cdn) {
                let d = locals[cdt][cdn];
                return {
                    filters: {
                        project: frm.project,
                        building: d.custom_building,
                        floor_no: d.custom_floor,
                        linked_item: ['!=', ''],
                        status: 'Available'
                    }
                };
            }
        );

        frm.add_custom_button(__('Create Payment Schedule'), function () {
            let dialog = new frappe.ui.Dialog({
                title: __("Create Payment Schedule"),
                fields: [
                    {
                        fieldname: 'child_table',
                        fieldtype: 'Table',
                        label: 'Payment Schedule',
                        fields: [
                            {
                                fieldtype: 'Int',
                                fieldname: 'payment_no',
                                label: 'Payment No',
                                in_list_view: 1
                            },
                            {
                                fieldtype: 'Date',
                                fieldname: 'payment_date',
                                label: 'Payment Date',
                                in_list_view: 1
                            },
                            {
                                fieldtype: 'Currency',
                                fieldname: 'payment_amount',
                                label: 'Payment Amount',
                                in_list_view: 1
                            },
                        ],
                        data: [],
                        get_data: function() {
                            return this.data;
                        }
                    }
                ],
                primary_action_label: __('Create'),
                primary_action(values) {
                    frappe.call({
						method: 'bbh.utils.create_terms',
                        args: { invoice: frm.doc.name, data: values },
                        callback: function (r) {
                            if(r.message) {
                                // Update the payment_terms_template field
                                console.log(r.message);
                                frm.set_value('payment_terms_template', r.message);

                                // Optionally, refresh the payment_schedule to reflect the changes
                                frm.refresh_field('payment_schedule');

                                dialog.hide();

                            }
                        }
                    });
                }
            });

            dialog.show();
        });
    },

    project: function (frm) {
        frm.set_query(
            "custom_building",
            "items",
            function (frm, cdt, cdn) {
                return {
                    filters: {
                        project: frm.custom_project,
                    },
                };
            }
        );
    },
});