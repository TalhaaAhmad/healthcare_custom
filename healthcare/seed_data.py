
import frappe

def seed():
    frequencies = [
        {"frequency_name": "Daily", "duration_in_days": 1, "sessions_per_duration": 1},
        {"frequency_name": "Weekly", "duration_in_days": 7, "sessions_per_duration": 1},
        {"frequency_name": "Twice a Week", "duration_in_days": 7, "sessions_per_duration": 2}
    ]

    for f in frequencies:
        if not frappe.db.exists("Therapy Plan Frequency", f["frequency_name"]):
            doc = frappe.new_doc("Therapy Plan Frequency")
            doc.update(f)
            doc.insert(ignore_permissions=True)
            print(f"Created {f['frequency_name']}")
    
    frappe.db.commit()
