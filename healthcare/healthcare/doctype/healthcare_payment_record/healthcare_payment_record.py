import json
import frappe
from frappe.model.document import Document
from frappe.utils import flt, getdate

from healthcare.healthcare.doctype.healthcare_settings.healthcare_settings import (
	get_receivable_account,
)
from healthcare.healthcare.doctype.patient_appointment.patient_appointment import (
	get_appointment_item,
)


class HealthcarePaymentRecord(Document):
	def on_update(self):
		if self.has_value_changed("status") and self.status == "Captured":
			self.process_sales_invoice()

	def process_sales_invoice(self):
		if self.payment_for_doctype == "Patient Appointment":
			self.process_appointment_payment()
		elif self.payment_for_doctype == "Therapy Session":
			self.process_therapy_session_payment()

	def process_appointment_payment(self):
		appointment_doc = frappe.get_doc("Patient Appointment", self.payment_for_document)

		sales_invoice = frappe.new_doc("Sales Invoice")
		sales_invoice.patient = appointment_doc.patient
		sales_invoice.customer = frappe.get_value("Patient", appointment_doc.patient, "customer")
		sales_invoice.appointment = appointment_doc.name
		sales_invoice.due_date = getdate()
		sales_invoice.company = appointment_doc.company
		sales_invoice.debit_to = get_receivable_account(appointment_doc.company)
		sales_invoice.allocate_advances_automatically = 0

		item = sales_invoice.append("items", {})
		item = get_appointment_item(appointment_doc, item)
		paid_amount = flt(self.amount)

		# Add payments if payment details are supplied else proceed to create invoice as Unpaid
		sales_invoice.is_pos = 1
		mode_of_payment = frappe.get_single_value("Healthcare Settings", "mode_of_payment")
		payment = sales_invoice.append("payments", {})
		payment.mode_of_payment = mode_of_payment
		payment.amount = paid_amount
		payment.reference_no = self.payment_id
		payment.reference_date = getdate(self.creation)

		sales_invoice.set_missing_values(for_validate=True)
		sales_invoice.flags.ignore_mandatory = True
		sales_invoice.save(ignore_permissions=True)
		sales_invoice.submit()

		frappe.db.set_value(
			"Patient Appointment",
			appointment_doc.name,
			{
				"status": "Scheduled",
				"invoiced": 1,
				"ref_sales_invoice": sales_invoice.name,
				"paid_amount": paid_amount,
				"mode_of_payment": mode_of_payment,
				"billing_item": item.item_code,
			},
		)

		appointment_doc.notify_update()

	def process_therapy_session_payment(self):
		session_doc = frappe.get_doc("Therapy Session", self.payment_for_document)
		
		sales_invoice = frappe.new_doc("Sales Invoice")
		sales_invoice.patient = session_doc.patient
		sales_invoice.customer = frappe.get_value("Patient", session_doc.patient, "customer")
		# sales_invoice.therapy_session = session_doc.name # Field might not exist in SI standard
		sales_invoice.due_date = getdate()
		sales_invoice.company = session_doc.company
		sales_invoice.debit_to = get_receivable_account(session_doc.company)
		sales_invoice.allocate_advances_automatically = 0

		# Create Line Item from Therapy Type rate
		# We need to fetch the item code mapped to the therapy type or use a generic one
		# Assuming Therapy Type has a linked item or we use a default service item
		
		therapy_type = frappe.get_doc("Therapy Type", session_doc.therapy_type)
		item_code = therapy_type.item_code
		
		if not item_code:
			# Fallback or error? attempting to find item
			item_code = frappe.db.get_single_value("Healthcare Settings", "inpatient_visit_charge_item") # Fallback?
		
		if not item_code:
			frappe.throw(f"No Item linked to Therapy Type {session_doc.therapy_type} and no default item found.")

		item = sales_invoice.append("items", {})
		item.item_code = item_code
		item.qty = 1
		item.rate = flt(self.amount)
		item.amount = flt(self.amount)
		
		# Add payments
		sales_invoice.is_pos = 1
		mode_of_payment = frappe.get_single_value("Healthcare Settings", "mode_of_payment")
		payment = sales_invoice.append("payments", {})
		payment.mode_of_payment = mode_of_payment
		payment.amount = flt(self.amount)
		payment.reference_no = self.payment_id
		payment.reference_date = getdate(self.creation)

		sales_invoice.set_missing_values(for_validate=True)
		sales_invoice.flags.ignore_mandatory = True
		sales_invoice.save(ignore_permissions=True)
		sales_invoice.submit()

		frappe.db.set_value(
			"Therapy Session",
			session_doc.name,
			{
				"invoiced": 1,
				# "ref_sales_invoice": sales_invoice.name # If field exists
			},
		)

	@frappe.whitelist()
	def sync(self):
		from healthcare.healthcare.healthcare.api.patient_portal import update_payment_record
		try:
			update_payment_record(self.payment_for_doctype, self.payment_for_document)
		except Exception:
			frappe.log_error(
				title="Failed to sync Payment Record",
				message=f"Exception:\n{frappe.get_traceback(with_context=True)}\n",
				reference_doctype=self.doctype,
				reference_name=self.name,
			)
