import frappe
from frappe.utils.data import today


def execute():
    rental_contracts = frappe.db.sql(
        """
            SELECT name
            FROM `tabRental`
            WHERE docstatus = 1
            AND cancellation_date < %s
        """,
        today(),
        as_dict=1
    )
    for rental in rental_contracts:
        rental_contract_doc = frappe.get_doc('Rental', rental['name'])
        rental_contract_doc.cancel()