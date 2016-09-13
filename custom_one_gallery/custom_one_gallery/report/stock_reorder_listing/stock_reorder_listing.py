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
	columns = get_columns(months,item_condition)
	items = get_item_info(item_condition)

	data = []
	for item in items:
		lmonths={0:0,1:0,2:0,3:0,4:0,5:0}
		if len(months)<6:
			lmonths={}
			mf=0
			for m in months:
				lmonths.update({mf:0})
				mf+=1
		no_months = 0
		scrap_quantity = 0
		warehouse_bal_quantity = 0
		warehouse_in_transit = 0
		avg_sales_quantity=0.0
		scrap_quantity=get_scrap_quantity(condition,item.item_name)
		warehouse_in_transit=get_warehouse_transit(condition ,item.item_name)
		warehouse_bal_quantity=get_stock_balance(condition,item.item_name)
	
		for mon in months:
			localcondition=condition + " and so.transaction_date >= '%s' and so.transaction_date <= '%s'" % (mon.get('start',''),mon.get('end',''))
			so_items_map=get_sales_items(localcondition,item.item_name)
			if so_items_map:
				so_items=so_items_map[0]
				lmonths.update({no_months:so_items.so_qty})
			
			no_months+=1
			
		total_sales_quantity = 0.0
		#frappe.throw(str(lmonths))
		datalist=[item.name, item.item_name]
		for i in lmonths:
			iqty=lmonths.get(i,0)
			total_sales_quantity+=iqty
			datalist.append(str(iqty))
		#frappe.throw(repr(datalist))
		if no_months:
			avg_sales_quantity = round((float(total_sales_quantity)/no_months),2)
		reorder_quantity = round((scrap_quantity + avg_sales_quantity - warehouse_bal_quantity - warehouse_in_transit),2)
		
		datalist+=[total_sales_quantity, no_months, avg_sales_quantity, scrap_quantity, warehouse_bal_quantity, warehouse_in_transit, reorder_quantity]
		data.append(datalist)
	#frappe.throw(repr(data))
	return columns ,data

def get_item_info(item_condition):
	if item_condition:
		query="select it.name, it.item_name, um.uom_name from `tabItem` it, `tabUOM` um where it.stock_uom=um.name and %s" % item_condition
		#frappe.throw(repr(query))
		return frappe.db.sql(query, as_dict=1)

	return frappe.db.sql("select it.name, it.item_name, um.uom_name as uom_name from `tabItem` it, `tabUOM` um where it.stock_uom=um.name", as_dict=1)

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
		where so.name = so_item.parent %s group by MONTH(so.transaction_date)""" % (condition)
	#frappe.throw(query)
	so_items = frappe.db.sql(query, as_dict=1)
	#frappe.throw(repr(so_items))
	return so_items


def get_columns(months,item_condition):
	items = get_item_info(item_condition)
	uom=''
	for item in items:
		uom=item.uom_name
	#frappe.throw(str(uom))
	columns = [_("Product ID") + "::100",_("Product Name") + "::200"]
	for mon in months:
		month_name=(datetime.strptime(mon.get('start'),'%Y-%m-%d').strftime('%B'))+' Sales Quantity ('+uom+')'
		columns.append(month_name + ":Float:150")
	columns+=[_("Total Sales Quantity") + ":Float:100",_("Total No of Months") + ":Int:100",_("Average Sales Quantity") + ":Float:100",_("Scrap Warehouse Quantity") + ":Float:100",_("Stock Balance (all local warehouse)") + ":Float:100",_("Warehouse-in Transit") + ":Float:100",_("Suggested Reorder Quantity") + ":Float:100"
		]
		
	return columns

def get_condition(filters):
	conditions = ""
	item_condition=""
	
	months=[]
	today=datetime.now().strftime("%Y-%m-%d")
	to_date=filters.get("to_date")
	if to_date>today:
		frappe.throw("To Date can not be greater than Current Date.")

	if filters.get("to_date") and filters.get("from_date"):
		# to_date=filters.get("to_date")[0:7] + "-01"
		# to_da=datetime.strptime(to_date,"%Y-%m-%d")
		# from_da= to_da - timedelta(6*365/12)
		
		# from_date=from_da.strftime('%Y-%m-%d')
		
		to_da=datetime.strptime(to_date,"%Y-%m-%d")
		from_date=filters.get("from_date")
		from_da= datetime.strptime(from_date,"%Y-%m-%d")
		if from_date>to_date:
			frappe.throw("To Date must be greater than From Date")
		#gen_conditions += " and so.transaction_date >= '%s' and so.transaction_date <= '%s'" % (from_date,to_date)
		#frappe.throw(conditions)
		
		while(from_da<to_da):
			start=from_da.strftime("%Y-%m-%d")
			flag=from_da.strftime('%m')
			while(from_da.strftime('%m')==flag):
				flag=from_da.strftime('%m')
				end=from_da.strftime("%Y-%m-%d")
				from_da+=timedelta(1)
			months.append({'start':start,'end':end})

	else:
		frappe.throw(_("From and To dates are required"))

	if filters.get("item"):
		item_condition += " item_code = '%s'" % filters["item"]

	if len(months)>6:
		frappe.throw("Difference between Date FROM and TO must not more than 6")

	return conditions,months,item_condition
