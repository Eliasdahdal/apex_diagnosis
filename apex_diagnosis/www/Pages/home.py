from __future__ import unicode_literals
import frappe
from frappe import _


def get_context(context):

    context.governorates = frappe.db.get_all('syria governorates')
    context.csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    
    return context

