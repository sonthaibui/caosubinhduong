from odoo import api, fields, models, _

class CTKT(models.Model):
    _name = 'ctkt'
    _description = 'Công thức kích thích'
    _rec_name = "name"

    name = fields.Char(string='Name', required=True, copy=False)
    congthuc = fields.Html(string='Công thức')

    def __init__(self, pool, cr):
        # Call the super method
        super(CTKT, self).__init__(pool, cr)
        # Check if the record with name 'Chưa bôi' exists
        cr.execute("SELECT id FROM ctkt WHERE name = 'Chưa bôi'")
        exists = cr.fetchone()
        if not exists:
            # Create the record if it does not exist: lam khac kieu rubbertree
            cr.execute("INSERT INTO ctkt (name, create_uid, create_date, write_uid, write_date) VALUES ('Chưa bôi', 1, NOW(), 1, NOW())")
