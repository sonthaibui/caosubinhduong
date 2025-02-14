from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class PlantationTest(models.Model):
    _name = 'plantation.test'
    _description = 'Plantation Test Model'
    _rec_name = "name"

    active = fields.Boolean('Active', default=True)
    name = fields.Char('Mã')#, compute='_compute_ma_to')
    nongtruong = fields.Selection([('DHR', 'Đăk Hring'), ('DRE', 'Đăk Tờ Re'),('THTR', 'Thanh Trung'),('DTH', 'Triệu Hải'),('SS', 'Sa Sơn'),('IL', 'Ia Le')], string='Nông Trường', default='DHR', required=True)
    loso = fields.Char('Lô Số', default='1')
    sophan = fields.Char('Số Hàng', default='1')
    to = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True,
        default=lambda self: self.env['hr.department'].search([('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], limit=1))
    to_name = fields.Char('Tổ', related='to.name')
    toname = fields.Char('Tổ Name', compute='_compute_ma_to')
    lo = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C')], string='Lô', default='a', required=True)
    sttcn = fields.Selection([
        ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'), ('07', '7'), ('08', '8'), ('09', '9'), ('10', '10'),
        ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'),
        ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'),
    ], string='STT CN', default='01', required=True)
    employee_id = fields.Many2one('hr.employee', string='Công nhân', required=True)
    hangso = fields.Char('Hàng số')    
    giong = fields.Char('Giống', default='GT1')
    tyle = fields.Char('% Giống', default='80%')    
    namtrong = fields.Char('Năm Trồng', default='1994')
    nammomieng = fields.Char('Năm Mở Miệng', default='2000')
    namcaoup = fields.Char('Năm Cạo Úp', default='2015')
    rubbertest_line_ids = fields.One2many('rubber.test', 'plantationtest_id', string='Sản lượng mũ cạo thí nghiệm')

    @api.constrains('nongtruong','lo','to','sttcn')
    def _check_plantationtest_unique(self):
        plantationtest_counts = self.search_count([('nongtruong','=', self.nongtruong),('id','!=',self.id),
            ('lo','=',self.lo),('to','=',self.to.id),('sttcn','=',self.sttcn)])
        if plantationtest_counts > 0:
            raise ValidationError("Plantation Test already exists!")       
    
    
    @api.depends('nongtruong','to','lo','sttcn')
    def _compute_ma_to(self):
        for rec in self:
            ref = 'To' + rec.to.name[3:]
            rec.name = rec.nongtruong + '-' + ref + '-' + rec.lo.upper() + rec.sttcn
            rec.toname = '-' + rec.to.name[3:]
