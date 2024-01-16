import frappe
import json

@frappe.whitelist()
def create_units_for_floor(floor, data):
    floor_doc = frappe.get_doc('Floor', floor)
    data = json.loads(data)
    units = data.get("num_units")
    for i in range(units):
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
