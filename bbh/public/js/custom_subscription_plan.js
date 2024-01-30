frappe.ui.form.on('Subscription Plan', {
    refresh(frm) {

        // Make fields read-only if the document is submitted
        if (frm.doc.docstatus === 0 && !frm.is_new()) {
            frm.set_df_property('project', 'read_only', 1);
            frm.set_df_property('building', 'read_only', 1);
            frm.set_df_property('floor', 'read_only', 1);
            frm.set_df_property('custom_unit', 'read_only', 1);
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

        frm.set_query("custom_unit", function () {
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

});