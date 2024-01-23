import frappe
import json

@frappe.whitelist()
def create_units_for_floor(floor, data):
    floor_doc = frappe.get_doc('Floor', floor)
    data = json.loads(data)
    units = data.get("num_units")
    previous_high = 0
    if frappe.db.exists("Unit", {"floor_no": floor_doc.name}):
        previous_high = frappe.db.get_value("Unit", {"floor_no": floor_doc.name}, "unit_no", order_by="unit_no DESC")

    for i in range(int(previous_high), int(previous_high)+int(units)):
        unit = frappe.get_doc({
            "doctype": "Unit",
            "project": floor_doc.project,
            "building": floor_doc.building,
            "floor_no": floor_doc.name,
            "unit_type": data.get("unit_type"),
            "unit_size_sq_m": data.get("unit_size_sq_m"),
            "unit_no": i+1,
            "price": data.get("price"),
            "unit_narration": str(floor_doc.name) + str(i+1)
        })
        unit.insert()
    floor_doc.has_units = 1
    floor_doc.save()

@frappe.whitelist()
def create_floors_for_buildings(building, data):
    building_doc = frappe.get_doc('Building', building)
    data = json.loads(data)
    units = data.get("no_of_floors")
    previous_high = 0
    if frappe.db.exists("Floor", {"building": building_doc.name}):
        previous_high = frappe.db.get_value("Floor", {"building": building_doc.name}, "floor_number", order_by="floor_number DESC")

    for i in range(int(previous_high), int(previous_high)+int(units)):

        floor = frappe.get_doc({
            "doctype": "Floor",
            "building": building_doc.name,
            "project": building_doc.project,
            "floor_number": int(i+1),
            "floor_name": "Floor "+str(i+1),
            "total_area": building_doc.covered_area
        })
        floor.insert()
    building_doc.has_floors = 1
    building_doc.save()

@frappe.whitelist()
def update_unit(doc,event):
    if event == "on_cancel":
        status = "Available"
    elif event == "on_submit":
        status = "Sold"
        if doc.custom_down_payment and doc.custom_down_payment > 0:
            make_payment_entry(doc)
    for row in doc.items:
        if row.custom_unit:
            frappe.db.set_value('Unit', row.custom_unit, 'status', status)

def make_payment_entry(doc):
    company = doc.company
    default_bank_account = frappe.db.get_value("Company",company,'default_cash_account')

    default_currency = frappe.db.get_value("Company",company,'default_currency')
    paid_amount = doc.custom_down_payment

    reference = frappe.get_doc({
        "doctype" : "Payment Entry Reference",
        "reference_doctype" : "Sales Invoice",
        "reference_name" : doc.name,
        "allocated_amount" : paid_amount,
        "parentfield":"references",
        "exchange_gain_loss" : 0,
        "parenttype" :"Payment Entry"}
        )
    references = [reference]
    payment_entry = frappe.get_doc({
        "doctype":"Payment Entry",
        "party_type":"Customer",
        "party" : doc.customer,
        "party_name": doc.customer_name,
        "account_currency": default_currency,
        "posting_date" : frappe.utils.getdate(),
        "company" : company,
        "paid_amount" : paid_amount,
        "paid_from": doc.debit_to,
        "paid_to" : default_bank_account,
        "received_amount" : paid_amount,
        "references" : references,
        "reference_no" :doc.name,
        "reference_date" : frappe.utils.getdate(),
        "unallocated_amount": 0,
        "target_exchange_rate" :1,
        "source_exchange_rate" : 1,
        "paid_to_account_currency" :default_currency
    })

    payment_entry.submit()

    frappe.db.commit()

from frappe.utils import date_diff
from frappe.utils.data import cint
@frappe.whitelist()
def create_terms(invoice,data):
    invoice_doc = frappe.get_doc('Sales Invoice',invoice)
    data = json.loads(data)
    total_invoice_amount = invoice_doc.grand_total

    payment_terms_template_name = f"Payment Terms for Invoice #{invoice_doc.name}"
    payment_terms = []

    try:
        for d in data:
            try:
                credit_days = date_diff(d.payment_date, invoice_doc.posting_date)
                invoice_portion = (d.payment_amount / total_invoice_amount) * 100 if total_invoice_amount else 0

                payment_term_name = str(number_to_ordinal(cint(d.idx))) + f' Installment for Invoice #{invoice_doc.name} for customer {invoice_doc.customer}'
                payment_term = frappe.get_doc({
                    'doctype': 'Payment Term',
                    'payment_term_name': payment_term_name,
                    'mode_of_payment': d.mode_of_payment,
                    'custom_payment_reference_':d.payment_no,
                    'invoice_portion': invoice_portion,
                    'description': f"Payment No {d.idx}",
                    'credit_days': credit_days if credit_days > 0 else 0,
                    'due_date_based_on': 'Day(s) after invoice date',
                })
                payment_term.insert()
                payment_terms.append(payment_term.name)
                frappe.log_error(title="Payment Term Inserted", message=f"Payment term {payment_term_name} created successfully.")
            except Exception as e:
                frappe.log_error(title="Payment Term Creation Failed", message=f"Failed to create payment term for row {d.idx} in Invoice {invoice_doc.name}: {e}")
                raise
        try:
            payment_terms_template = frappe.get_doc({
                'doctype': 'Payment Terms Template',
                'template_name': payment_terms_template_name,
                'allocate_payment_based_on_payment_terms':1,
                'terms': [{'payment_term': term} for term in payment_terms]
            })
            payment_terms_template.insert()
        except Exception as e:
            frappe.log_error(title="Payment Terms Template Creation Failed", message=f"Failed to create payment terms template for Invoice {invoice_doc.name}: {e}")
            raise
        try:
            return payment_terms_template.name
        except Exception as e:
            frappe.log_error(title="Sales Invoice Update Failed", message=f"Failed to link payment terms template to Invoice {invoice_doc.name}: {e}")
            raise

    except Exception as e:
        frappe.throw(f"An error occurred while creating payment terms: {e}")

def number_to_ordinal(n):
    suffixes = {1: 'st', 2: 'nd', 3: 'rd'}
    # Check for 11-13 because those are the numbers that don't follow the usual rule
    if 10 <= n % 100 <= 13:
        suffix = 'th'
    else:
        # The last digit of the number determines the appropriate suffix
        suffix = suffixes.get(n % 10, 'th')
    return f'{n}{suffix}'