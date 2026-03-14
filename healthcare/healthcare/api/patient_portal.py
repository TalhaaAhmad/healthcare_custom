import json
from datetime import datetime

import frappe
from frappe import _
from frappe.query_builder import Order
from frappe.utils import get_datetime, get_time, getdate

import erpnext

from healthcare.healthcare.doctype.observation.observation import get_observation_reference
from healthcare.healthcare.utils import get_appointment_billing_item_and_rate


@frappe.whitelist()
def get_appointments():
	patients = get_patients_with_relations()

	if not len(patients):
		return

	appointment = frappe.qb.DocType("Patient Appointment")
	encounter = frappe.qb.DocType("Patient Encounter")
	practitioner = frappe.qb.DocType("Healthcare Practitioner")
	patient = frappe.qb.DocType("Patient")
	company = frappe.qb.DocType("Company")

	query = (
		frappe.qb.from_(appointment)
		.left_join(encounter)
		.on((appointment.name == encounter.appointment) & (encounter.docstatus == 1))
		.left_join(practitioner)
		.on(appointment.practitioner == practitioner.name)
		.left_join(patient)
		.on(appointment.patient == patient.name)
		.left_join(company)
		.on(appointment.company == company.name)
		.select(appointment.star)
		.select(encounter.name.as_("encounter"))
		.select(practitioner.image.as_("practitioner_image"))
		.select(patient.image.as_("patient_image"))
		.select(company.default_currency.as_("default_currency"))
		.where(appointment.patient.isin(get_patients_with_relations()))
		.where(appointment.status != "Cancelled")
		.where(appointment.appointment_for == "Practitioner")
		.orderby(appointment.appointment_date, order=Order.desc)
	)

	appointment_details = query.run(as_dict=True)

	# Enrich with consultation fee for unpaid appointments
	appointment_type = frappe.db.get_value("Appointment Type", {}, "name")
	for appt in appointment_details:
		if not appt.get("paid_amount"):
			try:
				doc = frappe._dict({
					"department": appt.get("department"),
					"service_unit": appt.get("service_unit", ""),
					"doctype": "Patient Appointment",
					"inpatient_record": "",
					"practitioner": appt.get("practitioner"),
					"appointment_type": appointment_type,
				})
				details = get_appointment_billing_item_and_rate(doc)
				appt["consultation_charge"] = details.get("practitioner_charge") or 0
			except Exception:
				appt["consultation_charge"] = 0
		else:
			appt["consultation_charge"] = appt.get("paid_amount") or 0

	return appointment_details


@frappe.whitelist()
def get_appointment_by_id(appointment_id):
	"""Get a single appointment by ID for the payment/booking status page."""
	patients = get_patients_with_relations()
	if not len(patients):
		return None

	appointment = frappe.qb.DocType("Patient Appointment")
	encounter = frappe.qb.DocType("Patient Encounter")
	practitioner = frappe.qb.DocType("Healthcare Practitioner")
	patient = frappe.qb.DocType("Patient")
	company = frappe.qb.DocType("Company")

	query = (
		frappe.qb.from_(appointment)
		.left_join(encounter)
		.on((appointment.name == encounter.appointment) & (encounter.docstatus == 1))
		.left_join(practitioner)
		.on(appointment.practitioner == practitioner.name)
		.left_join(patient)
		.on(appointment.patient == patient.name)
		.left_join(company)
		.on(appointment.company == company.name)
		.select(appointment.star)
		.select(encounter.name.as_("encounter"))
		.select(practitioner.image.as_("practitioner_image"))
		.select(patient.image.as_("patient_image"))
		.select(company.default_currency.as_("default_currency"))
		.where(appointment.name == appointment_id)
		.where(appointment.patient.isin(patients))
	)

	result = query.run(as_dict=True)
	if not result:
		return None
		
	appt = result[0]
	
	# Enrich with consultation fee
	if not appt.get("paid_amount"):
		try:
			appointment_type = frappe.db.get_value("Appointment Type", {}, "name")
			doc = frappe._dict({
				"department": appt.get("department"),
				"service_unit": appt.get("service_unit", ""),
				"doctype": "Patient Appointment",
				"inpatient_record": "",
				"practitioner": appt.get("practitioner"),
				"appointment_type": appointment_type,
			})
			details = get_appointment_billing_item_and_rate(doc)
			appt["consultation_charge"] = details.get("practitioner_charge") or 0
		except Exception:
			appt["consultation_charge"] = 0
	else:
		appt["consultation_charge"] = appt.get("paid_amount") or 0

	# Enrich with payment record status (Captured / Failed / Pending)
	payment_records = frappe.get_all(
		"Healthcare Payment Record",
		filters={
			"payment_for_doctype": "Patient Appointment",
			"payment_for_document": appointment_id,
		},
		fields=["name", "status", "failure_reason", "payment_id", "amount", "amount_with_gst", "currency", "creation"],
		order_by="creation desc",
		limit=1,
		ignore_permissions=True,
	)
	if payment_records:
		pr = payment_records[0]
		appt["payment_status"] = pr.status  # Pending / Captured / Failed
		appt["payment_failure_reason"] = pr.failure_reason or ""
		appt["payment_id"] = pr.payment_id or ""
		appt["payment_record_amount"] = float(pr.amount_with_gst or pr.amount or 0)
		appt["payment_record_currency"] = pr.currency or appt.get("default_currency", "")
		appt["payment_record_name"] = pr.name
	else:
		appt["payment_status"] = ""
		appt["payment_failure_reason"] = ""
		appt["payment_id"] = ""

	return appt


@frappe.whitelist()
def get_encounter_details(encounter_id):
	"""Get encounter details including symptoms, diagnosis, and prescriptions."""
	patients = get_patients_with_relations()
	if not len(patients):
		return None

	encounter = frappe.get_doc("Patient Encounter", encounter_id)
	
	# Verify patient access
	if encounter.patient not in patients:
		frappe.throw(_("Not permitted"), frappe.PermissionError)

	details = {
		"symptoms": encounter.get("symptoms"),
		"diagnosis": encounter.get("diagnosis"),
		"drug_prescription": encounter.get("drug_prescription"),
		"lab_test_prescription": encounter.get("lab_test_prescription")
	}

	return details


@frappe.whitelist()
def get_logged_in_patient():
	patient = frappe.db.exists("Patient", {"status": "Active", "user_id": frappe.session.user})

	if not patient:
		return None

	return {"value": patient, "label": frappe.get_cached_value("Patient", patient, "patient_name")}


@frappe.whitelist()
def get_departments():
	return frappe.db.get_all(
		"Medical Department",
		fields=["name", "department"],
		order_by="name ASC",
	)


@frappe.whitelist()
def get_practitioners(department=None):
	filters = {}
	if department:
		filters["department"] = department

	return frappe.db.get_all(
		"Healthcare Practitioner",
		filters=filters,
		fields=["name", "practitioner_name", "designation", "department", "image"],
	)


@frappe.whitelist()
def get_patients():
	patient_names = get_patients_with_relations()
	patients = frappe.db.get_all(
		"Patient",
		filters={"name": ["in", patient_names]},
		fields=["name as value", "patient_name as label"],
	)

	patients.append({"value": "new", "label": _("Someone Else")})
	return patients


@frappe.whitelist()
def get_settings():
	return frappe.get_single("Healthcare Settings")


@frappe.whitelist()
def get_slots(practitioner, date):
	date = getdate() if date in ["undefined", "", "null"] else getdate(date)
	practitioner = None if practitioner in ["undefined", "", "null"] else practitioner

	if not practitioner:
		return

	current_date = getdate()
	if date < current_date:
		return {"status": "error", "message": "Cannot fetch slots for past dates."}

	practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)
	curr_bookings = frappe.db.get_all(
		"Patient Appointment",
		filters={
			"practitioner": practitioner_doc.name,
			"appointment_date": date,
			"status": ["not in", ["Cancelled"]],
		},
		pluck="appointment_time",
	)
	therapy_bookings = frappe.db.get_all(
		"Therapy Session",
		filters={"practitioner": practitioner_doc.name, "start_date": date, "docstatus": ["!=", 2]},
		pluck="start_time"
	)
	
	booked_slots = [(datetime.min + booked_slot).time() for booked_slot in curr_bookings + therapy_bookings]

	available_slots = full_slots = []
	weekday = date.strftime("%A")

	for schedule_entry in practitioner_doc.practitioner_schedules:
		practitioner_schedule = frappe.get_doc("Practitioner Schedule", schedule_entry.schedule)

		if practitioner_schedule and not practitioner_schedule.disabled:
			available_slots = []
			for time_slot in practitioner_schedule.time_slots:
				if weekday == time_slot.day:
					time = datetime.min + time_slot.from_time
					current_time = get_time(get_datetime())
					time = time.time()
					if date == current_date:
						if time not in booked_slots and time > current_time:
							available_slots.append(time.strftime("%H:%M"))
					else:
						if time not in booked_slots:
							available_slots.append(time.strftime("%H:%M"))
		full_slots.extend(available_slots)

	if len(full_slots) > 0:
		full_slots = list(sorted(full_slots))

	return full_slots if len(full_slots) > 0 else None

@frappe.whitelist(methods=["POST"])
def make_appointment(practitioner, patient, date, slot, relative_details=None, appointment_id=None):
	if patient == "new":
		if not relative_details:
			frappe.throw(_("Relative details are required when booking for someone else."))
		
		if isinstance(relative_details, str):
			relative_details = json.loads(relative_details)

		# Get current user's patient and customer
		user_patient_name = frappe.db.get_value("Patient", {"user_id": frappe.session.user}, "name")
		if not user_patient_name:
			frappe.throw(_("Primary patient record not found for the current user."))

		user_patient = frappe.get_doc("Patient", user_patient_name)
		customer = user_patient.customer

		# Create new patient record for the relative
		new_patient = frappe.new_doc("Patient")
		new_patient.first_name = relative_details.get("first_name")
		new_patient.last_name = relative_details.get("last_name")
		new_patient.sex = relative_details.get("sex")
		new_patient.dob = relative_details.get("dob")
		new_patient.mobile = relative_details.get("mobile_number")
		new_patient.email = relative_details.get("email")
		new_patient.customer = customer
		new_patient.status = "Active"
		new_patient.insert(ignore_permissions=True)

		# Add to current user's patient relations
		user_patient.append("patient_relation", {
			"patient": new_patient.name,
			"relation": relative_details.get("relation") or "Other"
		})
		user_patient.save(ignore_permissions=True)

		patient = new_patient.name

	if appointment_id:
		# Update existing appointment (Reschedule)
		doc = frappe.get_doc("Patient Appointment", appointment_id)
		# Verify ownership/permissions if needed, though get_doc handles basic perm checks
		if doc.status not in ["Open", "Scheduled", "Confirmed"]:
			frappe.throw(_("Cannot reschedule an appointment that is not Open, Scheduled or Confirmed"))
	else:
		# Create new appointment
		doc = frappe.new_doc("Patient Appointment")
	
	# Get first available appointment type (v15 compatible)
	appointment_type = frappe.db.get_value("Appointment Type", {}, "name")
	if appointment_type:
		doc.appointment_type = appointment_type
	
	# Default to Practitioner for v15
	doc.appointment_for = "Practitioner"
	
	company = frappe.defaults.get_user_default("company")
	if not company:
		company = frappe.db.get_single_value("Global Defaults", "default_company")
	doc.company = company

	doc.patient = patient
	practitioner_doc = frappe.get_doc("Healthcare Practitioner", practitioner)
	doc.practitioner = practitioner_doc.name
	doc.practitioner_name = practitioner_doc.practitioner_name
	doc.department = practitioner_doc.department
	doc.appointment_date = getdate(date)
	doc.appointment_time = slot

	weekday = getdate(date).strftime("%A")
	service_unit = None

	for schedule_entry in practitioner_doc.practitioner_schedules:
		practitioner_schedule = frappe.get_doc("Practitioner Schedule", schedule_entry.schedule)
		if hasattr(schedule_entry, 'service_unit') and schedule_entry.service_unit:
			service_unit = frappe.db.get_value(
				"Healthcare Service Unit", schedule_entry.service_unit, "name"
			)

		if practitioner_schedule and not practitioner_schedule.disabled:
			available_slots = []
			for time_slot in practitioner_schedule.time_slots:
				if weekday == time_slot.day:
					time = datetime.min + time_slot.from_time
					time = time.time()
					available_slots.append(time.strftime("%H:%M"))

		if slot in available_slots:
			break

	if service_unit:
		doc.service_unit = service_unit

	# Set status to Open (Unpaid) initially
	doc.status = "Open"
	
	doc.save(ignore_permissions=True)
	return doc


@frappe.whitelist()
def get_fees(practitioner=None, date=None):
	if not (practitioner or date):
		return

	default_currency = erpnext.get_default_currency()
	default_company = frappe.db.get_single_value("Global Defaults", "default_company")

	# Get first available appointment type (v15 compatible)
	appointment_type = frappe.db.get_value("Appointment Type", {}, "name")

	doc = frappe._dict(
		{
			"department": frappe.get_cached_value("Healthcare Practitioner", practitioner, "department"),
			"service_unit": "",
			"doctype": "Patient Appointment",
			"inpatient_record": "",
			"practitioner": practitioner,
			"appointment_type": appointment_type,
		}
	)

	try:
		details = get_appointment_billing_item_and_rate(doc)
	except Exception:
		details = {}

	return {
		"details": details,
		"default_currency": default_currency,
		"default_company": default_company,
	}


@frappe.whitelist()
def get_print_format(doctype: str, name: str):
	allowed_doctypes = ["Sales Invoice", "Patient Encounter", "Diagnostic Report"]
	if doctype not in allowed_doctypes:
		frappe.throw(_("Not allowed to print this document."), frappe.PermissionError)

	meta = frappe.get_meta(doctype)

	print_format = (
		"Diagnostic Report"
		if doctype == "Diagnostic Report"
		else meta.default_print_format or "Standard"
	)

	letter_head = None
	if meta.has_field("letter_head"):
		letter_head = frappe.db.get_value(doctype, name, "letter_head")

	if not letter_head:
		letter_head = frappe.db.exists("Letter Head", {"is_default": 1})

	return {"letter_head": letter_head, "print_format": print_format}


def get_patients_with_relations():
	# Always filter by user_id unless explicit bypass is added later
	# This ensures even admins see only "their" linked patients in the portal context
	filters = {"status": "Active", "user_id": frappe.session.user}
	
	patients = frappe.db.get_all("Patient", filters=filters, pluck="name")
	relation = frappe.db.get_all(
		"Patient Relation", filters={"parent": ["in", patients]}, pluck="patient"
	)

	return patients + relation


@frappe.whitelist()
def get_medical_history(patient=None):
	"""Fetch Patient Medical Records for the portal."""
	allowed_patients = get_patients_with_relations()
	if not allowed_patients:
		return []

	filters = {"patient": ["in", allowed_patients]}
	# If a specific patient is requested, ensure it's in the allowed list
	if patient:
		if patient not in allowed_patients:
			frappe.throw(_("Not permitted to view records for this patient"), frappe.PermissionError)
		filters["patient"] = patient

	pmr = frappe.qb.DocType("Patient Medical Record")
	pat = frappe.qb.DocType("Patient")

	query = (
		frappe.qb.from_(pmr)
		.left_join(pat)
		.on(pmr.patient == pat.name)
		.select(
			pmr.name,
			pmr.patient,
			pat.patient_name.as_("patient_name"),
			pmr.communication_date,
			pmr.reference_doctype,
			pmr.reference_name,
			pmr.subject,
			pmr.attach
		)
		.where(pmr.patient.isin(allowed_patients))
	)

	if patient:
		query = query.where(pmr.patient == patient)
		
	# Security: Ensure we don't fetch deleted or unauthorized rows
	# docstatus logic is omitted as PMR doesn't usually use submittable docstatus rigidly, 
	# but we only want active/open records.
	query = query.orderby(pmr.communication_date, order=Order.desc)

	return query.run(as_dict=True)


@frappe.whitelist()
def get_orders():
	patients = get_patients_with_relations()

	# Get all tests via service requests for the patients
	tests_via_service_requests = get_data_from_service_requests(patients)
	service_request_map = build_order_map(tests_via_service_requests)

	# Get all tests via sale invoice for the patients
	tests_via_invoices = get_data_from_invoices(patients)
	invoice_map = build_order_map(tests_via_invoices, True)

	all_tests = {**service_request_map, **invoice_map}

	# sort by date descending
	sorted_tests = sorted(all_tests.items(), key=lambda x: x[0][1], reverse=True)

	return list(dict(sorted_tests).values())


def build_order_map(orders, from_invoice=False):
	orders_map = {}
	for row in orders:
		patient_doc = frappe.get_doc("Patient", row.patient)
		row["days"] = patient_doc.calculate_age().get("age_in_days") or 0
		key = (row.order_name, row.order_date)
		if key not in orders_map:
			billing_status = (
				"Paid"
				if row.billing_status in ["Invoiced", "Paid"]
				else "Partly Paid"
				if row.billing_status in ["Partly Invoiced", "Partly Paid"]
				else "Unpaid"
			)

			orders_map[key] = {
				"order_name": row.order_name,
				"patient": row.patient,
				"patient_name": row.patient_name,
				"ref_practitioner": row.ref_practitioner_name,
				"order_date": row.order_date,
				"diagnostic_report": row.diagnostic_report,
				"diagnostic_report_status": row.diagnostic_report_status,
				"billing_status": billing_status,
				"collection_point": row.collection_point,
				"invoice": [],
				"patient_image": row.patient_image,
				"tests": [],
			}

		invoice = None
		if row.billing_status in ["Invoiced", "Partly Invoiced", "Paid", "Partly Paid"]:
			if from_invoice:
				invoice = row.order_name
			else:
				invoice = frappe.db.get_value(
					"Sales Invoice Item", {"reference_dn": row.service_request, "docstatus": 1}, "parent"
				)

		if invoice and not invoice in orders_map[key]["invoice"]:
			orders_map[key]["invoice"].append(invoice)

		orders_map[key]["tests"].append(build_template_dict(row))

	return orders_map


def build_template_dict(row):
	test_dict = {
		"observation_template": row.observation_template,
		"service_request": row.get("service_request"),
		"observation": row.observation,
		"reference": get_observation_reference(row) if row.observation else None,
		"result": get_observation_result(row) if row.observation else None,
		"uom": row.permitted_unit,
		"observation_status": "Approved" if row.observation else "Pending",
		"sample_collection_required": row.sample_collection_required,
		"sample_collection": row.sample_collection,
		"observation_sample_collection": row.observation_sample_collection,
		"sample_collection_status": row.sample_collection_status,
		"collection_date_time": row.collection_date_time,
		"has_component": row.has_component,
		"children": [],
	}

	if row.has_component:
		test_dict["children"] = get_child_observations(row)

	return test_dict


def get_child_observations(row):
	if not row.has_component:
		return []

	child_templates = frappe.db.get_all(
		"Observation Component",
		filters={
			"parent": row.observation_template,
			"parentfield": "observation_component",
			"parenttype": "Observation Template",
		},
		pluck="observation_template",
	)

	components = []
	if row.component_observations and isinstance(row.component_observations, str):
		components = json.loads(row.component_observations)

	child_observations = []

	if row.observation:
		child_observations = frappe.get_all(
			"Observation",
			filters={"parent_observation": row.observation, "docstatus": 1, "status": "Approved"},
			fields=["*"],
		)

	results = []
	for obs in child_observations:
		sample_details = next(
			(item for item in components if item.get("observation_template") == obs.observation_template),
			None,
		)
		results.append(
			{
				"observation_template": obs.observation_template,
				"service_request": obs.get("service_request"),
				"observation": obs.name,
				"observation_status": "Approved" if obs.get("docstatus") == 1 else "Pending",
				"reference": get_observation_reference(obs),
				"result": get_observation_result(obs) if obs.get("docstatus") == 1 else None,
				"uom": obs.get("permitted_unit"),
				"sample_collection_required": obs.sample_collection_required,
				"sample_collection": row.sample_collection,
				"observation_sample_collection": row.observation_sample_collection,
				"sample_collection_status": sample_details.get("status"),
				"collection_date_time": sample_details.get("collection_date_time"),
				"has_component": obs.get("has_component"),
			}
		)
		child_templates.remove(obs.observation_template)

	if child_templates:
		for child in child_templates:
			sample_details = next(
				(item for item in components if item["observation_template"] == child), None
			)
			obs = frappe._dict(
				{
					"observation_template": child,
					"gender": row.gender,
					"days": row.days,
				}
			)
			template_doc = frappe.db.get_value(
				"Observation Template", child, ["permitted_unit", "sample_collection_required"], as_dict=True
			)

			results.append(
				{
					"observation_template": child,
					"service_request": row.get("service_request"),
					"observation": None,
					"reference": get_observation_reference(obs) if obs else None,
					"result": None,
					"uom": template_doc.permitted_unit,
					"observation_status": None,
					"sample_collection_required": template_doc.sample_collection_required,
					"sample_collection": row.sample_collection,
					"observation_sample_collection": row.observation_sample_collection,
					"sample_collection_status": sample_details.get("status"),
					"has_component": template_doc.has_component,
				}
			)

	return results


def get_data_from_service_requests(patients):
	service_request = frappe.qb.DocType("Service Request")
	observation = frappe.qb.DocType("Observation")
	observation_template = frappe.qb.DocType("Observation Template")
	sample_collection = frappe.qb.DocType("Sample Collection")
	sample_collection_item = frappe.qb.DocType("Observation Sample Collection")
	diagnostic_report = frappe.qb.DocType("Diagnostic Report")
	patient = frappe.qb.DocType("Patient")
	practitioner = frappe.qb.DocType("Healthcare Practitioner")

	rows = (
		frappe.qb.from_(service_request)
		.left_join(observation)
		.on(
			(service_request.name == observation.service_request)
			& (observation.docstatus == 1)
			& (observation.status == "Approved")
		)
		.left_join(observation_template)
		.on(service_request.template_dn == observation_template.name)
		.left_join(sample_collection_item)
		.on(service_request.name == sample_collection_item.service_request)
		.left_join(sample_collection)
		.on(sample_collection_item.parent == sample_collection.name)
		.left_join(diagnostic_report)
		.on(service_request.order_group == diagnostic_report.docname)
		.left_join(patient)
		.on(service_request.patient == patient.name)
		.left_join(practitioner)
		.on(service_request.practitioner == practitioner.name)
		.select(
			service_request.name.as_("service_request"),
			service_request.order_group.as_("order_name"),
			service_request.patient,
			service_request.patient_name,
			service_request.practitioner.as_("ref_practitioner"),
			practitioner.practitioner_name.as_("ref_practitioner_name"),
			service_request.order_date,
			service_request.billing_status,
			service_request.template_dn.as_("observation_template"),
		)
		.select(
			observation.name.as_("observation"),
			observation.result_data,
			observation.result_text,
			observation.result_select,
		)
		.select(
			observation_template.permitted_unit,
			observation_template.permitted_data_type,
			observation_template.sample_collection_required,
			observation_template.has_component,
		)
		.select(
			sample_collection_item.name.as_("observation_sample_collection"),
			sample_collection_item.parent.as_("sample_collection"),
			sample_collection_item.collection_date_time,
			sample_collection_item.component_observations.as_("component_observations"),
		)
		.select(
			sample_collection.status.as_("sample_collection_status"),
			sample_collection.collection_point,
		)
		.select(
			diagnostic_report.name.as_("diagnostic_report"),
			diagnostic_report.status.as_("diagnostic_report_status"),
		)
		.select(
			patient.sex.as_("gender"),
			patient.image.as_("patient_image"),
		)
		.where(service_request.patient.isin(patients))
		.where(service_request.status != "revoked-Request Status")
		.where(service_request.docstatus != 2)
		.where(service_request.template_dt == "Observation Template")
		.orderby(service_request.order_date, order=Order.desc)
	)

	return rows.run(as_dict=True)


def get_data_from_invoices(patients):
	diagnostic_report = frappe.qb.DocType("Diagnostic Report")
	si_item = frappe.qb.DocType("Sales Invoice Item")
	si = frappe.qb.DocType("Sales Invoice")
	observation = frappe.qb.DocType("Observation")
	observation_template = frappe.qb.DocType("Observation Template")
	sample_collection = frappe.qb.DocType("Sample Collection")
	sample_collection_item = frappe.qb.DocType("Observation Sample Collection")
	patient = frappe.qb.DocType("Patient")

	rows = (
		frappe.qb.from_(diagnostic_report)
		.left_join(si_item)
		.on((diagnostic_report.docname == si_item.parent) & (si_item.reference_dn.isnull()))
		.left_join(si)
		.on(si.name == si_item.parent)
		.left_join(observation_template)
		.on(si_item.item_code == observation_template.item)
		.left_join(sample_collection)
		.on(diagnostic_report.docname == sample_collection.reference_name)
		.left_join(sample_collection_item)
		.on(
			(sample_collection.name == sample_collection_item.parent)
			& (observation_template.name == sample_collection_item.observation_template)
		)
		.left_join(observation)
		.on(
			(
				(diagnostic_report.docname == observation.sales_invoice)
				| (sample_collection.name == observation.reference_docname)
			)
			& (observation.docstatus == 1)
			& (observation.status == "Approved")
			& (observation_template.name == observation.observation_template)
		)
		.left_join(patient)
		.on(diagnostic_report.patient == patient.name)
		.select(
			diagnostic_report.docname.as_("order_name"),
			diagnostic_report.patient,
			diagnostic_report.patient_name,
			diagnostic_report.practitioner.as_("ref_practitioner"),
			diagnostic_report.practitioner_name.as_("ref_practitioner_name"),
			diagnostic_report.reference_posting_date.as_("order_date"),
			diagnostic_report.name.as_("diagnostic_report"),
			diagnostic_report.status.as_("diagnostic_report_status"),
		)
		.select(
			si.status.as_("billing_status"),
		)
		.select(
			observation_template.name.as_("observation_template"),
			observation_template.permitted_unit,
			observation_template.permitted_data_type,
			observation_template.sample_collection_required,
			observation_template.has_component,
		)
		.select(
			observation.name.as_("observation"),
			observation.result_data,
			observation.result_text,
			observation.result_select,
		)
		.select(
			sample_collection_item.name.as_("observation_sample_collection"),
			sample_collection_item.parent.as_("sample_collection"),
			sample_collection_item.collection_date_time,
			sample_collection_item.component_observations.as_("component_observations"),
		)
		.select(
			sample_collection.status.as_("sample_collection_status"),
			sample_collection.collection_point,
		)
		.select(
			patient.sex.as_("gender"),
			patient.image.as_("patient_image"),
		)
		.where(diagnostic_report.patient.isin(patients))
		.where(observation_template.name.isnotnull())
		.where(si.docstatus == 1)
		.orderby(diagnostic_report.reference_posting_date, order=Order.desc)
		.orderby(si_item.idx, order=Order.asc)
	)

	return rows.run(as_dict=True)


def get_observation_result(obs_data):
	result = None
	template_doc = frappe.get_doc("Observation Template", obs_data.observation_template)
	if template_doc.permitted_data_type in ["Range", "Ratio", "Quantity", "Numeric"]:
		result = obs_data.result_data
	elif obs_data.permitted_data_type == "Text":
		result = obs_data.result_text
	elif obs_data.permitted_data_type == "Select":
		result = obs_data.result_select

	return result


def get_payment_gateway():
	return frappe.db.get_single_value("Healthcare Settings", "payment_gateway")


def get_controller(payment_gateway):
	if "payments" in frappe.get_installed_apps():
		from payments.utils import get_payment_gateway_controller

		return get_payment_gateway_controller(payment_gateway)


def validate_currency(payment_gateway, currency):
	controller = get_controller(payment_gateway)
	controller().validate_transaction_currency(currency)


@frappe.whitelist()
def get_payment_link(
	doctype,
	docname,
	title,
	amount,
	total_amount,
	currency,
	patient,
	redirect_to,
):
	payment_gateway = get_payment_gateway()
	if not payment_gateway:
		frappe.throw(_("Payment Gateway not configured in Healthcare Settings"))

	amount_with_gst = total_amount if total_amount != amount else 0
	payment = record_payment(patient, doctype, docname, amount, currency, amount_with_gst)

	if payment_gateway == "GoPayFast":
		from gopayfast_gateway.api import initiate_payment

		payment_data = initiate_payment(
			amount=float(amount_with_gst or amount),
			reference_doctype="Healthcare Payment Record",
			reference_docname=payment.name
		)

		return frappe.render_template(
			"gopayfast_gateway/templates/pages/payment_redirect.html",
			{
				"redirect_url": payment_data["redirect_url"],
				"params": payment_data["params"]
			}
		)

	controller = get_controller(payment_gateway)
	if not controller:
		frappe.throw(_("Failed to get Payment Gateway Controller"))

	payment_details = {
		"amount": total_amount,
		"title": f"Payment for {doctype} {title} {docname}",
		"description": f"{patient}'s Consultation Charge payment for {title}",
		"reference_doctype": doctype,
		"reference_docname": docname,
		"payer_email": frappe.session.user,
		"payer_name": patient,
		"currency": currency,
		"payment_gateway": payment_gateway,
		"redirect_to": redirect_to,
		"payment": payment.name,
	}
	if payment_gateway == "Razorpay":
		order = controller.create_order(**payment_details)
		payment_details.update({"order_id": order.get("id")})

	url = controller.get_payment_url(**payment_details)

	return url


def record_payment(
	patient,
	doctype,
	docname,
	amount,
	currency,
	amount_with_gst=0,
):
	payment_doc = frappe.new_doc("Healthcare Payment Record")
	payment_doc.update(
		{
			"user": frappe.session.user,
			"patient": patient,
			"amount": amount,
			"currency": currency,
			"amount_with_gst": amount_with_gst,
			"payment_for_doctype": doctype,
			"payment_for_document": docname,
		}
	)

	payment_doc.save(ignore_permissions=True)
	return payment_doc


def update_payment_record(doctype, docname):
	request = frappe.get_all(
		"Integration Request",
		{
			"reference_doctype": doctype,
			"reference_docname": docname,
			"owner": frappe.session.user,
		},
		order_by="creation desc",
		limit=1,
	)

	if len(request):
		data = frappe.db.get_value("Integration Request", request[0].name, "data")
		data = frappe._dict(json.loads(data))

		payment_gateway = data.get("payment_gateway")
		if payment_gateway == "Razorpay":
			payment_id = "razorpay_payment_id"
		elif "Stripe" in payment_gateway:
			payment_id = "stripe_token_id"
		else:
			payment_id = "order_id"

		payment_doc = frappe.get_doc("Healthcare Payment Record", data.payment)
		payment_doc.update(
			{
				"status": "Captured",
				"payment_id": data.get(payment_id),
				"order_id": data.get("order_id"),
				"signature": data.get("razorpay_signature") or data.get("signature"),
			},
		)
		payment_doc.save(ignore_permissions=True)


@frappe.whitelist()
def get_therapy_plan_templates():
	return frappe.db.get_all(
		"Therapy Plan Template", 
		fields=["name", "plan_name", "total_sessions"],
		order_by="plan_name asc"
	)


@frappe.whitelist()
def get_therapy_plan_frequencies():
	return frappe.db.get_all(
		"Therapy Plan Frequency",
		fields=["name", "frequency_name", "duration_in_days", "sessions_per_duration"],
		order_by="name asc"
	)


@frappe.whitelist()
def get_therapy_plan_template_details(template_name):
	"""Fetch therapy plan template details including therapy types"""
	if not template_name:
		return None
	
	template = frappe.get_doc("Therapy Plan Template", template_name)
	
	therapy_types = []
	for item in template.therapy_types:
		therapy_types.append({
			"therapy_type": item.therapy_type,
			"no_of_sessions": item.no_of_sessions
		})
	
	return {
		"name": template.name,
		"plan_name": template.plan_name,
		"total_sessions": template.total_sessions,
		"therapy_types": therapy_types
	}


@frappe.whitelist()
def get_therapy_types_for_plan(therapy_plan):
	return frappe.db.get_all(
		"Therapy Plan Detail",
		filters={"parent": therapy_plan},
		fields=["therapy_type", "no_of_sessions", "sessions_completed"],
	)


@frappe.whitelist()
def get_therapy_type_fee(therapy_type):
	rate = frappe.db.get_value("Therapy Type", therapy_type, "rate")
	currency = erpnext.get_default_currency()
	return {"rate": rate, "currency": currency}


@frappe.whitelist()
def get_therapy_types_for_plan(therapy_plan):
	return frappe.db.get_all(
		"Therapy Plan Detail",
		filters={"parent": therapy_plan},
		fields=["therapy_type", "no_of_sessions", "sessions_completed"],
	)


@frappe.whitelist()
def get_therapy_sessions():
	patients = get_patients_with_relations()
	if not patients:
		return []

	return frappe.db.get_all(
		"Therapy Session",
		filters={"patient": ["in", patients]},
		fields=[
			"name",
			"therapy_type",
			"therapy_plan",
			"practitioner",
			"start_date",
			"start_time",
			"start_time",
			"duration",
			"invoiced",
			"docstatus",
		],
		order_by="start_date desc, start_time desc",
	)


@frappe.whitelist()
def make_therapy_session(therapy_plan, therapy_type, start_date, start_time, practitioner=None):
	plan_doc = frappe.get_doc("Therapy Plan", therapy_plan)
	
	# Verify patient access
	patients = get_patients_with_relations()
	if plan_doc.patient not in patients:
		frappe.throw(_("Not authorized to book session for this patient"))
	
	if plan_doc.status == "Completed":
		frappe.throw(_("Cannot book session for a completed therapy plan"))

	session = frappe.new_doc("Therapy Session")
	session.therapy_plan = therapy_plan
	session.patient = plan_doc.patient
	session.therapy_type = therapy_type
	session.start_date = start_date
	session.start_time = start_time
	
	if practitioner:
		session.practitioner = practitioner
	
	# Fetch duration from Therapy Type
	if not session.duration:
		session.duration = frappe.db.get_value("Therapy Type", therapy_type, "default_duration")

	try:
		session.insert(ignore_permissions=True)
	except Exception as e:
		frappe.log_error(f"Failed to create session: {str(e)}", "Therapy Session Booking Failed")
		frappe.throw(_("Could not book session. Please contact support."))

	return session


@frappe.whitelist()
def cancel_therapy_plan(therapy_plan):
	# Verify patient access
	plan = frappe.get_doc("Therapy Plan", therapy_plan)
	patients = get_patients_with_relations()
	if plan.patient not in patients:
		frappe.throw(_("Not authorized to cancel this plan"))

	# Update Plan Status
	if plan.status != "Cancelled":
		frappe.db.set_value("Therapy Plan", plan.name, "status", "Cancelled")
		frappe.db.commit()
	
	# Cancel future sessions
	from frappe.utils import now_datetime
	future_sessions = frappe.db.get_all("Therapy Session", filters={
		"therapy_plan": therapy_plan,
		"start_date": [">=", frappe.utils.nowdate()],
		"invoiced": 0
	}, fields=["name", "start_date", "start_time", "docstatus"])
	
	for session_data in future_sessions:
		# Check time for today's sessions
		s_dt = datetime.combine(getdate(session_data.start_date), get_time(session_data.start_time))
		if s_dt < now_datetime():
			continue 
			
		try:
			if session_data.docstatus == 1:
				frappe.get_doc("Therapy Session", session_data.name).cancel()
			else:
				frappe.delete_doc("Therapy Session", session_data.name)
		except Exception:
			pass
			
	return {"status": "success"}


@frappe.whitelist()
def get_therapy_plans():
	patients = get_patients_with_relations()
	if not patients:
		return []

	return frappe.db.get_all(
		"Therapy Plan",
		filters={"patient": ["in", patients], "status": ["!=", "Cancelled"]},
		fields=["name", "therapy_plan_template", "start_date", "status", "total_sessions", "total_sessions_completed", "patient_name", "patient"],
		order_by="start_date desc"
	)


@frappe.whitelist(methods=["POST"])
def create_therapy_plan(template, patient, sessions=None, relative_details=None, frequency=None, start_date=None):
	if relative_details:
		if isinstance(relative_details, str):
			relative_details = json.loads(relative_details)
		
		# Create new patient for relative
		try:
			new_patient = frappe.new_doc("Patient")
			new_patient.first_name = relative_details.get("first_name")
			new_patient.last_name = relative_details.get("last_name")
			new_patient.sex = relative_details.get("gender")
			new_patient.mobile = relative_details.get("mobile")
			new_patient.email = relative_details.get("email")
			new_patient.dob = relative_details.get("dob")
			new_patient.flags.ignore_mandatory = True 
			new_patient.insert(ignore_permissions=True)
			
			# Add to current user's patient relations
			user_patient_name = frappe.db.get_value("Patient", {"user_id": frappe.session.user}, "name")
			if user_patient_name:
				user_patient = frappe.get_doc("Patient", user_patient_name)
				user_patient.append("patient_relation", {
					"patient": new_patient.name,
					"relation": "Other"
				})
				user_patient.save(ignore_permissions=True)
			
			patient = new_patient.name
		except Exception as e:
			frappe.log_error(f"Failed to create relative patient: {str(e)}")
			frappe.throw(_("Could not create patient profile for relative."))

	plan = frappe.new_doc("Therapy Plan")
	plan.patient = patient
	plan.therapy_plan_template = template
	plan.set_therapy_details_from_template()
	plan.start_date = start_date or getdate()
	
	if frequency:
		plan.frequency = frequency

	plan.company = frappe.defaults.get_user_default("Company") or frappe.db.get_single_value("Global Defaults", "default_company")
	plan.status = "Not Started"
	plan.insert(ignore_permissions=True)

	if sessions:
		if isinstance(sessions, str):
			sessions = json.loads(sessions)
			
		for session_data in sessions:
			create_session(plan, session_data)

	return plan.name


def create_session(plan, data):
	session = frappe.new_doc("Therapy Session")
	session.therapy_plan = plan.name
	session.patient = plan.patient
	session.therapy_type = data.get("therapy_type")
	session.practitioner = data.get("practitioner")
	session.start_date = data.get("start_date")
	session.start_time = data.get("start_time")
	session.description = f"Session for {plan.name}"
	session.insert(ignore_permissions=True)



@frappe.whitelist(methods=["POST"])
def cancel_appointment(appointment_id):
	from healthcare.healthcare.doctype.patient_appointment.patient_appointment import update_status

	appointment = frappe.get_doc("Patient Appointment", appointment_id)
	
	# Check authorization - verify patient belongs to current user or their relations
	patients = get_patients_with_relations()
	if appointment.patient not in patients:
		frappe.throw(_("Not authorized to cancel this appointment"))
	
	if appointment.status == "Cancelled":
		frappe.throw(_("Appointment is already cancelled"))

	update_status(appointment_id, "Cancelled")
	return True


@frappe.whitelist(methods=["POST"])
def cancel_therapy_session(session_id):
	session = frappe.get_doc("Therapy Session", session_id)
	
	# Verify patient access
	patients = get_patients_with_relations()
	if session.patient not in patients:
		frappe.throw(_("Not authorized to cancel this session"))

	if session.docstatus == 2: # Cancelled
		frappe.throw(_("Session is already cancelled"))

	if session.invoiced:
		frappe.throw(_("Cannot cancel an invoiced session"))

	if session.docstatus == 0: # Draft
		# Check for linked Payment Records
		payment_records = frappe.get_all(
			"Healthcare Payment Record",
			filters={
				"payment_for_doctype": "Therapy Session",
				"payment_for_document": session.name
			},
			fields=["name", "status"]
		)
		
		for payment in payment_records:
			if payment.status == "Captured":
				frappe.throw(_("Cannot cancel session with captured payment"))
			else:
				# Delete pending/failed payments to allow session deletion
				frappe.delete_doc("Healthcare Payment Record", payment.name, ignore_permissions=True)

		# Delete draft sessions
		frappe.delete_doc("Therapy Session", session.name, ignore_permissions=True)
	elif session.docstatus == 1: # Submitted
		# Cancel submitted sessions
		session.flags.ignore_permissions = True
		session.cancel()
		
	return True


@frappe.whitelist(allow_guest=True, methods=["POST"])
def register_patient(first_name, last_name, email, mobile, gender):
	"""
	Register a new patient with user account creation.
	This is accessible to guest users for self-registration.
	"""
	# Validate required fields
	if not first_name:
		frappe.throw(_("First Name is required"))
	if not email:
		frappe.throw(_("Email is required"))
	if not mobile:
		frappe.throw(_("Mobile Number is required"))
	if not gender:
		frappe.throw(_("Gender is required"))
	
	# Check for existing user with same email
	if frappe.db.exists("User", {"email": email}):
		frappe.throw(_("An account with this email already exists. Please login instead."))
	
	# Check for existing user with same mobile
	if mobile and frappe.db.exists("User", {"mobile_no": mobile}):
		frappe.throw(_("An account with this mobile number already exists."))
	
	try:
		# Create the patient record
		patient = frappe.new_doc("Patient")
		patient.first_name = first_name
		patient.last_name = last_name
		patient.email = email
		patient.mobile = mobile
		patient.sex = gender
		patient.status = "Active"
		patient.invite_user = 1  # This triggers user creation via create_website_user()
		
		patient.insert(ignore_permissions=True)
		
		return {
			"success": True,
			"message": _("Registration successful! Please check your email for login instructions."),
			"patient": patient.name
		}
	except frappe.exceptions.DuplicateEntryError as e:
		frappe.throw(_("An account with this email or mobile already exists."))
	except Exception as e:
		frappe.log_error(f"Patient registration error: {str(e)}", "Patient Registration")
		frappe.throw(_("Registration failed. Please try again."))


@frappe.whitelist()
def retry_payment(doctype, docname):
	doc = frappe.get_doc(doctype, docname)
	patients = get_patients_with_relations()
	
	if doc.patient not in patients:
		frappe.throw(_("Not authorized to pay for this document"))

	amount = 0
	title = ""
	currency = erpnext.get_default_currency()
	
	if doctype == "Patient Appointment":
		if doc.status not in ["Open"]:
			frappe.throw(_("This appointment is not in a payable state"))
		
		# Calculate fee
		try:
			billing_details = get_appointment_billing_item_and_rate(doc)
			amount = billing_details.get("practitioner_charge", 0)
		except Exception:
			amount = 0
			
		title = f"Appointment with {doc.practitioner_name}"
		
	elif doctype == "Therapy Session":
		if doc.invoiced:
			frappe.throw(_("This session is already invoiced"))
		if doc.docstatus == 2:
			frappe.throw(_("Cannot pay for cancelled session"))

		# Calculate fee
		rate_data = get_therapy_type_fee(doc.therapy_type)
		amount = rate_data.get("rate", 0)
		title = f"Therapy Session - {doc.therapy_type}"
	
	else:
		frappe.throw(_("Invalid Document Type"))

	if amount <= 0:
		frappe.throw(_("No payment required for this record"))

	return get_payment_link(
		doctype=doctype,
		docname=docname,
		title=title,
		amount=amount,
		total_amount=amount,
		currency=currency,
		patient=doc.patient,
		redirect_to="/patient_portal"
	)
