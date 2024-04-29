import frappe


@frappe.whitelist()
def get_property_details(rental_contract):
    rental_contract_doc = frappe.get_all(
        'Rental',
        filters={'name': rental_contract},
        fields=['tenant', 'project']
    )
    if rental_contract_doc:
        rental_contract_doc = rental_contract_doc[0]
        customer = frappe.get_value('Tenant', rental_contract_doc.get('tenant'), 'customer')
        project = frappe.get_value('Project', rental_contract_doc.get('project'), 'project')
        building = frappe.get_value('building', rental_contract_doc.get('building'), 'building')
        floor = frappe.get_value('floor', rental_contract_doc.get('floor'), 'floor')
        unit = frappe.get_value('unit', rental_contract_doc.get('unit'), 'unit')
        return {
            **rental_contract_doc,
            'customer': customer,
            'project': project,
            'building': building,
            'floor': floor,
            'unit': unit

        }
    return None
