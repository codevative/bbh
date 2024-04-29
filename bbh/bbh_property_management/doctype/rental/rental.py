# Copyright (c) 2024, Codevative and contributors
# For license information, please see license.txt


from __future__ import unicode_literals
import frappe
from frappe import _, enqueue
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils.data import add_to_date, getdate, nowdate, now_datetime, get_first_day
from bbh.helpers import get_status, get_debit_to, set_invoice_created
from frappe.model.mapper import get_mapped_doc
from datetime import datetime, timedelta


class Rental(Document):

    # def create_sales_invoice_for_last_day_rentals(self):
    #     # Get the last day of the previous month
    #     today = datetime.now().date()
    #     last_day_of_previous_month = today.replace(day=1) - timedelta(days=1)

    #     # Get rental documents submitted on the last day of the previous month
    #     rentals = frappe.get_list("Rental", filters={
    #         "docstatus": 1,  # Submitted
    #         "modified": last_day_of_previous_month,
    #     })
    #     frappe.msgprint(rentals)
    #     for rental in rentals:
    #         frappe.msgprint(rental)
    #         self._create_sales_invoice_new(rental)

    # def _create_sales_invoice_new(self, rental):
    #     # Create Sales Invoice
    #     sales_invoice = frappe.new_doc("Sales Invoice")
    #     sales_invoice.custom_rental_doc = rental.name
    #     sales_invoice.customer = rental.tenant
    #     sales_invoice.project = rental.project

    #     # Add item details from rental
    #     sales_invoice.append("items", {
    #         "item_code": rental.unit,
    #         "qty": 1,
    #         "rate": rental.amount,
    #         "building": rental.building,
    #         "floor": rental.floor,
    #         "unit": rental.unit
    #         # Add other item details as needed
    #     })

    #     # Save and submit the sales invoice
    #     sales_invoice.insert()
    #     sales_invoice.submit()

    # # Schedule the function to run daily
    # @staticmethod
    # def schedule_sales_invoice_creation():
    #     frappe.get_doc({
    #         "doctype": "Scheduled Job Log",
    #         "event": "daily",
    #         "scheduled_job_type": "bbh.bbh_property_management.doctype.rental.rental.create_sales_invoice_for_last_day_rentals"
    #     }).insert()

    # # Schedule the function to run
    # schedule_sales_invoice_creation()

 

    def on_submit(self):
        if not self.sales_invoice_created:
            self.create_sales_invoice_on_submit(self.name)
            self.db_set('sales_invoice_created', 1, update_modified=False)

    def create_sales_invoice_on_submit(rental_docname):
        rental = frappe.get_doc("Rental", rental_docname)

        # Create Sales Invoice
        sales_invoice = get_mapped_doc("Rental", rental_docname, {
            "Rental": {
                "doctype": "Sales Invoice",
                "field_map": {
                    "tenant": "customer",
                    "project": "project",
                    "posting_date": "due_date"
                    # Add field mappings for other fields as needed
                }
            }
        })

        building = rental.building
        floor = rental.floor
        unit = rental.unit
        rate = rental.rental_amount
        frappe.msgprint("okay...1")


        # Append Sales Invoice item directly with building, floor, and unit values
        sales_invoice.append("items", {
            "item_code": unit,
            "qty": 1,
            "rate": rate,
            "building": building,
            "floor": floor,
            "unit": unit
            # Add other item details as needed
        })

        # Save Sales Invoice
        sales_invoice.insert(ignore_permissions=True)
        frappe.msgprint("okay...")

        # Optionally, you can submit the Sales Invoice immediately
        # sales_invoice.submit()

        frappe.msgprint("Sales Invoice created successfully against Rental {0}".format(rental_docname))
                



    def autoname(self):
        # abbr = frappe.db.get_value("Real Estate Property", self.property_group, "abbr")
        # if not abbr:
        #     frappe.throw(_(f"Please set the abbreviation of the Real Estate Property {self.property_group}"))

        # unit = frappe.db.get_value("Unit", self.unit, "unit_narration")
        # if not unit_narration:
        #     frappe.throw(_(f"Please set the property no of the Property {self.project}"))

        self.name = make_autoname("-".join(["BBH",self.title, ".###"]), "", self)

    def validate(self):
        _validate_contract_dates(self)
        _validate_property(self)
        _set_status(self)
        if not self.items:
            self.update({"items": _generate_items(self)})
        

    def on_submit(self):
        _set_property_as_rented(self)
        if self.apply_invoices_now:
            _generate_invoices_now(self)

    def on_update_after_submit(self):
        _update_items(self)

    def before_cancel(self):
        _delink_sales_invoices(self)
        _set_property_as_vacant(self)


def _set_status(renting):
    status = None

    if renting.docstatus == 0:
        status = "Draft"
    elif renting.docstatus == 2:
        status = "Cancelled"
    elif renting.docstatus == 1:
        status = get_status(
            {
                "Active": [renting.contract_end_date > nowdate()],
                "Expired": [renting.contract_end_date < nowdate()],
            }
        )

    renting.db_set("status", status, update_modified=True)


def _validate_contract_dates(renting):
    if renting.contract_start_date > renting.contract_end_date:
        frappe.throw(_("Please set contract end date after the contract start date"))


def _validate_property(renting):
    rental_status = frappe.db.get_value("Unit", renting.unit, "status")
    if rental_status == "Rented":
        frappe.throw(_("Please make choose unoccupied Unit."))


def _generate_items(renting):
    """
    Create items for succeeding dates
    :param renting:
    :return:
    """

    def make_item(invoice_date):
        return {
            "invoice_date": getdate(invoice_date),
            "description": "Rent Due",
            "is_invoice_created": 0,
        }

    items = []

    if _get_invoice_on_start_date():
        items.append(make_item(renting.start_invoice_date))

    end_date = getdate(renting.contract_end_date)
    next_date = _get_next_date(
        getdate(renting.start_invoice_date), renting.rental_frequency
    )
    while next_date < end_date:
        items.append(make_item(next_date))
        next_date = _get_next_date(next_date, renting.rental_frequency)

    return items


def _set_property_as_rented(renting):
    frappe.db.set_value("Unit", renting.unit, "status", "Rented")


def _generate_invoices_now(renting):
    def make_data(item_data):
        return {
            "customer": customer,
            "due_date": item_data.invoice_date,
            "posting_date": get_first_day(item_data.invoice_date),
            "debit_to": debit_to,
            "set_posting_time": 1,
            "posting_time": 0,
            "custom_pm_rental": renting.name,
            "items": [
                {"item_code": rental_item,"custom_building": renting.building, "custom_floor": renting.floor, "custom_unit": renting.unit, "rate": renting.rental_amount, "qty": 1}
            ],
        }

    items = list(
        filter(
            lambda x: getdate(x.invoice_date) < getdate(now_datetime()), renting.items
        )
    )
    customer = frappe.db.get_value("Tenant", renting.tenant, "customer")
    rental_item = frappe.db.get_single_value(
        "BBH Property Management Settings", "rental_item"
    )
    submit_si = frappe.db.get_single_value("BBH Property Management Settings", "submit_si")
    debit_to = get_debit_to()

    for item in items:
        invoice_data = make_data(item)
        items = invoice_data.pop("items")

        invoice = frappe.new_doc("Sales Invoice")
        invoice.update(invoice_data)
        invoice.append("items", items[0])
        invoice.set_missing_values()
        invoice.save()

        if submit_si:
            invoice.submit()

        set_invoice_created(item.name, invoice.name)


def _update_items(renting):
    existing_items = list(map(lambda x: x.invoice_date, renting.items))
    items = list(
        filter(
            lambda x: x.get("invoice_date").strftime("%Y-%m-%d") not in existing_items,
            _generate_items(renting),
        )
    )
    last_idx = len(existing_items)
    for count, item in enumerate(items):
        last_idx = last_idx + 1
        frappe.get_doc(
            {
                **item,
                "idx": last_idx,
                "doctype": "Rental items",
                "parent": renting.name,
                "parentfield": "items",
                "parenttype": "Rental",
            }
        ).save()


def _delink_sales_invoices(renting):
    sales_invoices = frappe.get_all(
        "Sales Invoice", filters={"custom_pm_rental": renting.name}
    )
    for sales_invoice in sales_invoices:
        frappe.db.set_value("Sales Invoice", sales_invoice, "custom_pm_rental", "")


def _set_property_as_vacant(renting):
    retain_rental_on_cancel = frappe.db.get_single_value(
        "BBH Property Management Settings", "retain_rental_on_cancel"
    )
    if not retain_rental_on_cancel:
        frappe.db.set_value("Unit", renting.unit, "status", "Available")


def _get_next_date(date, frequency):
    next_date = date
    if frequency == "Monthly":
        next_date = add_to_date(next_date, months=1)
    elif frequency == "Quarterly":
        next_date = add_to_date(next_date, months=4)
    elif frequency == "Half-yearly":
        next_date = add_to_date(next_date, months=6)
    elif frequency == "Yearly":
        next_date = add_to_date(next_date, years=1)
    return next_date


def _get_invoice_on_start_date():
    return frappe.db.get_single_value(
        "BBH Property Management Settings", "invoice_on_start_date"
    )
        
# def create_sales_invoice(rental_id):
#         try:
#             # Fetch Rent document
#             rent_doc = frappe.get_doc("Rental", rental_id)

#             # Create Sales Invoice
#             sales_invoice = frappe.new_doc("Sales Invoice")
            
#             # Set customer and company
#             sales_invoice.customer = rent_doc.customer
#             sales_invoice.company = rent_doc.company

#             # Set items from Rent document
#             for item in rent_doc.items:
#                 sales_invoice.append("items", {
#                     "item_code": rent_doc.unit,
#                     "qty": item.qty,
#                     "rate": rent_doc.rental_amount,
#                     "income_account": item.income_account,
#                     "cost_center": item.cost_center
#                 })

#             # Set taxes and charges
#             # sales_invoice.taxes_and_charges = rent_doc.taxes_and_charges

#             # Save Sales Invoice as draft
#             sales_invoice.save()

#             # Submit Sales Invoice
#             sales_invoice.submit()
#             frappe.msgprint("succssesful Testing")
#             frappe.msgprint("Sales Invoice created successfully against Rent {0}".format(rent_doc.name))
#         except Exception as e:
#             frappe.msgprint("Faild Testing")
#             frappe.log_error(frappe.get_traceback(), "Failed to create Sales Invoice against Rent {0}".format(rent_doc.name))

# # Hook to create Sales Invoice on Rent submission
# @frappe.whitelist()        
# def create_sales_invoice_on_rent_submission(doc, method):
#     if doc.doctype == "Rental" and doc.docstatus == 1:  # Check if Rent document is submitted
#         create_sales_invoice(doc.name)  



# import frappe

# @frappe.whitelist()
# def create_sales_invoice(rental_id):
    # try:
    #     # Fetch Rental document
    #     rental = frappe.get_doc('Rental', rental_id)

    #     # Create Sales Invoice
    #     sales_invoice = frappe.new_doc('Sales Invoice')
    #     sales_invoice.customer = rental.tenant
    #     sales_invoice.project = rental.project
    #     frappe.msgprint(sales_invoice.customer)
    #     # sales_invoice.rental_doc = rental_id  # Set the reference to the Rental document
    #     # Add other fields from Rental document as needed

    #     # Add items from Rental document to Sales Invoice
    #     # for item in rental.items:
     
    #     sales_invoice.append('items', {
    #             'item_code': rental.unit,  # Set the unit as item code
    #             'tem_name': rental.unit,  # Set the unit as item code
    #             'qty': 1,  # Set default quantity to 1
    #             'rate': rental.rental_amount,  # Set the rate from Rental item
    #             'building': rental.building,
    #             'floor': rental.floor,
    #             'unit': rental.unit,
    #             # Add other fields from Rental item as needed
    #         })

    #     # Save Sales Invoice
    #     sales_invoice.insert()
    #     # sales_invoice.save()
    #     frappe.msgprint("test ok..")
    #     return sales_invoice.name
        
    # except Exception as e:
    #     frappe.msgprint("test faild..")
    #     frappe.log_error(frappe.get_traceback(), 'Failed to create Sales Invoice against Rental {0}'.format(rental_id))


    

