from odoo import http
from odoo.http import request

class RubberTestReportController(http.Controller):
    @http.route(['/rubbertest/report'], type='http', auth="user", website=True)
    def rubber_test_report(self, **kw):
        available_to = request.env['hr.department'].search([('name', 'ilike', 'TỔ')], order='name')
        available_lo = request.env['plantation.test'].fields_get(['lo'])['lo']['selection']

        wizard_data = {
            'nhom': kw.get('nhom', 'all'),
            'compare_field': kw.get('compare_field', 'mu_up'),
            'detail_field': kw.get('detail_field', 'none'),
            'sort_order': kw.get('sort_order', 'desc'),
            'to': kw.get('to', ''),
            'lo': kw.get('lo', 'a'),
            'dao_kt_up': kw.get('dao_kt_up', ''),
        }
        report_obj = request.env['report.caosu.rubbertest_report_template']
        values = report_obj._get_report_values(docids=[], data=wizard_data)
        values.update({
            'available_to': available_to,
            'available_lo': available_lo,
            'selected_to': wizard_data.get('to') or '',
            'selected_lo': wizard_data.get('lo') or '',
        })
        return request.render('caosu.rubbertest_report_template', values)

