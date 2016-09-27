# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors
# License: GNU General Public License v3. See license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import flt, cstr
from frappe import msgprint, _

def execute(filters=None):
	if not filters: filters = {}
	
	salary_slips = get_salary_slips(filters)
	columns, earning_types, ded_types = get_columns(salary_slips)
	ss_earning_map = get_ss_earning_map(salary_slips)
	ss_ded_map = get_ss_ded_map(salary_slips)
	
	#frappe.throw(str(ss_earning_map)+str(ss_ded_map))
	data = []
	for ss in salary_slips:
		row = [ss.employee, ss.employee_name]
			
		for e in earning_types:
			row.append(ss_earning_map.get(ss.name, {}).get(e))
			
		row += [ss.gross_pay]
		
		for d in ded_types:
			row.append(ss_ded_map.get(ss.name, {}).get(d))
		
		row += [ss.total_deduction, ss.net_pay]
		
		data.append(row)
	
	return columns, data
	
def get_columns(salary_slips):
	columns = [
		_("Employee") + ":Link/Employee:120", _("Employee Name") + "::140"]
	
	
	earning_types = frappe.db.sql_list("""select distinct salary_component from `tabSalary Detail`
		where amount != 0 and parent in (%s)""" % (', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]))
		
		
	ded_types = frappe.db.sql_list("""select distinct salary_component from `tabSalary Detail`
		where amount != 0 and parent in (%s)""" % 
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]))
		
	columns = columns + [(e + ":Currency:120") for e in earning_types] + \
		["Gross Pay:Currency:120"] + \
		["Total Deduction:Currency:120", "Net Pay:Currency:120"]

	return columns, earning_types, ded_types
	
def get_salary_slips(filters):
	conditions, filters = get_conditions(filters)
	salary_slips = frappe.db.sql("""select * from `tabSalary Slip` where docstatus = 1 %s
		order by employee, month""" % conditions, filters, as_dict=1)
	
	if not salary_slips:
		msgprint(_("No salary slip found for month: ") + cstr(filters.get("month")) + 
			_(" and year: ") + cstr(filters.get("fiscal_year")), raise_exception=1)
	
	return salary_slips
	
def get_conditions(filters):
	conditions = ""
	if filters.get("month"):
		month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", 
			"Dec"].index(filters["month"]) + 1
		filters["month"] = month
		conditions += " and month = %(month)s"
	
	if filters.get("fiscal_year"): conditions += " and fiscal_year = %(fiscal_year)s"
	if filters.get("company"): conditions += " and company = %(company)s"
	if filters.get("employee"): conditions += " and employee = %(employee)s"
	
	return conditions, filters
	
def get_ss_earning_map(salary_slips):
	ss_earnings = frappe.db.sql("""select parent, salary_component, amount 
		from `tabSalary Detail` where parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)
	
	ss_earning_map = {}
	for d in ss_earnings:
		ss_earning_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		ss_earning_map[d.parent][d.salary_component] = flt(d.amount)
	
	return ss_earning_map

def get_ss_ded_map(salary_slips):
	ss_deductions = frappe.db.sql("""select parent, salary_component, amount 
		from `tabSalary Detail` where parent in (%s)""" %
		(', '.join(['%s']*len(salary_slips))), tuple([d.name for d in salary_slips]), as_dict=1)
	
	ss_ded_map = {}
	for d in ss_deductions:
		ss_ded_map.setdefault(d.parent, frappe._dict()).setdefault(d.salary_component, [])
		ss_ded_map[d.parent][d.salary_component] = flt(d.amount)
	
	return ss_ded_map