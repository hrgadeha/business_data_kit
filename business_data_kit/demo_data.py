# Demo dataset definitions for a hardware trading business.
# Kept separate from install.py so the data can be reviewed/tweaked
# without touching the creation logic.

COMPANY = {
	"company_name": "Bright Hardware Traders",
	"abbr": "BHT",
	"default_currency": "SGD",
	"country": "Singapore",
	"create_chart_of_accounts_based_on": "Standard Template",
	"chart_of_accounts": "Singapore - Chart of Accounts",
	"valuation_method": "Moving Average",
}

UOMS = ["Nos", "Meter", "Box", "Pair"]

PARENT_ITEM_GROUP = "Hardware"

ITEM_GROUPS = [
	"Hand Tools",
	"Power Tools",
	"Pipes & Fittings",
	"Fasteners",
	"Locks & Hardware",
]

# item_code, item_name, item_group, uom, buying_rate, selling_rate
ITEMS = [
	("HW-HAM-001", "Claw Hammer 450g", "Hand Tools", "Nos", 180, 260),
	("HW-SCR-002", "Screwdriver Set 6pc", "Hand Tools", "Nos", 220, 320),
	("HW-WRN-003", "Adjustable Wrench 10 inch", "Hand Tools", "Nos", 150, 220),
	("HW-PWR-004", "Pipe Wrench 14 inch", "Hand Tools", "Nos", 280, 400),
	("HW-TAP-005", "Measuring Tape 5m", "Hand Tools", "Nos", 90, 140),
	("HW-SAW-006", "Hacksaw Frame 12 inch", "Hand Tools", "Nos", 110, 170),
	("HW-BRS-007", "Industrial Paint Brush 3 inch", "Hand Tools", "Nos", 60, 95),
	("HW-DRL-008", "Electric Drill Machine 13mm", "Power Tools", "Nos", 1800, 2600),
	("HW-GRN-009", "Angle Grinder 4 inch", "Power Tools", "Nos", 1500, 2200),
	("HW-GIP-010", "GI Pipe 1/2 inch", "Pipes & Fittings", "Meter", 65, 95),
	("HW-PVC-011", "PVC Pipe 3/4 inch", "Pipes & Fittings", "Meter", 35, 55),
	("HW-BLT-012", "Hex Bolt M8x50 (Box of 100)", "Fasteners", "Box", 320, 480),
	("HW-NUT-013", "Hex Nut M8 (Box of 100)", "Fasteners", "Box", 180, 280),
	("HW-HNG-014", "Door Hinges 4 inch (Pair)", "Locks & Hardware", "Pair", 45, 75),
	("HW-LCK-015", "Cylindrical Door Lock", "Locks & Hardware", "Nos", 350, 550),
]

SUPPLIERS = [
	"Apex Tools & Hardware Pvt Ltd",
	"Steelcraft Hardware Suppliers",
]

CUSTOMERS = [
	"Shree Construction Co",
	"Metro Builders & Developers",
	"Om Hardware Retail Store",
]

# Each row: (days_ago, supplier, [(item_code, qty), ...])
PURCHASE_INVOICES = [
	(80, "Apex Tools & Hardware Pvt Ltd", [("HW-HAM-001", 30), ("HW-SCR-002", 25), ("HW-WRN-003", 25)]),
	(76, "Steelcraft Hardware Suppliers", [("HW-PWR-004", 18), ("HW-TAP-005", 40), ("HW-SAW-006", 22)]),
	(70, "Apex Tools & Hardware Pvt Ltd", [("HW-BRS-007", 30), ("HW-DRL-008", 8), ("HW-GRN-009", 7)]),
	(65, "Steelcraft Hardware Suppliers", [("HW-GIP-010", 180), ("HW-PVC-011", 150)]),
	(60, "Apex Tools & Hardware Pvt Ltd", [("HW-BLT-012", 22), ("HW-NUT-013", 22), ("HW-HNG-014", 36)]),
	(55, "Steelcraft Hardware Suppliers", [("HW-LCK-015", 15), ("HW-HAM-001", 30)]),
	(48, "Apex Tools & Hardware Pvt Ltd", [("HW-SCR-002", 25), ("HW-WRN-003", 20), ("HW-PWR-004", 12)]),
	(40, "Steelcraft Hardware Suppliers", [("HW-TAP-005", 30), ("HW-SAW-006", 18), ("HW-DRL-008", 7)]),
	(33, "Apex Tools & Hardware Pvt Ltd", [("HW-GIP-010", 120), ("HW-PVC-011", 100), ("HW-GRN-009", 5)]),
	(25, "Steelcraft Hardware Suppliers", [("HW-BLT-012", 18), ("HW-NUT-013", 18), ("HW-LCK-015", 10)]),
]

# Each row: (days_ago, customer, [(item_code, qty), ...])
SALES_INVOICES = [
	(58, "Shree Construction Co", [("HW-HAM-001", 10), ("HW-GIP-010", 60), ("HW-PVC-011", 40)]),
	(52, "Metro Builders & Developers", [("HW-SCR-002", 8), ("HW-WRN-003", 10), ("HW-PWR-004", 6)]),
	(46, "Om Hardware Retail Store", [("HW-TAP-005", 15), ("HW-SAW-006", 10), ("HW-BRS-007", 12)]),
	(39, "Shree Construction Co", [("HW-BLT-012", 10), ("HW-NUT-013", 10), ("HW-HNG-014", 14)]),
	(32, "Metro Builders & Developers", [("HW-DRL-008", 4), ("HW-GRN-009", 3), ("HW-LCK-015", 6)]),
	(27, "Om Hardware Retail Store", [("HW-HAM-001", 8), ("HW-SCR-002", 7), ("HW-WRN-003", 7)]),
	(21, "Shree Construction Co", [("HW-GIP-010", 70), ("HW-PVC-011", 55)]),
	(15, "Metro Builders & Developers", [("HW-PWR-004", 6), ("HW-SAW-006", 8), ("HW-BRS-007", 8)]),
	(9, "Om Hardware Retail Store", [("HW-BLT-012", 8), ("HW-NUT-013", 8), ("HW-LCK-015", 5)]),
	(4, "Shree Construction Co", [("HW-TAP-005", 10), ("HW-HNG-014", 12), ("HW-DRL-008", 3)]),
]

# Inventory movements independent of sales/purchase, each tagged with
# days_ago and a short remark describing the business reason.
STOCK_ENTRIES = [
	{
		"days_ago": 83,
		"purpose": "Material Receipt",
		"remark": "Opening stock of paint brushes carried over from previous ledger",
		"items": [("HW-BRS-007", 20)],
		"target_warehouse": "Stores",
	},
	{
		"days_ago": 18,
		"purpose": "Material Transfer",
		"remark": "Transferred power tools to Finished Goods store for showroom display",
		"items": [("HW-DRL-008", 2), ("HW-GRN-009", 2)],
		"source_warehouse": "Stores",
		"target_warehouse": "Finished Goods",
	},
	{
		"days_ago": 7,
		"purpose": "Material Issue",
		"remark": "Written off damaged measuring tapes found during stock check",
		"items": [("HW-TAP-005", 2)],
		"source_warehouse": "Stores",
	},
]
