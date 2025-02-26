from odoo import http

from odoo.http import request
class Main(http.Controller):
    @http.route('/caosu/nhanvien', type='http', auth='none')
    def nhanvien(self):
        nhanvien = request.env['hr.employee'].sudo().search([])
        html_result = '<html><body><ul>'
        for nv in nhanvien:
            html_result += "<li> %s </li>" % nv.name
        html_result += '</ul></body></html>'
        return html_result
    
    @http.route('/caosu/nhanvien', type='json', auth='none')
    def nhanvien_json(self):
        records = request.env['hr.employee'].sudo().search([])
        return records.read(['name'])