from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

#from .rubberprice import RubberPrice  # Import the RubberPrice class from the new file

class RubberHarvest(models.Model):
    _name = 'rubber.harvest'
    _description = 'Rubber Harvest Model'

    to_id = fields.Many2one('hr.department', string='Tổ')
    daily_id = fields.Many2one('res.partner', string='Đại lý')
    source = fields.Many2one('res.partner', string='Gốc', related='rubberdeliver_id.daily_id')
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
    ngay = fields.Date('Ngày', related='company_truck_id.ngaygiao', store=True)
    selected = fields.Boolean(string="Select")

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

    @api.depends('ngay', 'sanpham', 'daily_id')
    def _compute_name(self):
        for rec in self:
            # Customize the name as needed
            rec.name = f"{rec.ngay or ''} - {rec.sanpham or ''} - {rec.daily_id or ''}"

class RubberDeliver(models.Model):
    _name = 'rubber.deliver'
    _description = 'Rubber Deliver Model'

    ngay = fields.Date('Ngày giao', related='rubberbydate_id.ngay')
    ngay_giao = fields.Date(string='Ngày giao', compute='_compute_ngay_giao', store=True)    
    to_id = fields.Many2one('hr.department', string ='Tổ', related='rubberbydate_id.to', store=True)
    to_name = fields.Char(string='Tổ', related='to_id.name', store=True)    
    daily = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer','=',True)],
                default=lambda self: self.env['res.partner'].search([('is_customer','=',True),('name','=','Xe tải nhà')], limit=1))
    daily_id = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer','=',True)], required=True,
                default=lambda self: self.env['res.partner'].search([('is_customer','=',True),('name','=','Xe tải nhà')], limit=1))
    daily_name = fields.Char('Tên đại lý', related='daily_id.name')
    daily_ban = fields.Many2one('res.partner', string='Đại lý bán', compute='_compute_daily_ban', readonly=False)
       
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
        ('luu','Chưa lưu'),('chua', 'Chưa giao'), ('giao', 'Đã giao'), ('mua', 'Mua mũ'), ('nhan', 'Đã nhận'), ('order', 'Đã order')], string='Trạng thái',
        copy=False, default='chua', index=True, readonly=True,
        help="Trạng thái của mũ.")
    rubberbydate_id = fields.Many2one('rubber.date', string='Nhập sản lượng', ondelete='cascade')
    company_truck_id = fields.Many2one('company.truck', string='Xe công ty', ondelete='set null')
    tyle = fields.Float(compute='_compute_tyle', string='Tỷ lệ (%)')
    is_selected = fields.Boolean(string="Select", default=False)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', copy=False)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', copy=False)

    def unlink(self):
        for record in self:
            if record.state not in ['chua', 'giao']:
                raise UserError(_("You can only delete records in 'chua' or 'giao' state."))
        return super().unlink()
    @api.depends('ngay')
    def _compute_ngay_giao(self):
        for rec in self:
            rec.ngay_giao = rec.ngay    
    
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

    @api.depends('daily_id', 'company_truck_id')
    def _compute_daily_ban(self):
        for record in self:
            # Default: daily_ban = daily_id
            record.daily_ban = record.daily_id
            
            # If daily_id is "Xe tải nhà", apply special logic
            if (record.daily_id and record.daily_id.name == 'Xe tải nhà' and record.company_truck_id) or (record.to_id and record.to_name == 'TỔ Xe tải' and record.company_truck_id):
                # Search for rubber.sell records with the same company_truck_id
                sell_records = self.env['rubber.sell'].search([
                    ('company_truck_id', '=', record.company_truck_id.id),                    
                    ('sanpham', '=', record.sanpham)
                ])
                
                # If exactly one sell record exists, use its daily_id
                if len(sell_records) == 1:
                    record.daily_ban = sell_records.daily_id
                else:
                    # If no sell records or multiple sell records, set to False
                    record.daily_ban = False

    def giaomu(self):
        for rec in self:
            if rec.state == 'chua':
                rec.state = 'giao'   
                ngay = rec.ngay
                if not ngay:
                    continue  # Skip if ngay is not set
                    
                # Search for truck once
                truck = self.env['company.truck'].search([('ngaygiao', '=', ngay)], limit=1)
                if not truck:
                    truck = self.env['company.truck'].create({
                        'ngaygiao': ngay,
                        'ngayban': ngay,
                    })  
                
                rec.soluongtt = rec.soluong
                rec.dott = rec.do
                rec.quykhott = rec.quykho
                rec.company_truck_id = truck.id    
        
    def sualai(self):
        for rec in self:
            if rec.state == 'order':
                # Direct access to the order line - no search needed
                if rec.sale_order_line_id:
                    order_line = rec.sale_order_line_id
                    sale_order = order_line.order_id
                    
                    # Check if order is in an editable state
                    if sale_order.state not in ['draft', 'cancel']:
                        raise UserError(_(
                            "Cannot change delivery status: the sales order is in '{}' state. "
                            "Please cancel the sales order first."
                        ).format(sale_order.state))
                    
                    # If we can proceed, unlink the order
                    line_count = len(sale_order.order_line)
                    order_line.unlink()
                    
                    if line_count == 1:
                        sale_order.unlink()
                
                # Update state and clear references
                rec.sale_order_id = False
                rec.sale_order_line_id = False
                rec.state = 'nhan'
            
            elif rec.state == 'nhan':
                rec.state = 'giao'                
            elif rec.state == 'giao':   
                rec.state = 'chua'
                rec.company_truck_id = False

            _logger.info(f"Record ID: {rec.id}, sale_order_line_id: {rec.sale_order_line_id}, "
                    f"type: {type(rec.sale_order_line_id)}")
        
            if rec.sale_order_line_id:
                _logger.info(f"Order line exists: {rec.sale_order_line_id.exists()}")


    def nhanmu(self):
        for rec in self:
            if rec.state == 'giao':
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
    daily_id = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer','=',True)], required=True,
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
                        'to_id': rbd.to_id,
                        'daily_id': rec.daily_id,                        
                        'sanpham': rec.sanpham,
                        'tyle': rbd.tyle,
                        'soluong': rec.soluong,
                        'do': rec.do,
                        'rubbersell_id': rec.id,
                        'rubberdeliver_id': rbd.id,
                        'company_truck_id': rec.company_truck_id.id,
                    })
    
    @api.depends('soluong','do')
    def _compute_quykho(self):
        for rec in self:
            rec.quykho = rec.soluong * rec.do / 100
    
    def unlink(self):
        for sell in self:
            harvests = self.env['rubber.harvest'].search([('rubbersell_id', '=', sell.id)])
            harvests.unlink()
        return super(RubberSell, self).unlink()
    
    
        
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