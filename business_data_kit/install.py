import frappe
from frappe.utils import add_days, add_years, getdate, today

from business_data_kit import demo_data

SAVEPOINT = "business_data_kit_demo_data"


def after_install():
	create_demo_data()


def create_demo_data():
	"""Create a demo hardware trading company with items, pricing,
	sales/purchase invoices and stock movements. Safe to re-run: it
	skips everything if the demo company already exists."""
	if frappe.db.exists("Company", {"company_name": demo_data.COMPANY["company_name"]}):
		return

	frappe.db.savepoint(SAVEPOINT)
	try:
		frappe.flags.in_import = True
		company = create_company()
		create_fiscal_year()
		create_uoms()
		create_item_groups()
		create_items()
		create_parties()
		create_purchase_invoices(company)
		create_sales_invoices(company)
		create_stock_entries(company)
		frappe.db.commit()
	except Exception:
		# A nested insert (e.g. chart of accounts import during company
		# creation) may have already issued its own commit, in which case
		# our savepoint no longer exists and rolling back to it would
		# itself raise. Fall back to a plain rollback in that case.
		try:
			frappe.db.rollback(save_point=SAVEPOINT)
		except Exception:
			frappe.db.rollback()
		frappe.log_error(title="Business Data Kit: demo data generation failed")
		print("Business Data Kit: demo data generation failed, see Error Log for details")
	finally:
		frappe.flags.in_import = False


def _ensure_tree_node(doctype, name_field, parent_field, root_name, leaf_name=None, leaf_is_group=0):
	"""Ensure a root node (and optionally a leaf under it) exists for a
	tree doctype (Item Group, Territory, Customer Group, Supplier Group).
	Self-contained instead of depending on erpnext's Setup Wizard having
	run, since bench install-app erpnext does not run it, and a site that
	did run it may have used a different country/leaf than ours."""
	if not frappe.db.exists(doctype, root_name):
		frappe.get_doc(
			{"doctype": doctype, name_field: root_name, parent_field: "", "is_group": 1}
		).insert()

	if leaf_name and not frappe.db.exists(doctype, leaf_name):
		frappe.get_doc(
			{
				"doctype": doctype,
				name_field: leaf_name,
				parent_field: root_name,
				"is_group": leaf_is_group,
			}
		).insert()


def create_company():
	# bench install-app erpnext does not run the Setup Wizard, so the
	# baseline fixtures it normally creates (root Item/Customer/Supplier
	# Groups, Territories, default Price Lists, UOMs, etc.) may not exist.
	# Ensure exactly what we need ourselves rather than depending on
	# erpnext's install_fixtures(), which assumes a from-scratch site.
	_ensure_tree_node("Item Group", "item_group_name", "parent_item_group", "All Item Groups")
	_ensure_tree_node(
		"Territory", "territory_name", "parent_territory", "All Territories", demo_data.COMPANY["country"]
	)
	_ensure_tree_node(
		"Customer Group", "customer_group_name", "parent_customer_group", "All Customer Groups", "Commercial"
	)
	_ensure_tree_node(
		"Supplier Group", "supplier_group_name", "parent_supplier_group", "All Supplier Groups", "Hardware"
	)

	for price_list, buying, selling in (
		("Standard Buying", 1, 0),
		("Standard Selling", 0, 1),
	):
		if not frappe.db.exists("Price List", price_list):
			frappe.get_doc(
				{
					"doctype": "Price List",
					"price_list_name": price_list,
					"enabled": 1,
					"buying": buying,
					"selling": selling,
					"currency": demo_data.COMPANY["default_currency"],
				}
			).insert()

	# ERPNext's Company.create_default_warehouses() hardcodes a "Transit"
	# Warehouse Type but some ERPNext versions don't ship that master
	# record, so creating a brand new company fails. Ensure it exists.
	if not frappe.db.exists("Warehouse Type", "Transit"):
		frappe.get_doc({"doctype": "Warehouse Type", "name": "Transit"}).insert()

	company = frappe.get_doc(
		{
			"doctype": "Company",
			"company_name": demo_data.COMPANY["company_name"],
			"abbr": demo_data.COMPANY["abbr"],
			"default_currency": demo_data.COMPANY["default_currency"],
			"country": demo_data.COMPANY["country"],
			"create_chart_of_accounts_based_on": demo_data.COMPANY["create_chart_of_accounts_based_on"],
			"chart_of_accounts": demo_data.COMPANY["chart_of_accounts"],
			"valuation_method": demo_data.COMPANY["valuation_method"],
		}
	)
	company.insert()

	# The Singapore CoA template's income ledger is named "Sales Income"
	# rather than "Sales"/"Sales Account", so ERPNext's auto-detection in
	# Company.set_default_accounts() doesn't find it and leaves
	# default_income_account empty, which then fails Sales Invoice
	# validation. Set it explicitly.
	if not company.default_income_account:
		company.db_set("default_income_account", _account("Sales Income"))

	return company.name


def create_fiscal_year():
	max_days_ago = max(
		row[0] for row in (*demo_data.PURCHASE_INVOICES, *demo_data.SALES_INVOICES)
	)
	max_days_ago = max(max_days_ago, *(e["days_ago"] for e in demo_data.STOCK_ENTRIES))

	start = add_days(today(), -(max_days_ago + 5))
	end = add_years(start, 1)
	end = add_days(end, -1)

	if frappe.db.exists("Fiscal Year", {"year_start_date": ["<=", start], "year_end_date": [">=", today()]}):
		return

	start_year, end_year = getdate(start).year, getdate(end).year
	year_name = str(start_year) if start_year == end_year else f"{start_year}-{end_year}"
	frappe.get_doc(
		{
			"doctype": "Fiscal Year",
			"year": year_name,
			"year_start_date": start,
			"year_end_date": end,
		}
	).insert()


def create_uoms():
	for uom in demo_data.UOMS:
		if not frappe.db.exists("UOM", uom):
			frappe.get_doc({"doctype": "UOM", "uom_name": uom}).insert()


def create_item_groups():
	if not frappe.db.exists("Item Group", demo_data.PARENT_ITEM_GROUP):
		frappe.get_doc(
			{
				"doctype": "Item Group",
				"item_group_name": demo_data.PARENT_ITEM_GROUP,
				"parent_item_group": "All Item Groups",
				"is_group": 1,
			}
		).insert()

	for group in demo_data.ITEM_GROUPS:
		if not frappe.db.exists("Item Group", group):
			frappe.get_doc(
				{
					"doctype": "Item Group",
					"item_group_name": group,
					"parent_item_group": demo_data.PARENT_ITEM_GROUP,
					"is_group": 0,
				}
			).insert()


def create_items():
	for item_code, item_name, item_group, uom, buying_rate, selling_rate in demo_data.ITEMS:
		if frappe.db.exists("Item", item_code):
			continue

		frappe.get_doc(
			{
				"doctype": "Item",
				"item_code": item_code,
				"item_name": item_name,
				"item_group": item_group,
				"stock_uom": uom,
				"is_stock_item": 1,
			}
		).insert()

		frappe.get_doc(
			{
				"doctype": "Item Price",
				"item_code": item_code,
				"price_list": "Standard Buying",
				"buying": 1,
				"price_list_rate": buying_rate,
			}
		).insert()
		frappe.get_doc(
			{
				"doctype": "Item Price",
				"item_code": item_code,
				"price_list": "Standard Selling",
				"selling": 1,
				"price_list_rate": selling_rate,
			}
		).insert()


def create_parties():
	for supplier_name in demo_data.SUPPLIERS:
		if not frappe.db.exists("Supplier", supplier_name):
			frappe.get_doc(
				{
					"doctype": "Supplier",
					"supplier_name": supplier_name,
					"supplier_group": "Hardware",
					"supplier_type": "Company",
					"country": demo_data.COMPANY["country"],
				}
			).insert()

	for customer_name in demo_data.CUSTOMERS:
		if not frappe.db.exists("Customer", customer_name):
			frappe.get_doc(
				{
					"doctype": "Customer",
					"customer_name": customer_name,
					"customer_group": "Commercial",
					"customer_type": "Company",
					"territory": demo_data.COMPANY["country"],
				}
			).insert()


def _item_lookup():
	return {row[0]: {"rate_buy": row[4], "rate_sell": row[5]} for row in demo_data.ITEMS}


def _warehouse(name):
	return f"{name} - {demo_data.COMPANY['abbr']}"


def _account(name):
	return f"{name} - {demo_data.COMPANY['abbr']}"


def create_purchase_invoices(company):
	items_by_code = _item_lookup()
	for days_ago, supplier, lines in demo_data.PURCHASE_INVOICES:
		posting_date = add_days(today(), -days_ago)
		pi = frappe.get_doc(
			{
				"doctype": "Purchase Invoice",
				"company": company,
				"supplier": supplier,
				"posting_date": posting_date,
				"set_posting_time": 1,
				"update_stock": 1,
				"items": [
					{
						"item_code": item_code,
						"qty": qty,
						"rate": items_by_code[item_code]["rate_buy"],
						"warehouse": _warehouse("Stores"),
					}
					for item_code, qty in lines
				],
			}
		)
		pi.insert()
		pi.submit()


def create_sales_invoices(company):
	items_by_code = _item_lookup()
	for days_ago, customer, lines in demo_data.SALES_INVOICES:
		posting_date = add_days(today(), -days_ago)
		si = frappe.get_doc(
			{
				"doctype": "Sales Invoice",
				"company": company,
				"customer": customer,
				"posting_date": posting_date,
				"set_posting_time": 1,
				"update_stock": 1,
				"items": [
					{
						"item_code": item_code,
						"qty": qty,
						"rate": items_by_code[item_code]["rate_sell"],
						"warehouse": _warehouse("Stores"),
					}
					for item_code, qty in lines
				],
			}
		)
		si.insert()
		si.submit()


def create_stock_entries(company):
	items_by_code = _item_lookup()
	for entry in demo_data.STOCK_ENTRIES:
		posting_date = add_days(today(), -entry["days_ago"])
		se = frappe.get_doc(
			{
				"doctype": "Stock Entry",
				"company": company,
				"stock_entry_type": entry["purpose"],
				"purpose": entry["purpose"],
				"posting_date": posting_date,
				"set_posting_time": 1,
				"remarks": entry["remark"],
				"items": [
					{
						"item_code": item_code,
						"qty": qty,
						"s_warehouse": _warehouse(entry["source_warehouse"])
						if entry.get("source_warehouse")
						else None,
						"t_warehouse": _warehouse(entry["target_warehouse"])
						if entry.get("target_warehouse")
						else None,
						"basic_rate": items_by_code[item_code]["rate_buy"]
						if entry["purpose"] == "Material Receipt"
						else None,
					}
					for item_code, qty in entry["items"]
				],
			}
		)
		se.insert()
		se.submit()
