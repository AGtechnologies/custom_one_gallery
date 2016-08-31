# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from datetime import datetime,timedelta
from frappe.utils import flt, getdate, today

def execute(filters=None):
	if not filters: filters = {}

	condition,months,item_condition=get_condition(filters)
	columns = get_columns()
	items = get_item_info(item_condition)

	total_no_months = 6
	scrap_quantity = 0
	warehouse_bal_quantity = 0
	warehouse_in_transit = 0
	data = []
	for item in items:
		
		lmonths=months.copy()

		so_items_map=get_sales_items(condition,item.item_name)
		scrap_quantity=get_scrap_quantity(condition,item.item_name)
		warehouse_in_transit=get_warehouse_transit(condition,item.item_name)
		warehouse_bal_quantity=get_stock_balance(condition,item.item_name)
		for so_items in so_items_map:
			mon=int(str(so_items.transaction_date)[5:7])
			monqty=lmonths.get(mon,0) + so_items.so_qty
			lmonths.update({mon:monqty})

		total_sales_quantity = 0
		
		datalist=[item.name, item.item_name]
		for i in lmonths:
			iqty=lmonths.get(i,0)
			total_sales_quantity+=iqty
			datalist.append(iqty)
		
		avg_sales_quantity = float(total_sales_quantity)/total_no_months
		reorder_quantity = scrap_quantity + avg_sales_quantity - warehouse_bal_quantity - warehouse_in_transit
		datalist+=[total_sales_quantity, total_no_months, avg_sales_quantity, scrap_quantity, warehouse_bal_quantity, warehouse_in_transit, reorder_quantity]
		data.append(datalist)
	#frappe.throw(repr(data))
	return columns ,data

def get_item_info(item_condition):
	if item_condition:
		query="select name, item_name from tabItem where %s" % item_condition
		#frappe.throw(repr(query))
		return frappe.db.sql(query, as_dict=1)

	return frappe.db.sql("select name, item_name from tabItem", as_dict=1)

def get_scrap_quantity(condition, item_name):
	condition=" and it.item_name ='%s'" %item_name
	query="""select bi.actual_qty
		from `tabBin` bi, `tabWarehouse` wh, `tabItem` it
		where wh.name = bi.warehouse and bi.item_code = it.name and wh.warehouse_name='Warehouse- Scrap' %s""" % (condition)
	sc_items = frappe.db.sql(query, as_dict=1)
	if not sc_items:
		return 0
	#frappe.throw(repr(sc_items))
	return sc_items[0].actual_qty

def get_warehouse_transit(condition, item_name):
	condition=" and it.item_name ='%s'" %item_name
	query="""select bi.actual_qty
		from `tabBin` bi, `tabWarehouse` wh, `tabItem` it
		where wh.name = bi.warehouse and bi.item_code = it.name and wh.warehouse_name='Warehouse-in transit' %s""" % (condition)
	sc_items = frappe.db.sql(query, as_dict=1)
	if not sc_items:
		return 0
	#frappe.throw(repr(sc_items))
	return sc_items[0].actual_qty

def get_stock_balance(condition, item_name):
	condition=" and it.item_name ='%s'" %item_name
	query="""select bi.actual_qty
		from `tabBin` bi, `tabWarehouse` wh, `tabItem` it
		where wh.name = bi.warehouse and bi.item_code = it.name %s""" % (condition)
	sc_items = frappe.db.sql(query, as_dict=1)
	if not sc_items:
		return 0
	#frappe.throw(repr(sc_items))
	return sc_items[0].actual_qty

def get_sales_items(condition, item_name):
	condition+=" and so_item.item_name ='%s'" %item_name
	query="""select so_item.item_name, so.transaction_date, sum(so_item.qty) as so_qty
		from `tabSales Order` so, `tabSales Order Item` so_item
		where so.name = so_item.parent %s group by so.transaction_date""" % (condition)
	#frappe.throw(query)
	so_items = frappe.db.sql(query, as_dict=1)
	#frappe.throw(repr(so_items))
	return so_items


def get_columns():
	columns = [_("Product ID") + "::100",_("Product Name") + "::100",_("1st Month Sales Quantity") + ":Float:100",_("2nd Month Sales Quantity") + ":Float:100",_("3rd Month Sales Quantity") + ":Float:100",_("4th Month Sales Quantity") + ":Float:100",_("5th Month Sales Quantity") + ":Float:100",_("6th Month Sales Quantity") + ":Float:100",_("Total Sales Quantity") + ":Float:100",_("Total No of Months") + "::100",_("Average Sales Quantity") + ":Float:100",_("Scrap Warehouse Quantity") + ":Float:100",_("Stock Balance") + ":Float:100",_("Warehouse-in Transit") + ":Float:100",_("Reorder Quantity") + ":Float:100"
		]
		
	return columns

def get_condition(filters):
	conditions = ""
	item_condition=""
	months={}
	if filters.get("to_date"):
		to_date=filters.get("to_date")[0:7] + "-01"
		to_da=datetime.strptime(to_date,"%Y-%m-%d")
		from_da= to_da - timedelta(6*365/12)
		
		from_date=from_da.strftime('%Y-%m-%d')
		#frappe.throw(repr(filters.get("to_date")))
		conditions += " and so.transaction_date >= '%s' and so.transaction_date <= '%s'" % (from_date,to_date)
		#frappe.throw(conditions)
		flag=""
		while(from_da<to_da):
			if from_da.strftime('%m')!=flag:
				flag=from_da.strftime('%m')
				months.update({int(flag):0})
				
			from_da+=timedelta(1)

	else:
		frappe.throw(_("From and To dates required"))

	if filters.get("item"):
		item_condition += " item_code = '%s'" % filters["item"]

		#frappe.throw(repr(item_condition))

	return conditions,months,item_condition
