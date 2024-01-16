# Copyright (c) 2024, Codevative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Unit(Document):
	def after_insert(self):
		item_data = {
			'doctype': 'Item',
			'item_name': self.name,
			'item_code': self.name,
			'description': f'Item for Unit {self.name}, Unit type: {self.unit_type}, Area: {self.unit_size_sq_m}',
			'item_group': 'Services',
		}

		item = frappe.get_doc(item_data)
		item.insert()

		# Update the linked_item field in the Unit document
		frappe.db.set_value('Unit', self.name, 'linked_item', item.name)