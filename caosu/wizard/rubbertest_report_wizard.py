from odoo import api, fields, models

class RubberTestReportWizard(models.TransientModel):
    _name = 'rubbertest.report.wizard'
    _description = 'Wizard for Rubber Test Report'

    nhom = fields.Selection([('all', 'All'), ('grp1', 'Group 1')], string="Nhóm", default='all')
    to = fields.Many2one('hr.department', string="Tổ")
    lo = fields.Selection([], string="Lô", default='a')
    compare_field = fields.Selection([
        ('mu_up', 'Mũ Cạo Up'),
        ('do_up', 'Đỏ Cạo Up'),
        ('mu_ngua', 'Mũ Ngửa'),
        ('do_ngua', 'Đỏ Ngửa')
    ], string="Primary Field", default='mu_up')
    detail_field = fields.Selection([
        ('none', 'None'),
        ('kichthich', 'Kích Thích'),
        ('mu_ngua', 'Mũ Ngửa'),
        ('do_up', 'Đỏ Cạo Up')
    ], string="Detail Field", default='none')
    sort_order = fields.Selection([('asc', 'Ascending'), ('desc', 'Descending')], string="Sort Order", default='desc')
    dao_kt_up = fields.Char(string="Dao KT", default='')

    @api.onchange('to')
    def _onchange_to(self):
        # Optionally, update the available options for 'lo' based on selected "to".
        if self.to:
            # Replace with your actual logic if needed.
            self.lo = 'a'
        else:
            self.lo = 'a'

    def print_report(self):
        wizard_data = {
            'nhom': self.nhom,
            'to': self.to.id if self.to else '',
            'lo': self.lo,
            'compare_field': self.compare_field,
            'detail_field': self.detail_field,
            'sort_order': self.sort_order,
            'dao_kt_up': self.dao_kt_up,
        }
        # Call the report action (ensure the external ID matches your report action).
        return self.env.ref('caosu.action_report_rubbertest').report_action(self, data=wizard_data)