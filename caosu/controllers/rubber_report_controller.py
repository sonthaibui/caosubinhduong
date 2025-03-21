from odoo import http
from odoo.http import request

class RubberReportController(http.Controller):
    @http.route(['/rubber/report'], type='http', auth='user', website=True)
    def rubber_report(self, **kw):
        # Load available selections
        available_to = request.env['hr.department'].search([('name', 'ilike', 'TỔ')], order='name')
        available_lo = request.env['plantation'].fields_get(['lo'])['lo']['selection']
        
        # Retrieve wizard data
        wizard_data = {
            'nhom': kw.get('nhom', 'all'),
            'compare_field': kw.get('compare_field', 'cong'),
            'detail_field': kw.get('detail_field', 'none'),
            'sort_order': kw.get('sort_order', 'desc'),
            'to': kw.get('to') or (available_to[0].id if available_to else ''),
            'lo': kw.get('lo', 'a'),
            'dao_kt': kw.get('dao_kt', ''),
        }
        
        # Call _get_report_values on the Rubber Report template object
        report_obj = request.env['report.caosu.rubber_report_template']
        values = report_obj._get_report_values(docids=[], data=wizard_data)
        values.update({
            'available_to': available_to,
            'available_lo': available_lo,
            'selected_to': wizard_data.get('to') or '',
            'selected_lo': wizard_data.get('lo') or '',
        })
        return request.render('caosu.rubber_report_template', values)