
import frappe

def get_latest_error():
    logs = frappe.get_list("Error Log", limit=1, order_by="creation desc", fields=["error", "method"])
    if logs:
        print(logs[0].error)

