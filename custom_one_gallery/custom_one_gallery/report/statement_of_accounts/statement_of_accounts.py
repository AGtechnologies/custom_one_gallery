# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from erpnext.accounts.report.accounts_receivable.accounts_receivable import ReceivablePayableReport
from datetime import datetime,timedelta
from frappe.utils import flt, getdate, today

#class AccountsReceivableSummary(ReceivablePayableReport):
def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns(filters)
	data = get_data(filters)
	
	return columns,data
	# def run(self, args):0-12 Days
	# 	party_naming_by = frappe.db.get_value(args.get("naming_by")[0], None, args.get("naming_by")[1])
	# 	return self.get_columns(party_naming_by, args)

def get_columns(filters):
	columns = [_("Invoice Date") + "::100",_("Document") + "::100",_("Invoice No.") + "::100",_("Customer's Contact Person") + "::100",_("Customer ID") + "::100",_("Payment Term") + "::100",_("Days Overdue") + "::100",
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
		if cust.contact_person:
			contact_person=cust.contact_person
		data.append([inv_date,'Invoice',cust.name,contact_person,cust.customer_id,cust.credit_days,days_overdue,cust.base_grand_total,aging1,aging2,aging3,aging4,total_bal,cust.currency_name])

	return data

def get_cust_list(filters):
	conditions = get_conditions(filters)
	#conditions = []
	# aa="""select naming_series, posting_date, base_grand_total, base_paid_amount from `tabSales Invoice` where %s order by posting_date""" % conditions
	# frappe.throw(_(aa))
	cust_list = frappe.db.sql("""select si.name, si.posting_date, si.due_date, si.naming_series, si.base_grand_total, si.contact_person, si.customer_name, cs.name as customer_id, cs.credit_days, cr.currency_name from `tabSales Invoice` si, `tabCustomer` cs, `tabCurrency` cr where cs.name=si.customer and cs.default_currency=cr.currency_name %s order by posting_date""" %
		conditions, as_dict=1)

	return cust_list
