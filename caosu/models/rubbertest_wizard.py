from odoo import api, fields, models, _

class RubberTestReportWizard(models.TransientModel):
    _name = 'rubbertest.report.wizard'
    _description = 'Rubber Test Report Wizard'

    # Selection of group (nhóm) – adjust options to match your plantation.test.nhom values
    nhom = fields.Selection([
        ('blue', 'Blue'),
        ('red', 'Red'),
        ('brown', 'Brown'),
    ], string="Nhóm", required=True, default='blue')

    compare_field = fields.Selection([
        ('mu_up', 'Mũ Cạo Up'),
        ('do_up', 'Đỏ Cạo Up'),
        ('mu_ngua', 'Mũ Ngửa'),
        ('do_ngua', 'Đỏ Ngửa'),
    ], string="Compare Field", required=True, default='mu_up')

    def action_print_report(self):
        """Return the report action, passing wizard data in context."""
        data = {
            'nhom': self.nhom,
            'compare_field': self.compare_field,
        }
        return self.env.ref('caosu.action_report_rubbertest').report_action(self, data=data)

    def print_report(self):
        wizard_data = {
            'nhom': self.nhom,
            'lo': self.lo,
            'compare_field': self.compare_field,
            'detail_field': self.detail_field,
            'sort_order': self.sort_order,
            'dao_kt_up': self.dao_kt_up,
        }
        # This will call the report action and render the report as HTML.
        return self.env.ref('caosu.action_report_rubbertest').report_action(self, data=wizard_data)