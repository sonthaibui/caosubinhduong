{
    "name": "Stock Move Quick Lot",
    "summary": "Set lot name and end date directly on picking operations",
    "category": "Warehouse",
    "version": "1.0.1",
    "author": "DuyBQ",
    "license": "OPL-1",
    "application": False,
    "installable": True,
    "auto_install": False,
    "website": "https://www.odoobase.com/",
    "depends": [
        "product_expiry",
        "odb_stock_auto_lot_sn",
    ],
    "data": [
        "views/stock_view.xml"
    ],
}
