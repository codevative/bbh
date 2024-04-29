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
    
            frm.set_query(
                "custom_floor",
                function (doc) {
                    return {
                        filters: {
                            project: doc.project,
                            building: frm.custom_building,
                            has_units: 1
                        }
                    };
                }
            );
        
        if (!frm.is_new() && frm.doc.docstatus == 0) {
            frm.add_custom_button(__('Create Payment Schedule'), function () {

                if (frm.doc.payment_terms_template && frm.doc.payment_terms_template !== '') {
                    frappe.throw(__('Payment Terms already exists for this Invoice, Please remove template if you would like to change terms.'));
                    return; // Stop further execution
                }
                let dialog = new frappe.ui.Dialog({
                    title: __("Create Payment Schedule"),
                    fields: [
                        {
                            fieldname: 'child_table',
                            fieldtype: 'Table',
                            label: 'Payment Schedule',
                            fields: [
                                {
                                    fieldtype: 'Link',
                                    fieldname: 'mode_of_payment',
                                    options: 'Mode of Payment',
                                    label: 'Payment Type',
                                    in_list_view: 1
                                },
                                {
                                    fieldtype: 'Int',
                                    fieldname: 'payment_no',
                                    label: 'Payment Ref #',
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
                            get_data: function () {
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
                                if (r.message) {
                                    frm.set_value('payment_terms_template', r.message);

                                    frm.refresh_field('payment_schedule');

                                    dialog.hide();

                                }
                            }
                        });
                    }
                });
                dialog.show();
            });
        }
        setTimeout(() => {
            frm.remove_custom_button('Sales Order','Get Items From');
            frm.remove_custom_button('Delivery Note','Get Items From');
            frm.remove_custom_button('Quotation','Get Items From');
            frm.remove_custom_button('Fetch Timesheet');
        }, 75);

    },

    project: function (frm) {
        frm.set_query(
            "custom_building",
            "items",
            function (frm, cdt, cdn) {
                return {
                    filters: {
                        project: frm.project,
                    },
                };
            }
        );
    },
    project: function (frm) {
        frm.set_query(
            "custom_building",
            function (doc) {
                return {
                    filters: {
                        project: frm.project,
                        has_floors: 1
                    }
                };
            }
        );
    },

    custom_building: function (frm) {
        frm.set_query(
            "custom_floor",
            function (doc) {
                return {
                    filters: {
                        project: doc.project,
                        custom_building: frm.custom_building,
                        has_units: 1
                    }
                };
            }
        );
    },
    custom_floor: function (frm) {
        frm.set_query(
            "custom_unit",
            function (doc) {
                return {
                    filters: {
                        project: doc.project,
                        custom_building: frm.building,
                        custom_floor: frm.floor,
                        linked_item: ['!=', ''],
                        status: 'Available',
                    }
                };
            }
        );
    },
})  