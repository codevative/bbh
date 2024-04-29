import frappe


def validate(doc, method):
    _set_missing_values(doc)


def _set_missing_values(invoice):
    if not invoice.customer_name:
        invoice.customer_name = frappe.get_value('Customer', invoice.customer, 'customer_name')

    if invoice.custom_pm_rental:
        rental_contract = frappe.get_all(
            'Rental',
            filters={'name': invoice.custom_pm_rental},
            fields=['tenant', 'project' , 'building', 'floor', 'unit']
        )[0]
        # property_group = rental_contract.get('property_group')
        # cost_center = frappe.get_value('Real Estate Property', property_group, 'cost_center')

        # invoice.pm_property_group = property_group
        invoice.custom_tenant = rental_contract.get('tenant')
        invoice.project = rental_contract.get('project')
        invoice.custom_builing = rental_contract.get('building')
        invoice.custom_floor = rental_contract.get('floor')
        invoice.custom_unit = rental_contract.get('unit')
        # invoice.pm_property = rental_contract.get('property')
        invoice.remarks = invoice.custom_pm_rental

        # for item in invoice.items:
        #     item.cost_center = cost_center
