# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from datetime import datetime,timedelta
from frappe.utils import flt, getdate, today

def execute(filters=None):
	if not filters: filters = {}

	condition,months,mycustomer=get_condition(filters)
	columns = get_columns(months)
	items = get_item_info()
	#frappe.throw(repr(items))
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
		tot_months = 0
		warehouse_bal_quantity = 0
		warehouse_name=''
		customer_name=''
		customer=''
		avg_sales_quantity=0.0
		#frappe.throw(repr(months))
		for mon in months:
			localcondition=condition + " and si.posting_date >= '%s' and si.posting_date <= '%s'" % (mon.get('start',''),mon.get('end',''))
			si_items_map=get_sales_items(localcondition,item.item_name)
			#frappe.throw(repr(si_items_map))
			if si_items_map:
				si_items=si_items_map[0]

				customer_name=mycustomer and si_items.customer_name or ''
				customer=mycustomer and si_items.customer_id or ''
				warehouse_name=si_items.warehouse_name
				warehouse_bal_quantity=si_items.actual_qty
				lmonths.update({no_months:si_items.so_qty})
				if si_items.so_qty:
					tot_months+=1
			no_months+=1
		total_sales_quantity = 0.0
		datalist=[customer,customer_name,warehouse_name, item.name, item.item_name,item.uom_name]
		for i in lmonths:
			iqty=lmonths.get(i,0)
			total_sales_quantity+=iqty
			datalist.append(str(iqty))
		#frappe.throw(repr(datalist))
		if tot_months:
			avg_sales_quantity = round((float(total_sales_quantity)/tot_months),2)
		replenish_quantity = round((avg_sales_quantity - warehouse_bal_quantity),2)
		datalist+=[avg_sales_quantity, warehouse_bal_quantity, replenish_quantity]
		data.append(datalist)
	
	return columns ,data

def get_item_info():
	
	return frappe.db.sql("select it.name, it.item_name, um.uom_name as uom_name from `tabItem` it, `tabUOM` um where it.stock_uom=um.name", as_dict=1)

def get_sales_items(condition, item_name):
	condition+=" and si_item.item_name ='%s'" %item_name
	query="""select cs.name as customer_id, si.customer_name, si_item.item_name, si.posting_date, sum(si_item.qty) as so_qty, wh.name as warehouse_name, si_item.actual_qty
		from `tabSales Invoice` si, `tabSales Invoice Item` si_item, `tabCustomer` cs, `tabWarehouse` wh
		where si.name = si_item.parent and si.customer=cs.name and si_item.warehouse=wh.name %s group by MONTH(si.posting_date)""" % (condition)
	#frappe.throw(query)
	si_items = frappe.db.sql(query, as_dict=1)
	#frappe.throw(repr(si_items))
	return si_items


def get_columns(months):
	
	columns = [_("Customer ID") + "::100",_("Customer Name") + "::150",_("Warehouse") + "::100",_("Product ID") + "::100",_("Product Name") + "::150",_("UOM") + "::100"]
	for mon in months:
		start=datetime.strptime(mon.get('start'),'%Y-%m-%d')
		end=datetime.strptime(mon.get('end'),'%Y-%m-%d')
		month_name=start.strftime('%d')+'-'+end.strftime('%d')+' '+start.strftime('%b')+' Sales Qty'
		columns.append(month_name + ":Float:150")

	columns+=[_("Average Sales Qty") + ":Float:100",_("Stock Balance at Customer W/Hse") + ":Float:100",_("Suggested Replenishment Qty") + ":Float:100"
		]
		
	return columns

def get_condition(filters):
	conditions = ""
	months=[]
	today=datetime.now().strftime("%Y-%m-%d")
	to_date=filters.get("to_date")
	mycustomer=False
	if to_date>today:
		frappe.throw("To Date can not be greater than Current Date.")

	if filters.get("to_date") and filters.get("from_date"):
		
		to_da=datetime.strptime(to_date,"%Y-%m-%d")
		from_date=filters.get("from_date")
		from_da= datetime.strptime(from_date,"%Y-%m-%d")
		if from_date>to_date:
			frappe.throw("To Date must be greater than From Date")
		end=""
		while(from_da<to_da):
			start=from_da.strftime("%Y-%m-%d")
			flag=from_da.strftime('%m')
			while(from_da.strftime('%m')==flag):
				flag=from_da.strftime('%m')
				end=from_da.strftime("%Y-%m-%d")
				if flag==to_da.strftime('%m'):
					end=to_da.strftime("%Y-%m-%d")
				from_da+=timedelta(1)
			months.append({'start':start,'end':end})
		#frappe.throw(repr(months))
	
	else:
		frappe.throw(_("From and To dates are required"))

	if filters.get("warehouse"):
		conditions += " and warehouse = '%s'" % filters["warehouse"]

	if filters.get("customer"):
		conditions += " and customer = '%s'" % filters["customer"]
		mycustomer=True

	if len(months)>6:
		frappe.throw("Difference between Date FROM and TO must not more than 6")

	return conditions,months,mycustomer
