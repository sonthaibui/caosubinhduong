from odoo import api, fields, models, _

class EmployeeBenefit(models.Model):
    _name = "employee.benefit"
    _description = "Employee Benefit Model"

    department_id = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True, readonly=True)
    name = fields.Char('Name', related='department_id.name')
    nam = fields.Selection([
        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
    ], string='Năm', default=str(fields.Datetime.now().year), required=True)
    allowance_line_ids = fields.One2many('allowance', 'employeebenefit_id', string='Phụ cấp', domain=[('byyear', '=', True)])

    @api.onchange('nam')
    def _onchange_nam(self):
        if self.nam:
            als = self.env['allowance'].search([('employee_id.department_id','=',self.department_id.id)])
            thang = als[0].thang
            for al in als:
                if al.nam == self.nam and al.thang == thang:
                    al.byyear = True
                else:
                    al.byyear = False
