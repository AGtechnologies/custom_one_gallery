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

	columns = [_("Customer SKU") + "::140",
		_("Sales Quantity per month <past 6 months>") + ":Float:100",
		_("Total Sales Quantity") + ":Float:110",
		_("Average Sales") + ":Float:100",
		_("Scrap Quantity") + ":Float:100",
		_("Warehouse-in transit") + ":Float:100",
		_("Warehouse Balance Quantity") + ":Float:100"]

	return columns

def get_conditions(filters):
	conditions = ""

	if filters.get("date"):
		conditions += "and so.transaction_date <= '%s'" % frappe.db.escape(filters["date"])

	return conditions

def get_data(filters):
	#conditions = get_conditions(filters)
	sales_list = get_sales_list(filters)
	data = []

	for sales in sales_list:
		avg_sales = sales.quantity/6
		data.append([sales.customer_name,sales.quantity,sales.tot_quantity,avg_sales,sales.quantity,sales.quantity,sales.quantity])

	return data

def get_sales_list(filters):
	conditions = get_conditions(filters)
	#conditions = []
	# aa="""select naming_series, posting_date, base_grand_total, base_paid_amount from `tabSales Invoice` where %s order by posting_date""" % conditions
	# frappe.throw(_(aa))
	sales_list = frappe.db.sql("""select cu.customer_name, sum(so_item.qty) as quantity, sum(so_item.qty) as tot_quantity from `tabSales Order` so, `tabSales Order Item` so_item, `tabCustomer` cu where so_item.parent = so.name and so.customer=cu.name %s group by so.customer""" %
		conditions, as_dict=1)

	return sales_list
