import frappe


def get_status(status_conditions):
    for key, values in status_conditions.items():
        if all(values):
            return key


def get_debit_to():
    company = frappe.defaults.get_user_default('Company')
    return frappe.db.get_value('Company', company, 'default_receivable_account')

def get_debit_to_in():
    company = frappe.defaults.get_user_default('Company')
    return frappe.db.get_value('Company', company, 'default_income_account')


def set_invoice_created(name, invoice_ref):
    frappe.db.set_value('Rental items', name, 'is_invoice_created', 1)
    frappe.db.set_value('Rental items', name, 'invoice_ref', invoice_ref)


def set_all_property_as_vacant():
    """
    bench execute bbh.helpers.set_all_property_as_vacant
    :return:
    """
    properties = frappe.get_all('Unit')
    for unit_narration in properties:
        frappe.db.set_value('Unit', unit_narration, 'status', 'Available')
