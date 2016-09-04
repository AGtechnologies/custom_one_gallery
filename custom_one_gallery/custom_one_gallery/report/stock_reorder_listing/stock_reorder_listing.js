// Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
// License: GNU General Public License v3. See license.txt

frappe.query_reports["Stock Reorder Listing"] = {
	"filters": [
		{
			"fieldname":"item",
			"label": __("Item"),
			"fieldtype": "Link",
			"options": "Item"
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": get_today()
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": get_today()
		}
	]
}
