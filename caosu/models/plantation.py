from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class Plantation(models.Model):
    _name = 'plantation'
    _description = 'Plantation Model'
    _rec_name = "name"

    active = fields.Boolean('Active', default=True)
    can_duplicate = fields.Boolean('Can Duplicate', default=False)
    name = fields.Char('Mã')#, compute='_compute_ma_to')
    location_id = fields.Many2one('location', string='Khu vực', required=True)
    nongtruong = fields.Selection([('DHR', 'Đăk Hring'), ('DRE', 'Đăk Tờ Re'),('THTR', 'Thanh Trung'),('DTH', 'Triệu Hải'),('SS', 'Sa Sơn'),('IL', 'Ia Le')], string='Nông Trường', default='DHR')
    loso = fields.Char('Lô Số', default='1')
    sophan = fields.Char('Số Hàng', default='1')
    to = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True,
        default=lambda self: self.env['hr.department'].search([('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], limit=1))
    toname = fields.Char('Tổ Name', compute='_compute_ma_to')
    to_name = fields.Char('Tổ', related='to.name', store=True)
    lo = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C')], string='Lô', default='a', required=True, store=True)
    sttcn = fields.Selection([
        ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'), ('07', '7'), ('08', '8'), ('09', '9'), ('10', '10'),
        ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'),
        ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'), ('31', '31'),
    ], string='STT CN', default='01', required=True)
    employee_id = fields.Many2one('hr.employee', string='Công nhân', required=True)
    hangso = fields.Char('Hàng số')
    caycao = fields.Integer('Cây cạo')
    cayk = fields.Integer('Cây K')
    cayd6 = fields.Integer('Cây D<60')
    cayd68 = fields.Integer('Cây D60-80')
    cayd810 = fields.Integer('Cây D80-100')
    cayd10 = fields.Integer('Cây D>100')
    giong1 = fields.Char('Giống1', default='GT1')
    tyle1 = fields.Char('%G1', default='0%')
    giong2 = fields.Char('Giống2', default='PB235')
    tyle2 = fields.Char('%G2', default='0%')
    giong3 = fields.Char('Giống2')
    tyle3 = fields.Char('%G3')
    namtrong = fields.Char('Năm Trồng', default='2000')
    nammomieng = fields.Char('Năm Mở Miệng', default='2000')
    namcaoup = fields.Char('Năm Cạo Úp', default='2000')
    rubber_line_ids = fields.One2many('rubber', 'plantation_id', string='Sản lượng mũ')
    treeline_line_ids = fields.One2many('tree.line', 'plantation_id', string='Hàng Cây')
    ghi_chu = fields.Text('Ghi Chú')
    note = fields.Html('Note')
    nhom = fields.Char('Nhóm')

    """ @api.constrains('nongtruong','lo','to','sttcn')
    def _check_plantation_unique(self):
        plantation_counts = self.search_count([('nongtruong','=', self.nongtruong),('id','!=',self.id),
            ('lo','=',self.lo),('to','=',self.to.id),('sttcn','=',self.sttcn)])
        if plantation_counts > 0:
            raise ValidationError("Plantation already exists!")
        
    @api.constrains('nongtruong','lo','to','sttcn','employee_id')
    def _check_plantation_worker_unique(self):
        plantation_counts = self.search_count([('nongtruong','=', self.nongtruong),('lo','=',self.lo),('id','!=',self.id),
            ('to','=',self.to.id),('sttcn','!=',self.sttcn),('employee_id','=',self.employee_id.id)])
        if plantation_counts > 0:
            raise ValidationError("Plantation with worker already exists!")
    
    @api.depends('nongtruong','to','lo','sttcn')
    def _compute_ma_to(self):
        for rec in self:
            ref = 'To' + rec.to.name[3:]
            rec.name = rec.nongtruong + '-' + ref + '-' + rec.lo.upper() + rec.sttcn
            rec.toname = '-' + rec.to.name[3:] """
    
    @api.constrains('nongtruong','lo','to','sttcn','employee_id')
    def _check_plantation_worker_unique(self):
        if self.can_duplicate == False:
            plantation_counts = self.search_count([('nongtruong','=', self.nongtruong),('lo','=',self.lo),('id','!=',self.id),
                ('to','=',self.to.id),('sttcn','=',self.sttcn),('employee_id','=',self.employee_id.id)])
            if plantation_counts > 0:
                raise ValidationError("Plantation with worker already exists!")
    
    @api.depends('nongtruong','to','lo','sttcn')
    def _compute_ma_to(self):
        for rec in self:
            ref = 'To' + rec.to.name[3:]
            rec.name = rec.nongtruong + '-' + ref + '-' + rec.lo.upper() + rec.sttcn
            rec.toname = '-' + rec.to.name[3:]

    def copy(self):
        if self.can_duplicate == True:
            return super(Plantation, self).copy()
        elif self.can_duplicate == False:
            raise ValidationError("Plantation with worker already exists!")

class location(models.Model):
    _name = 'location'
    _description = 'Khu vực'

    code = fields.Char(string='Mã')
    name = fields.Char(string='Tên')