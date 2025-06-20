from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
#from .rubberprice import RubberPrice  # Import the RubberPrice class from the new file

class RubberHarvest(models.Model):
    _name = 'rubber.harvest'
    _description = 'Rubber Harvest Model'

    to = fields.Char('Tổ', readonly=True)
    daily = fields.Char('Đại lý', readonly=True)
    sanpham_id = fields.Many2one('sanpham', string='Sản phẩm')
    sanpham = fields.Selection([
        ('nuoc', 'Mũ nước'), ('tap', 'Mũ tạp'), ('day', 'Mũ dây'), ('dong', 'Mũ đông'), ('chen', 'Mũ chén')
    ], string='Sản phẩm', readonly=True)
    tyle = fields.Float('Tỷ lệ', readonly=True)
    soluong = fields.Float('Số lượng', digits='One Decimal', readonly=True)
    soluongban = fields.Float('Số lượng bán', digits='One Decimal', compute='_compute_soluongban')
    do = fields.Float('Độ bán', digits='One Decimal', readonly=True)
    quykho = fields.Float('Quy khô bán', digits='One Decimal', readonly=True, compute='_compute_quykho')
    rubbersell_id = fields.Many2one('rubber.sell', ondelete='cascade')
    rubberdeliver_id = fields.Many2one('rubber.deliver', ondelete='cascade')
    company_truck_id = fields.Many2one('company.truck', ondelete='cascade')
    
    @api.depends('soluongban', 'do')
    def _compute_quykho(self):
        for rec in self:
            rec.quykho = 0
            rec.quykho = rec.soluongban * rec.do / 100
    
    @api.depends('soluong', 'tyle')
    def _compute_soluongban(self):
        for rec in self:
            rec.soluongban = 0
            rec.soluongban = rec.tyle * rec.soluong

class RubberDeliver(models.Model):
    _name = 'rubber.deliver'
    _description = 'Rubber Deliver Model'

    ngay = fields.Date('Ngày giao', related='rubberbydate_id.ngay')
    ngay_giao = fields.Date(
        string='Ngày giao',
        compute='_compute_ngay_giao',
        store=True
    )
    @api.depends('ngay')
    def _compute_ngay_giao(self):
        for rec in self:
            rec.ngay_giao = rec.ngay
    to = fields.Char('Tổ', related='rubberbydate_id.to.name')
    daily = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer','=',True)], required=True,
                default=lambda self: self.env['res.partner'].search([('is_customer','=',True),('name','=','Xe tải nhà')], limit=1))
    daily_name = fields.Char('Tên đại lý', related='daily.name')
    sanpham_id = fields.Many2one('sanpham', string='Sản phẩm')
    sanpham = fields.Selection([
        ('nuoc', 'Mũ nước'), ('tap', 'Mũ tạp'), ('day', 'Mũ dây'), ('dong', 'Mũ đông'), ('chen', 'Mũ chén')
    ], string='Sản phẩm', required=True, default='nuoc')
    soluong = fields.Float('Số lượng', default='0', digits='One Decimal')
    do = fields.Float('Độ', default='0', digits='One Decimal')
    quykho = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_quykho')
    soluongtt = fields.Float('SL thực tế', default='0', digits='One Decimal')
    dott = fields.Float('Độ thực tế', default='0', digits='One Decimal')
    quykhott = fields.Float('QK thực tế', default='0', digits='One Decimal', compute='_compute_quykhott')
    state = fields.Selection([
        ('luu','Chưa lưu'),('chua', 'Chưa giao'), ('giao', 'Đã giao'), ('mua', 'Mua mũ'), ('nhan', 'Đã nhận'),], string='Trạng thái',
        copy=False, default='luu', index=True, readonly=True,
        help="Trạng thái của mũ.")
    rubberbydate_id = fields.Many2one('rubber.date', string='Nhập sản lượng', ondelete='cascade')
    company_truck_id = fields.Many2one('company.truck', string='Xe công ty', ondelete='set null')
    tyle = fields.Float(compute='_compute_tyle', string='Tỷ lệ (%)')

    #Nếu mũ giao từ tổ thì trạng thái là chưa mua , ngược lại trạng thái là mua
    @api.model
    def create(self, vals):
        res = super(RubberDeliver, self).create(vals)
        if res.to != 'TỔ Xe tải':
            res.state = 'chua'
        else:
            res.state = 'mua'
        return res
    
    @api.depends('quykhott')
    def _compute_tyle(self):
        for rec in self:
            rec.tyle = 0
            rbs = self.env['rubber.deliver'].search([('sanpham','=',rec.sanpham),('ngay','=',rec.ngay)])
            qktt = 0
            if len(rbs) > 0:
                for rb in rbs:
                    qktt += rb.quykhott
                if qktt > 0:
                    rec.tyle = rec.quykhott / qktt

    def giaomu(self):
        for rec in self:
            rec.state = 'giao'
            if len(self.env['company.truck'].search([('ngaygiao','=',rec.ngay)])) == 1:
                if rec.company_truck_id.id == False and rec.daily_name == 'Xe tải nhà':
                    rec.soluongtt = rec.soluong
                    rec.dott = rec.do
                    rec.quykhott = rec.quykho
                    rec.company_truck_id = self.env['company.truck'].search([('ngaygiao','=',rec.ngay)])[0].id
                #Nếu bên Nhận và bán tạo xong có id cho xe tải cùng ngày thì gắn company_truck_id và gán các giá trị thực tế
                #Trường hợp bán ngoài thì tạo rec.daily_name != 'Xe tải nhà' thì tạo 
                #elif rec.company_truck_id.id == False and rec.daily_name != 'Xe tải nhà':
                
                elif rec.daily_name != 'Xe tải nhà':
                    rec.env['rubber.harvest'].create({
                        'to': rec.to,
                        'daily': rec.daily_name,
                        'sanpham': rec.sanpham,
                        'soluong': rec.soluong,
                        'tyle': 1.0,
                        'do': rec.do,
                        'quykho': rec.quykho,
                        'rubberdeliver_id': rec.id,
                        'company_truck_id': self.env['company.truck'].search([('ngaygiao','=',rec.ngay)])[0].id,
                    })
        
    def chuagiao(self):
        for rec in self:
            rec.state = 'chua'

    def nhanmu(self):
        for rec in self:
            rec.state = 'nhan'

    @api.depends('soluong', 'do')
    def _compute_quykho(self):
        for rec in self:
            rec.quykho = rec.soluong * rec.do / 100

    @api.depends('soluongtt', 'dott')
    def _compute_quykhott(self):
        for rec in self:
            rec.quykhott = rec.soluongtt * rec.dott / 100

class RubberSell(models.Model):
    _name = 'rubber.sell'
    _description = 'Rubber Sell Model'

    ngay = fields.Date('Ngày', default=fields.Datetime.now(), required=True, store=True)
    daily = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer','=',True)], required=True,
        default=lambda self: self.env['res.partner'].search([('is_customer','=',True)], limit=1))
    sanpham_id = fields.Many2one('sanpham', string='Sản phẩm')
    sanpham = fields.Selection([
        ('nuoc', 'Mũ nước'), ('tap', 'Mũ tạp'), ('day', 'Mũ dây'), ('dong', 'Mũ đông'), ('chen', 'Mũ chén')
    ], string='Sản phẩm', required=True, default='nuoc')
    soluong = fields.Float('Số lượng bán', default='0', digits='One Decimal')
    do = fields.Float('Độ bán', default='0', digits='One Decimal')
    quykho = fields.Float('Quy khô bán', default='0', digits='One Decimal', compute='_compute_quykho')
    company_truck_id = fields.Many2one('company.truck', string='Xe công ty', ondelete='cascade', required=True)
    ngaygiao = fields.Date(related='company_truck_id.ngaygiao')
    dailygiao = fields.Char('dailygiao', readonly=True, default='Xe tải nhà')
    state = fields.Selection([
        ('no', 'Chưa phân bổ'), ('yes', 'Đã phân bổ')
    ], string='Phân bổ', default='no', readonly=True)
    
    def phan_bo(self):
        for rec in self:
            rec.state = 'yes'
            rbds = rec.env['rubber.deliver'].search([('company_truck_id','=',rec.company_truck_id.id),('sanpham','=',rec.sanpham),('ngay','=',rec.ngaygiao)])
            if len(rbds) > 0:
                for rbd in rbds:
                    rec.env['rubber.harvest'].create({
                        'to': rbd.to,
                        'daily': rec.daily.name,
                        'sanpham': rec.sanpham,
                        'tyle': rbd.tyle,
                        'soluong': rec.soluong,
                        'do': rec.do,
                        'rubbersell_id': rec.id,
                        'company_truck_id': rec.company_truck_id.id,
                    })
    
    @api.depends('soluong','do')
    def _compute_quykho(self):
        for rec in self:
            rec.quykho = rec.soluong * rec.do / 100

class RubberLoss(models.Model):
    _name = 'rubber.loss'
    _description = 'Rubber Loss Model'

    ngay = fields.Date('Ngày')
    to = fields.Char('Tổ')
    hhnuoc = fields.Float('Hao hụt nước', default='0', digits='One Decimal')
    hhdo = fields.Float('Hao hụt độ', default='0', digits='One Decimal')
    hhtap = fields.Float('Hao hụt tạp', default='0', digits='One Decimal')
    hhdong = fields.Float('Hao hụt đông', default='0', digits='One Decimal')
    hhday = fields.Float('Hao hụt dây', default='0', digits='One Decimal')
    company_truck_id = fields.Many2one('company.truck', string='Xe công ty', ondelete='cascade')