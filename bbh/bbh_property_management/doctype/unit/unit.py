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
		self.create_or_update_item_price()

	def on_update(self):
		# Check if the price has changed and update the item price
		if self.has_value_changed('price'):
			self.create_or_update_item_price()


	def create_or_update_item_price(self):
			existing_price = frappe.db.get_value('Item Price', {'item_code': self.name}, 'name')

			item_price_data = {
				'doctype': 'Item Price',
				'price_list': 'Standard Selling',
				'item_code': self.name,
				'price_list_rate': self.price
			}

			if existing_price:
				item_price = frappe.get_doc('Item Price', existing_price)
				item_price.update(item_price_data)
				item_price.save()
			else:
				item_price = frappe.get_doc(item_price_data)
				item_price.insert()