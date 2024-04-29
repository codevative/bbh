// Copyright (c) 2024, Codevative and contributors
// For license information, please see license.txt

frappe.ui.form.on("Rental", {
//   custom_unit: function(frm) {
//       // Reset quantity to 1 when unit is set
//       frm.set_value('quantity', 1);
// },
    onload(frm) {

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
  
    // refresh: function (frm) {
      validate: function(frm) {
        if (frm.doc.docstatus === 1 && !frm.doc.sales_invoice_created) {
            var sales_invoice = frappe.model.get_new_doc('Sales Invoice');

            // Set customer and project from Rental
            sales_invoice.customer = frm.doc.tenant;
            sales_invoice.project = frm.doc.project;

            // Set item details from Rental
            var sales_invoice_item = frappe.model.add_child(sales_invoice, 'items');
            sales_invoice_item.item_code = frm.doc.unit;
            sales_invoice_item.qty = 1;
            sales_invoice_item.rate = frm.doc.rental_amount;
            sales_invoice_item.building = frm.doc.building;
            sales_invoice_item.floor = frm.doc.floor;
            sales_invoice_item.unit = frm.doc.unit;

            frappe.set_route('Form', 'Sales Invoice', sales_invoice.name);

            frm.set_value('sales_invoice_created', true);
        }
    },
    
      refresh: function(frm) {
        _add_payment_entry(frm);
        _add_cancel_btn(frm);
        _set_items_read_only(frm);
              // if (frm.doc.docstatus === 1 && !frm.custom_button_added) {
          //     frm.add_custom_button(__('Create Sales Invoice'), function() {
          //         frappe.route_options = {
          //             'custom_rental_doc': frm.doc.name,
          //             'customer':frm.doc.tenant
          //         };
          //         frappe.new_doc('Sales Invoice');
          //     });
          //     frm.custom_button_added = true;
          // }
      
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
    //     if (!frm.is_new() && frm.doc.docstatus == 0) {
    //         frm.add_custom_button(__('Create Payment Schedule'), function () {

    //             if (frm.doc.payment_terms_template && frm.doc.payment_terms_template !== '') {
    //                 frappe.throw(__('Payment Terms already exists for this Invoice, Please remove template if you would like to change terms.'));
    //                 return; // Stop further execution
    //             }
    //             let dialog = new frappe.ui.Dialog({
    //                 title: __("Create Payment Schedule"),
    //                 fields: [
    //                     {
    //                         fieldname: 'child_table',
    //                         fieldtype: 'Table',
    //                         label: 'Payment Schedule',
    //                         fields: [
    //                             {
    //                                 fieldtype: 'Link',
    //                                 fieldname: 'mode_of_payment',
    //                                 options: 'Mode of Payment',
    //                                 label: 'Payment Type',
    //                                 in_list_view: 1
    //                             },
    //                             {
    //                                 fieldtype: 'Int',
    //                                 fieldname: 'payment_no',
    //                                 label: 'Payment Ref #',
    //                                 in_list_view: 1
    //                             },
    //                             {
    //                                 fieldtype: 'Date',
    //                                 fieldname: 'payment_date',
    //                                 label: 'Payment Date',
    //                                 in_list_view: 1
    //                             },
    //                             {
    //                                 fieldtype: 'Currency',
    //                                 fieldname: 'payment_amount',
    //                                 label: 'Payment Amount',
    //                                 in_list_view: 1
    //                             },
    //                         ],
    //                         data: [],
    //                         get_data: function () {
    //                             return this.data;
    //                         }
    //                     }
    //                 ],
    //                 primary_action_label: __('Create'),
    //                 primary_action(values) {
    //                     frappe.call({
    //                         method: 'bbh.utils.create_terms',
    //                         args: { invoice: frm.doc.name, data: values },
    //                         callback: function (r) {
    //                             if (r.message) {
    //                                 frm.set_value('payment_terms_template', r.message);

    //                                 frm.refresh_field('payment_schedule');

    //                                 dialog.hide();

    //                             }
    //                         }
    //                     });
    //                 }
    //             });
    //             dialog.show();
    //         });
    //     }
    //     setTimeout(() => {
    //         frm.remove_custom_button('Sales Order','Get Items From');
    //         frm.remove_custom_button('Delivery Note','Get Items From');
    //         frm.remove_custom_button('Quotation','Get Items From');
    //         frm.remove_custom_button('Fetch Timesheet');
    //     }, 75);

    // },

    
    //     _add_payment_entry(frm);
    //     _add_cancel_btn(frm);
        // _set_items_read_only(frm);
      },
      contract_start_date: function (frm) {
        _set_start_invoice_date(frm);
      },
});
function _add_payment_entry(frm) {
    if (frm.doc.docstatus !== 0) {
      frm.add_custom_button(__('Add Payment Entry'), async function () {
        const { message: tenant } = await frappe.db.get_value(
          'Tenant',
          frm.doc.tenant,
          'customer',
        );
        // ! hax ! (manually doing the route options of core and timing)
        frappe.__route_options = {
          mode_of_payment: 'Cash',
          party_type: 'Customer',
          party: tenant.customer,
          paid_amount: frm.doc.rental_amount,
        };
        frappe.new_doc('Payment Entry');
      });
    }
  }


function _add_cancel_btn(frm) {
    if (frm.doc.docstatus === 1) {
      // remove cancel button and add contract disable
      setTimeout(function () {
        frm.page.set_secondary_action('Contract Disable', function () {
          frappe.prompt(
            [
              {
                fieldname: 'cancellation_date',
                fieldtype: 'Date',
                label: 'Cancellation Date',
                description:
                  'Set as empty if you want to cancel the Rental Contract now.',
              },
              {
                fieldname: 'reason_for_cancellation',
                fieldtype: 'Small Text',
                label: 'Reason for Cancellation',
              },
            ],
            function (values) {
              if (values.cancellation_date) {
                frm.set_value('cancellation_date', values.cancellation_date);
                frm.set_value(
                  'reason_for_cancellation',
                  values.reason_for_cancellation,
                );
              } else {
                frm.savecancel();
              }
            },
            'Rental Cancel',
          );
        });
        frm.page.btn_secondary.addClass('btn-danger');
      }, 300);
    }
  }
  
  function _set_start_invoice_date(frm) {
    frm.set_value('start_invoice_date', frm.doc.contract_start_date);
  }
  
  function _set_items_read_only(frm) {
    frm.set_df_property('items', 'read_only', 1);
  }
  
// function create_sales_invoice(frm) {
//     frappe.call({
//         method: 'bbh.bbh_property_management.doctype.rental.rental.create_sales_invoice',
//         args: {
//             rental_id: frm.doc.name
//         },
//         callback: function(r) {
//             if (r.message) {
//                 frappe.show_alert(__('Sales Invoice created successfully'), 5);
//                 frm.reload_doc();
//             }
//         }
//     });
// }
