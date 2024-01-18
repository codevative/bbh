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
                        project: frm.project
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