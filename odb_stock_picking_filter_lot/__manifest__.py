{
    "name": "Stock picking filter lot",
    "summary": "In picking out lots' selection, filter lots based on their location",
    "category": "Warehouse",
    "version": "1.0.1",
    "author": "DuyBQ",
    "license": "OPL-1",
    "application": False,
    "installable": True,
    "auto_install": False,
    "website": "https://www.odoobase.com/",
    "depends": [
        "stock",
        "odb_stock_auto_lot_sn",
    ],
    "data": [
        "views/stock_move_line_view.xml",
        "views/stock_picking_type_view.xml",
        "views/stock_scrap_view.xml",
    ],
}
