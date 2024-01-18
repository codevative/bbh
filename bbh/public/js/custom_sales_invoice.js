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