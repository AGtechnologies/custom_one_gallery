# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, today

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns(filters)
	data = get_data(filters)
	
	return columns,data

def get_columns(filters):
	"""return columns based on filters"""

	columns = [_("Invoice No") + "::140", _("Invoice Date") + "::100",
		_("Invoice Amount") + ":Float:110", _("Paid Amount") + ":Float:100",
		_("Balance Amount") + ":Float:100"]

	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("to_date"):
		conditions += " due_date <= '%s'" % frappe.db.escape(filters["to_date"])

	else:
		frappe.throw(_("'Date' is required"))

	if filters.get("customer"):
		#frappe.throw(_(filters["customer"]))
		conditions += " and customer = '%s'" % filters["customer"]

	return conditions

def get_data(filters):
	#conditions = get_conditions(filters)
	cust_list = get_cust_list(filters)
	data = []

	for cust in cust_list:
		balance = cust.base_grand_total - cust.base_paid_amount
		data.append([cust.naming_series,cust.posting_date,cust.base_grand_total,cust.base_paid_amount,balance])

	return data

def get_cust_list(filters):
	conditions = get_conditions(filters)
	#conditions = []
	# aa="""select naming_series, posting_date, base_grand_total, base_paid_amount from `tabSales Invoice` where %s order by posting_date""" % conditions
	# frappe.throw(_(aa))
	cust_list = frappe.db.sql("""select naming_series, posting_date, base_grand_total, base_paid_amount from `tabSales Invoice` where %s order by posting_date""" %
		conditions, as_dict=1)

	return cust_list
