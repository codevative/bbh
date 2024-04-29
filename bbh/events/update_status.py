import frappe
from frappe.utils import nowdate

def execute():
    # Get all rental contracts
   
    rental_contracts = frappe.get_all("Rental",
        filters={"docstatus": 1},
        fields=["name", "contract_start_date", "contract_end_date", "unit"])
    for contract in rental_contracts:
            units = frappe.get_doc("Unit", fields=["name","status"])
        # Check if start date is greater than end date
            if contract.contract_start_date > contract.end_date:
                for unit in units:
                    frappe.db.set_value("Unit", contract.unit, "status", "Rented")
                frappe.db.set_value("Unit", unit.unit, "status", "Rented")
            if contract.contract_end_date < nowdate():
                for unit in units:
                    frappe.db.set_value("Unit", unit.unit, "status", "Available")
             

# Schedule the script to run daily
# @frappe.whitelist()
# def daily_update_unit_status():
#     update_unit_status()

# # Run the script initially
# update_unit_status()