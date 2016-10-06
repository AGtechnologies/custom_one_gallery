# Copyright (c) 2015, Frappe Technologies Pvt. Ltd. and Contributors and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _

from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
from frappe.utils import flt, getdate, today

def execute(filters=None):
	if not filters: filters = {}

	condition,months,item_condition,future_months=get_condition(filters)
	columns = get_columns(months,item_condition)
	items = get_item_info(item_condition)

	data = []
	for item in items:
		lmonths={0:0,1:0,2:0,3:0,4:0,5:0}
		fmonths={0:0,1:0,2:0}
		#frappe.throw(repr(months))
		if len(months)<6:
			lmonths={}
			mf=0
			for m in months:
				lmonths.update({mf:0})
				mf+=1

		so_months = 0
		scrap_quantity = 0
		warehouse_bal_quantity = 0
		future_1stmonth = 0
		reserved_quant = 0
		sales_qty_current = 0.0
		sales_qty_next = 0.0
		scrap_quantity=get_scrap_quantity(condition,item.item_name)
		st_items=get_stock_balance(condition,item.item_name)
		if st_items:
			st_items=st_items[0]
			warehouse_bal_quantity=st_items.actual_qty
			reserved_qty=st_items.reserved_qty
		#frappe.throw(repr(warehouse_bal_quantity)+repr(reserved_quant))
		datalist=[item.name, item.item_name,item.uom_name]
		for lmon in months:
			localcondition=condition + " and so.transaction_date >= '%s' and so.transaction_date <= '%s'" % (lmon.get('start',''),lmon.get('end',''))

			so_items_map=get_sales_items(localcondition,item.item_name)
			if so_items_map:
				so_items=so_items_map[0]
				lmonths.update({so_months:so_items.so_qty})
			so_months+=1
		#frappe.throw(str(lmonths))
		f=1
		checker=len(lmonths)-2
		for i in lmonths:
			iqty=lmonths.get(i,0)
			if checker:
				datalist.append(iqty)
			if f==checker:
				datalist.append(warehouse_bal_quantity)
			elif not checker:
				datalist.append(warehouse_bal_quantity)
				datalist.append(iqty)
				checker=True
			f+=1
			
		#datalist+=[warehouse_bal_quantity, sales_qty_current, sales_qty_next]
		#frappe.throw(repr(lmonths)+repr(datalist))
		po_months=0
		for fmon in future_months:
			localcondition=condition + " and po.transaction_date >= '%s' and po.transaction_date <= '%s'" % (fmon.get('start',''),fmon.get('end',''))

			po_items_map=get_purchase_items(localcondition,item.item_name)
			if po_items_map:
				po_items=po_items_map[0]
				fmonths.update({po_months:po_items.po_qty})
			po_months+=1
		#frappe.throw(str(po_items_map))
		f=1
		for i in fmonths:
			iqty=fmonths.get(i,0)
			datalist.append(iqty)
			if f==1:
				future_1stmonth=iqty
			f+=1
		#frappe.throw(repr(datalist))
		short_current = warehouse_bal_quantity - sales_qty_current
		short_next = (sales_qty_next + short_current) - (future_1stmonth + reserved_quant)
		datalist+=[short_current, short_next, scrap_quantity, reserved_quant]
		data.append(datalist)
	#frappe.throw(repr(data)+repr(columns))
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

def get_stock_balance(condition, item_name):
	condition=" and it.item_name ='%s'" %item_name
	query="""select bi.actual_qty, bi.reserved_qty
		from `tabBin` bi, `tabWarehouse` wh, `tabItem` it
		where wh.name = bi.warehouse and bi.item_code = it.name %s""" % (condition)
	sc_items = frappe.db.sql(query, as_dict=1)
	if not sc_items:
		return 0

	#frappe.throw(repr(sc_items))
	return sc_items

def get_sales_items(condition, item_name):
	condition+=" and so_item.item_name ='%s'" %item_name
	query="""select so_item.item_name, so.transaction_date, sum(so_item.qty) as so_qty
		from `tabSales Order` so, `tabSales Order Item` so_item
		where so.name = so_item.parent %s group by MONTH(so.transaction_date)""" % (condition)
	#frappe.throw(query)
	so_items = frappe.db.sql(query, as_dict=1)
	#frappe.throw(repr(so_items))
	return so_items

def get_purchase_items(condition, item_name):
	condition+=" and po_item.item_name ='%s'" %item_name
	query="""select po_item.item_name, po.transaction_date, sum(po_item.qty) as po_qty
		from `tabPurchase Order` po, `tabPurchase Order Item` po_item
		where po.name = po_item.parent %s group by MONTH(po.transaction_date)""" % (condition)
	#frappe.throw(query)
	po_items = frappe.db.sql(query, as_dict=1)
	#frappe.throw(repr(so_items))
	return po_items


def get_columns(months,item_condition):
	items = get_item_info(item_condition)
	columns = [_("Product ID") + "::100",_("Product Name") + "::200",_("UOM") + "::100"]
	#frappe.throw(repr(months))
	for mon in months[:-2]:
		start=datetime.strptime(mon.get('start'),'%Y-%m-%d')
		end=datetime.strptime(mon.get('end'),'%Y-%m-%d')
		
		month_name=start.strftime('%d')+'-'+end.strftime('%d')+' '+start.strftime('%b')+' Sales Qty'
		#frappe.throw(repr(month_name))
		columns.append(month_name + ":Float:150")
	columns+=[_("Stock Balance (all local W/Hse)") + ":Float:100",_("Sales Order Total qty (Current month)") + ":Float:100",_("Sales Order Total qty (Next month)") + ":Float:100",_("Future 1st Month PO Qty") + ":Float:100",_("Future 2nd Month PO Qty") + ":Float:100",_("Future 3rd Month PO Qty") + ":Float:100",_("Shortagefor *current month*") + ":Float:100",_("Shortage for *Next month*") + ":Float:100",_("Scrap W/Hse Qty") + ":Float:100",_("Reserved Qty") + ":Float:100"
		]
		
	return columns

def get_condition(filters):
	conditions = ""
	item_condition=""
	
	months=[]
	future_months=[]
	today=datetime.now().strftime("%Y-%m-%d")
	to_date=filters.get("to_date")
	if to_date>today:
		frappe.throw("To Date can not be greater than Current Date.")

	if filters.get("to_date") and filters.get("from_date"):
		to_da=datetime.strptime(to_date,"%Y-%m-%d")
		from_date=filters.get("from_date")
		from_da= datetime.strptime(from_date,"%Y-%m-%d")
		if from_date>to_date:
			frappe.throw("To Date must be greater than From Date")
		end=""
		start=""
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
		from_da=to_da
		to_da=to_da+relativedelta(months=3)
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
			future_months.append({'start':start,'end':end})
	else:
		frappe.throw(_("From and To dates are required"))

	if filters.get("item"):
		item_condition += " item_code = '%s'" % filters["item"]

	if len(months)>4:
		frappe.throw("Difference between Date FROM and TO must not more than 3.")

	# if len(future_months)>3:
	# 	frappe.throw("Difference between Date FROM and TO must not more than 3.")

	return conditions,months+future_months[:2],item_condition,future_months