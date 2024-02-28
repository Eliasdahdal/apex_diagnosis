from __future__ import unicode_literals
import frappe
from frappe import _


def get_context(context):
    
    context.apex_patient = frappe.db.get_all('apex patient',fields=["latitude","longitude","first_name","last_name","name"])
    context.csrf_token = frappe.sessions.get_csrf_token()
    frappe.db.commit()
    
    return context

