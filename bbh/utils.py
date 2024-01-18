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
    for row in doc.items:
        if row.custom_unit:
            frappe.db.set_value('Unit', row.custom_unit, 'status', status)