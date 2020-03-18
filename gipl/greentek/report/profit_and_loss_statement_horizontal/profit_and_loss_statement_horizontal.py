# Copyright (c) 2013, Officexlr Business Solutions Pvt. Ltd. and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import flt
from erpnext.accounts.report.financial_statements import (get_period_list, get_columns, get_data)

def execute(filters=None):
	period_list = get_period_list(filters.from_fiscal_year, filters.to_fiscal_year,
		filters.periodicity, filters.accumulated_values, filters.company)

	income = get_data(filters.company, "Income", "Credit", period_list, filters = filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)
	inc=[]
	for d in income:
		dict_list={}
		for key, value in d.items() :
			if key !='indent':
				key='in_'+key
			dict_list.update({key:value})
		inc.append(dict_list)	
	income=inc
	expense = get_data(filters.company, "Expense", "Debit", period_list, filters=filters,
		accumulated_values=filters.accumulated_values,
		ignore_closing_entries=True, ignore_accumulated_values_for_fy= True)
	exp=[]
	for d in expense:
		dict_list={}
		for key, value in d.items() :
			if key !='indent':
				key='ex_'+key
			dict_list.update({key:value})
		exp.append(dict_list)	
	expense=exp
	data = []
	a=income
	b=expense
	if len(income)<len(expense):
		b=income
		a=expense
	for i in range(len(a)):
		if i < len(b):
			a[i].update(b[i])
	data=a
	columns = get_columns(filters.periodicity, period_list, filters.accumulated_values, filters.company)
	col=[]
	for d in columns:
		dict_list={}
		for key, value in d.items() :
			if key in ['fieldname']:
				value='in_'+value
			dict_list.update({key:value})
		col.append(dict_list)
	for d in columns:
		dict_list={}
		for key, value in d.items() :
			if key in ['fieldname']:
				value='ex_'+value
			dict_list.update({key:value})
		col.append(dict_list)
	columns=col
	get_net_profit_loss(income, expense,data, period_list, filters.company, filters.presentation_currency)

	return columns, data

def get_net_profit_loss(income, expense,data, period_list, company, currency=None, consolidated=False):
	net_profit1={}
	net_profit2={}
	for period in period_list:
		key = period if consolidated else period.key
		total_income = flt(income[0]['in_'+key], 3) if income else 0
		total_expense = flt(expense[0]['ex_'+key], 3) if expense else 0
		net_profit_loss= total_income - total_expense
		net_profit1.update({'ex_account':"Total Income (Credit)",'ex_'+key:total_income})
		net_profit2.update({'ex_account':"Profit for the year",'ex_'+key:net_profit_loss})
	data.append(net_profit1)
	data.append(net_profit2)
