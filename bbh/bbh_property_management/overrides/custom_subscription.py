import frappe
from frappe import _
import erpnext
from erpnext import get_default_company
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
	get_accounting_dimensions,
)
from erpnext.accounts.doctype.subscription_plan.subscription_plan import get_plan_rate
from erpnext.accounts.party import get_party_account_currency

from erpnext.accounts.doctype.subscription.subscription import Subscription
from frappe.utils.data import (
	add_days,
	cint,
)

class CustomSubscription(Subscription):

	def create_invoice(self, prorate):
		"""
		Creates a `Invoice`, submits it and returns it
		"""
		doctype = "Sales Invoice" if self.party_type == "Customer" else "Purchase Invoice"

		invoice = frappe.new_doc(doctype)

		# For backward compatibility
		# Earlier subscription didn't had any company field
		company = self.get("company") or get_default_company()
		if not company:
			frappe.throw(
				_("Company is mandatory was generating invoice. Please set default company in Global Defaults")
			)

		invoice.company = company
		invoice.set_posting_time = 1
		invoice.posting_date = (
			self.current_invoice_start
			if self.generate_invoice_at_period_start
			else self.current_invoice_end
		)

		invoice.cost_center = self.cost_center

		if doctype == "Sales Invoice":
			invoice.customer = self.party
		else:
			invoice.supplier = self.party
			if frappe.db.get_value("Supplier", self.party, "tax_withholding_category"):
				invoice.apply_tds = 1

		### Add party currency to invoice
		invoice.currency = get_party_account_currency(self.party_type, self.party, self.company)

		## Add dimensions in invoice for subscription:
		accounting_dimensions = get_accounting_dimensions()

		for dimension in accounting_dimensions:
			if self.get(dimension):
				invoice.update({dimension: self.get(dimension)})

		# Subscription is better suited for service items. I won't update `update_stock`
		# for that reason
		project = ''
		items_list = self.get_items_from_plans(self.plans, prorate)
		for item in items_list:
			if doctype == "Sales Invoice":
				project, building, unit, floor = frappe.db.get_value("Unit", {"linked_item": item["item_code"]}, ["project", "building", "name", "floor_no"])
				item["custom_building"] = building
				item["custom_unit"] = unit
				item["custom_floor"] = floor
			item["cost_center"] = self.cost_center
			invoice.append("items", item)
		if doctype == "Sales Invoice" and project:		
			invoice.project = project
			invoice.is_rented = 1

		# Taxes
		tax_template = ""

		if doctype == "Sales Invoice" and self.sales_tax_template:
			tax_template = self.sales_tax_template
		if doctype == "Purchase Invoice" and self.purchase_tax_template:
			tax_template = self.purchase_tax_template

		if tax_template:
			invoice.taxes_and_charges = tax_template
			invoice.set_taxes()

		# Due date
		if self.days_until_due:
			invoice.append(
				"payment_schedule",
				{
					"due_date": add_days(invoice.posting_date, cint(self.days_until_due)),
					"invoice_portion": 100,
				},
			)

		# Discounts
		if self.is_trialling():
			invoice.additional_discount_percentage = 100
		else:
			if self.additional_discount_percentage:
				invoice.additional_discount_percentage = self.additional_discount_percentage

			if self.additional_discount_amount:
				invoice.discount_amount = self.additional_discount_amount

			if self.additional_discount_percentage or self.additional_discount_amount:
				discount_on = self.apply_additional_discount
				invoice.apply_discount_on = discount_on if discount_on else "Grand Total"

		# Subscription period
		invoice.from_date = self.current_invoice_start
		invoice.to_date = self.current_invoice_end

		invoice.flags.ignore_mandatory = True

		invoice.set_missing_values()
		invoice.save()

		if self.submit_invoice:
			invoice.submit()

		return invoice
