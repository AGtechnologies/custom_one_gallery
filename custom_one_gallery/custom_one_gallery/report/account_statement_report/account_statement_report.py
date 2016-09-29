# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt, getdate, today
from datetime import datetime,timedelta

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns(filters)
	data = get_data(filters)
	
	return columns,data

def get_columns(filters):
	columns = [_("Invoice Date") + "::100",_("Invoice No.") + "::100",_("Customer ID") + "::100",_("Payment Term") + "::100",_("Days Overdue") + "::100",
		_("Amount") + ":Float:140",
		_("0 - " + str(filters.range1) +" Days") + ":Float:100",
		_(str(filters.range1) + " - " + str(filters.range2) + " Days") + ":Float:100",
		_(str(filters.range2) + " - " + str(filters.range3) + " Days") + ":Float:100",
		_("Over " + str(filters.range3) + " Days") + ":Float:100",
		_("Total Outstanding Balance") + ":Float:100",
		_("Currency") + "::100"]
		
	return columns

def get_conditions(filters):
	conditions = ""
	if filters.get("ageing_based_on")=='Posting Date':
		if filters.get("report_date"):
			conditions += "and posting_date <= '%s'" % frappe.db.escape(filters["report_date"])
	elif filters.get("ageing_based_on")=='Due Date':
		if filters.get("report_date"):
			conditions += "and due_date <= '%s'" % frappe.db.escape(filters["report_date"])

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
		due_date=datetime.strptime(str(cust.due_date),'%Y-%m-%d')
		#current_date=datetime.now()
		current_date=datetime.strptime(str(filters.report_date),'%Y-%m-%d')
		days_overdue=(current_date-due_date).days
		inv_date=(datetime.strptime(str(cust.posting_date),'%Y-%m-%d')).strftime('%d-%m-%Y')
		contact_person=cust.customer_name
		aging1=0.0
		aging2=0.0
		aging3=0.0
		aging4=0.0
		total_bal=0.0
		if days_overdue >= 0 and days_overdue <= filters.range1:
			aging1=cust.base_grand_total
		elif days_overdue >filters.range1 and days_overdue <= filters.range2:
			aging2=cust.base_grand_total
		elif days_overdue >filters.range2 and days_overdue <= filters.range3:
			aging3=cust.base_grand_total
		elif days_overdue >filters.range3:
			aging4=cust.base_grand_total
		total_bal=aging1+aging2+aging3+aging4
		data.append([inv_date,cust.name,cust.customer_id,cust.credit_days,days_overdue,cust.base_grand_total,aging1,aging2,aging3,aging4,total_bal,cust.currency_name])

	return data

def get_cust_list(filters):
	conditions = get_conditions(filters)
	# frappe.throw(_(aa))
	cust_list = frappe.db.sql("""select si.name, si.posting_date, si.due_date, si.naming_series, si.base_grand_total, si.customer_name, cs.name as customer_id, cs.credit_days, cr.currency_name from `tabSales Invoice` si, `tabCustomer` cs, `tabCurrency` cr where cs.name=si.customer and cs.default_currency=cr.currency_name %s order by si.posting_date""" %
		conditions, as_dict=1)

	return cust_list