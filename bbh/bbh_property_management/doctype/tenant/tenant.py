# Copyright (c) 2024, Codevative and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Tenant(Document):
	def before_insert(self):
		customer = frappe.get_doc({
			'doctype': 'Customer',
			'customer_name': self.tenant_name,
			'custom_id': self.id,
			'custom_email': self.email,
			'custom_mobile': self.mobile,
			'custom_is_tenant': 1,
		})
		customer.insert(ignore_permissions=True)
		self.customer = customer.name
		self.name = customer.name

	def on_trash(self):
		customer_name = self.db_get('customer')
		if customer_name and frappe.db.exists('Customer', customer_name):
			frappe.delete_doc('Customer', customer_name, ignore_permissions=True)
