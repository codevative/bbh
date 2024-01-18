# Copyright (c) 2024, Codevative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Building(Document):
    pass
	# def after_insert(self):
	# 	if self.has_floors and not self.no_of_floors:
	# 		frappe.throw("No. of Floors is mandatory when Has Floors is checked")
	# 	if not self.has_floors and self.no_of_floors:
	# 		self.no_of_floors = 0
	# 	if self.has_floors and self.no_of_floors:
	# 		for i in range(self.no_of_floors):
	# 			floor = frappe.get_doc({
	# 				"doctype": "Floor",
	# 				"building": self.name,
	# 				"project": self.project,
	# 				"floor_number": int(i+1),
	# 				"floor_name": "Floor "+str(i+1),
	# 				"total_area": self.covered_area
	# 			})
	# 			floor.insert()

