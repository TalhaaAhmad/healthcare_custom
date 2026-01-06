# Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
# GNU GPLv3 License. See license.txt

import frappe
from frappe.utils import cint, get_system_timezone

no_cache = 1


def get_context():
	context = frappe._dict()
	context.boot = get_boot()
	return context


def get_boot():
	return frappe._dict(
		{
			"frappe_version": frappe.__version__,
			"site_name": frappe.local.site,
			"csrf_token": frappe.sessions.get_csrf_token(),
			"setup_complete": cint(frappe.get_system_settings("setup_complete")),
			"is_guest": True,
			"timezone": {
				"system": get_system_timezone(),
			},
		}
	)
