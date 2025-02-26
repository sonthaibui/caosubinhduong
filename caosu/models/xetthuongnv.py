from odoo import api, models, fields, _
from odoo.exceptions import UserError

class RewardOffice(models.Model):
    _name = 'reward.office'
    _description = 'Reward Office Model'
    _rec_name = 'name'

    number = fields.Integer('STT')
    employee_id = fields.Many2one('hr.employee', string='Nhân Viên')
    positive = fields.Selection([
        ('1', 'Rất cao'), ('0', 'Bình thường'), ('-1', 'Chưa đạt')
    ], string='Tích Cực, siêng năng', default='1', required=True)
    proactive = fields.Selection([
        ('1', 'Rất cao'), ('0', 'Bình thường'), ('-1', 'Chưa đạt')
    ], string='Chủ động', default='1', required=True)
    error = fields.Selection([
        ('-2', 'Nghiêm trọng'), ('-1', 'Nhẹ'), ('0', 'Không')
    ], string='Sai sót', default='0', required=True)
    creative = fields.Selection([
        ('1', 'Có'), ('0', 'Không')
    ], string='Sáng tạo', default='1', required=True)
    hardwork = fields.Selection([
        ('1', 'Có'), ('0', 'Không')
    ], string='Độ khó công việc', default='1', required=True)
    point = fields.Integer('Điểm', compute='_compute_point')
    classification = fields.Char('Xếp loại')
    bonus = fields.Float('Thưởng')
    bonuscum = fields.Float('Tích lũy')
    rewardofficebymonth_id = fields.Many2one('reward.office.by.month', string='Xét Thưởng Tháng Nhân viên', ondelete='cascade')
    month = fields.Selection(related='rewardofficebymonth_id.month', string='month')
    year = fields.Selection(related='rewardofficebymonth_id.year', string='year')
    name = fields.Char('Name', compute='_compute_name')

    @api.depends('positive','proactive','error','creative','hardwork')
    def _compute_point(self):
        for rec in self:
            rec.point = int(rec.positive) + int (rec.proactive) + int(rec.error) + int(rec.creative) + int(rec.hardwork)
            if rec.point ==  4:
                rec.classification = 'Xuất sắc'
            elif rec.point ==  3:
                rec.classification = 'Giỏi'
            elif rec.point ==  2:
                rec.classification = 'Khá'
            elif rec.point <=  0:
                rec.classification = 'Trung bình'

    @api.depends('employee_id','month','year')
    def _compute_name(self):
        for rec in self:
            rec.name = rec.employee_id.name[0:-3] + '/' + rec.month + '/' + rec.year

class RewardOfficeByMonth(models.Model):
    _name = 'reward.office.by.month'
    _description = 'Reward Office By Month Model'
    _rec_name = 'name'

    month = fields.Selection([
        ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'),
        ('07', '7'), ('08', '8'), ('09', '9'), ('10', '10'), ('11', '11'), ('12', '12'),
    ], string='Tháng', required=True)
    year = fields.Selection([
        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
    ], string='Năm', default=str(fields.Datetime.now().year), required=True)
    note = fields.Char('Ghi chú')
    name = fields.Char('Name', compute='_compute_name')
    rewardoffice_ids = fields.One2many('reward.office', 'rewardofficebymonth_id', string='Xét Thưởng Nhân viên')

    @api.depends('month','year')
    def _compute_name(self):
        for rec in self:
            rec.name = 'NV' + rec.month + '/' + rec.year

    @api.onchange('month')
    def _onchange_month(self):
        rewardofficebymonth_counts = self.search_count([('month','=',self.month),('year','=',self.year)])
        if rewardofficebymonth_counts > 0:
            raise UserError(_("Xét thưởng nhân niên" + " tháng " + self.month + "/" + self.year + " đã có rồi."))