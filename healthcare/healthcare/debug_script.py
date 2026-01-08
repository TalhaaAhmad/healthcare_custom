import frappe
from healthcare.healthcare.api.patient_portal import get_slots

def test_slots():
	try:
		slots = get_slots('HLC-PRAC-2026-00002', '2026-01-08')
		print(slots or 'No slots')
	except Exception as e:
		print(f"Error: {e}")

if __name__ == "__main__":
	frappe.connect()
	test_slots()
