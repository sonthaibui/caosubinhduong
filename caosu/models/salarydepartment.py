from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class SalaryOfficeDepartment(models.Model):
    _name = "salary.office.department"
    _description = "Salary Office Department Model"
    _rec_name = "recname"

    to = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True)
    toname = fields.Char('Tổ', related='to.name')
    thang = fields.Selection([
        ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'),
        ('07', '7'), ('08', '8'), ('09', '9'), ('10', '10'), ('11', '11'), ('12', '12'),
    ], string='Tháng', required=True, default=str(fields.Datetime.now().strftime('%m')))
    nam = fields.Selection([
        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
    ], string='Năm', default=str(fields.Datetime.now().year), required=True)
    recorded = fields.Boolean('recorded', default=False, compute='_compute_recorded')
    recname = fields.Char('recname', compute='_compute_recname')
    company_id = fields.Many2one('res.company', store=True, copy=False,
        string="Company", default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
        related='company_id.currency_id')
    tongcong1 = fields.Char('Tổng cộng', default='Tổng Cộng')
    tongcong = fields.Float('tongcong', compute='_compute_tongcong')
    nhanthuc = fields.Float('nhanthuc', compute='_compute_tongcong')
    dep_hf = fields.Boolean(default=False)
    trachnhiem_hf = fields.Boolean(default=False)
    dixa_hf = fields.Boolean(default=False)
    tienmuon_hf = fields.Boolean(default=False)
    caotn_hf = fields.Boolean(default=False)
    laimc_hf = fields.Boolean(default=False)
    chiendo_hf = fields.Boolean(default=False)
    ngaytet_hf = fields.Boolean(default=False)
    thuongtet_hf = fields.Boolean(default=False)
    kyten_hf = fields.Boolean(default=False)
    ghichu_hf = fields.Boolean(default=False)
    salaryofficestaff_line_ids = fields.One2many('salary.office.staff', 'salaryofficedepartment_id', string='Lương bảo vệ')

    def _compute_recorded(self):
        for rec in self:
            if len(rec.salaryofficestaff_line_ids) > 0:
                rec.recorded = True
            elif str(rec.id).replace('NewId_', '')[0:2] != "0x":
                rec.recorded = True
                sos = self.env['salary.office.staff'].search([('salaryofficedepartment_id.id','=',rec.id)])
                if len(sos) == 0:
                    emps = self.env['hr.employee'].search([('name', 'like', '-bv'),('department_id','=',rec.to.id)])
                    if len(emps) == 0:
                        raise UserError(rec.to.name + ' không có bảo vệ.')
                    stt = 0
                    for emp in emps:
                        stt += 1
                        stt_text = ''
                        if stt < 10:
                            stt_text = '0' + str(stt)
                        else:
                            stt_text = str(stt)
                        self.env['salary.office.staff'].create({'to': rec.to.id, 'salaryofficedepartment_id': rec.id, 'stt': stt_text, 'employee_id': emp.id, 'phucloi': float(emp.diachi), 'thang': rec.thang, 'nam': rec.nam})

    @api.constrains('thang','nam','to')
    def _check_salaryofficedepartment_unique(self):
        salaryofficedepartment_counts = self.search_count([('thang','=',self.thang),('nam','=',self.nam),('to','=',self.to.id),('id','!=',self.id)])
        if salaryofficedepartment_counts > 0:
            raise ValidationError("Bảng lương bảo vệ đã tồn tại!")

    """ @api.onchange('to')
    def _onchange_to(self):
        if self.to:
            salaryofficedepartment_counts = self.search_count([('thang','=',self.thang),('nam','=',self.nam),('to','=',self.to.id)])
            if salaryofficedepartment_counts > 0:
                raise UserError(_("Bảng Lương Văn Phòng đã tồn tại."))
            else:
                if len(self.salaryofficestaff_line_ids) > 0:
                    to = self.to
                    for line in self.salaryofficestaff_line_ids:
                        line.unlink()
                    self.thang = to
                if len(self.salaryofficestaff_line_ids) == 0:
                    emps = self.env['hr.employee'].search([('name', 'like', '-bv'),('department_id','=',self.to.id)])
                    if len(emps) == 0:
                        raise UserError(self.to.name + ' không có bảo vệ.')
                    stt = 0
                    for emp in emps:
                        stt += 1
                        stt_text = ''
                        if stt < 10:
                            stt_text = '0' + str(stt)
                        else:
                            stt_text = str(stt)
                        self.env['salary.office.staff'].create({'to': self.to.id, 'salaryofficedepartment_id': self.id, 'stt': stt_text, 'employee_id': emp.id, 'thang': self.thang, 'nam': self.nam}) """

    @api.depends('thang', 'nam', 'to')
    def _compute_recname(self):
        for rec in self:
            if rec.recorded == True:
                rec.recname = rec.to.name + '_' + rec.thang + '_' + rec.nam

    @api.depends('salaryofficestaff_line_ids')
    def _compute_tongcong(self):
        for rec in self:
            if rec.recorded == True:
                tongcong = 0
                nhanthuc = 0
                for line in rec.salaryofficestaff_line_ids:
                    tongcong += line.tongcong
                    nhanthuc += line.nhanthuc
                rec.tongcong = tongcong
                rec.nhanthuc = nhanthuc
