
# -*- coding: utf-8 -*-
# Copyright (c) 2020, 9T9IT and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now


class UnitMaintenance(Document):
	def validate(self):
		if not self.created_by:
			self.created_by = frappe.session.user

	@frappe.whitelist()
	def close_issue(self):
		self.status = 'Closed'
		self.append('items', {
			'activity_datetime': now(),
			'status': 'Closed',
		})
		_send_email(self, 'Closed', 'Check Issue')
	
	@frappe.whitelist()
	def log_history(self, datetime, status, description):
		self.status = status
		self.append('items', {
			'activity_datetime': datetime,
			'status': status,
			'description': description,
		})
		_send_email(self, status, description)


def _send_email(unit_maintenance, status, description):
	if not unit_maintenance.email_notification:
		return
	if not unit_maintenance.email:
		frappe.throw(_('Email is not set'))
	try:
		frappe.sendmail(
			recipients=[unit_maintenance.email],
			subject=f'Issue {unit_maintenance.name} on {status}',
			message=description
		)
	except:
		frappe.msgprint('Unable to send email')
