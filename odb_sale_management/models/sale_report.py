from odoo import api, fields, models


class SaleReport(models.Model):
    _inherit = 'sale.report'

    value_delivered = fields.Float('Values Delivered', readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['value_delivered'] = ", CASE WHEN l.product_id IS NOT NULL THEN SUM((l.qty_delivered * l.price_unit) / u.factor * u2.factor) ELSE 0 END as value_delivered"
        # groupby += ', s.website_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)