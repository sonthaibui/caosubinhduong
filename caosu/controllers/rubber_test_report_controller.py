from odoo import http

class RubberTestReportController(http.Controller):
    @http.route('/rubbertest/report', type='http', auth='user', website=True)
    def rubber_test_report(self, **kw):
        # The GET parameters (like lo, nhom, etc.) are available in kw.
        # You can now call http.request.render using your QWeb report template.
        return http.request.render("caosu.rubbertest_report_template", kw)