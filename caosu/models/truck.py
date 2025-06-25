from collections import defaultdict
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class RubberTruck(models.Model):
    _name = "rubber.truck"
    _description = "Rubber Truck Model"

    daily_id = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer', '=', 'True')])
    dayban = fields.Float('Mũ dây')
    doban = fields.Float('Độ')
    dongban = fields.Float('Mũ đông')
    nuocban = fields.Float('Mũ nước')
    tapban = fields.Float('Mũ tạp')
    tenxe = fields.Char('Tên xe')
    company_truck_id = fields.Many2one('company.truck', string='Xe công ty')

class CompanyTruck(models.Model):
    _name = "company.truck"
    _description = "Company Truck"
    _rec_name = 'ngaygiao'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ngaygiao = fields.Date('Ngày giao', default=fields.Datetime.now(), required=True, tracking=True, store=True)
    thang = fields.Char('Tháng', compute='_compute_ngay', store=True)
    nam = fields.Char('Năm', compute='_compute_ngay', store=True)
    nam_kt = fields.Char('Năm khai thác', compute='_compute_ngay', store=True)
    ngayban = fields.Date('Ngày bán', default=fields.Datetime.now(), required=True, tracking=True, store=True)
    #recorded = fields.Boolean('recorded', default=False, compute='_compute_recorded')
    sanpham_id = fields.Many2one('sanpham', string='Sản phẩm')
    
    # 1. Thêm field để lọc loại sản phẩm
    active_sanpham = fields.Selection([
        ('all', 'Tất cả'),
        ('nuoc', 'Mũ nước'),
        ('tap', 'Mũ tạp'),
        ('day', 'Mũ dây'),
        ('dong', 'Mũ đông'),
        ('chen', 'Mũ chén')
    ], string="Lọc sản phẩm", default='all')

    # 2. Giữ lại field one2many gốc - không thay đổi
    deliver_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        string='Nhận mũ'
    )    
    # 3. Tạo field computed để hiển thị dữ liệu được lọc
    filtered_deliver_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        compute='_compute_filtered_deliver_line_ids',
        readonly=False,  # Thêm dòng này
        string='Danh sách lọc'   )

    filtered_tructiep_deliver_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        compute='_compute_filtered_tructiep_deliver_line_ids',
        readonly=False,  # Thêm dòng này
        string='Danh sách lọc'   )

    
    # 4. Phương thức tính toán cho filtered_deliver_line_ids
    @api.depends('active_sanpham', 'deliver_line_ids', 'deliver_line_ids.sanpham', 
                'deliver_line_ids.daily_id', 'deliver_line_ids.to_id', 'deliver_line_ids.state','ngaygiao')
    def _compute_filtered_deliver_line_ids(self):
        for truck in self:
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.ngay == truck.ngaygiao and
                          (l.soluong != 0 or l.soluongtt != 0) and
                          l.state in ['giao', 'mua', 'nhan']
            )
            # Lọc theo đại lý "Xe tải nhà" và tổ "TỔ Xe tải"
            lines = lines.filtered(
                lambda l: (l.daily_id.name == 'Xe tải nhà') or 
                            (l.to_id.name == 'TỔ Xe tải')
            )
            # Lọc theo sanpham nếu không phải "all"
            if truck.active_sanpham != 'all':
                lines = lines.filtered(lambda l: l.sanpham == truck.active_sanpham)
                
            # Sắp xếp theo daily, sanpham
            lines = lines.sorted(key=lambda l: (l.daily_id.name if l.daily_id else "", l.sanpham))
            
            truck.filtered_deliver_line_ids = lines
    
    # Phương thức tính toán cho filtered_tructiep_deliver_line_ids
    @api.depends('active_sanpham', 'deliver_line_ids', 'deliver_line_ids.sanpham', 
                'deliver_line_ids.daily_id', 'deliver_line_ids.to_id', 'deliver_line_ids.state', 'ngaygiao')
    def _compute_filtered_tructiep_deliver_line_ids(self):
        for truck in self:
            # Lọc theo ngày, số lượng và trạng thái
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.ngay == truck.ngaygiao and
                          (l.soluong != 0 or l.soluongtt != 0) and
                          l.state in ['giao','nhan']
            )
            
            # Lọc theo đại lý khác "Xe tải nhà" và tổ khác "TỔ Xe tải"
            lines = lines.filtered(
                lambda l: (l.daily_id.name != 'Xe tải nhà' and 
                           l.to_id.name != 'TỔ Xe tải')
            )
            
            '''# Lọc theo sanpham nếu không phải "all"
            if truck.active_sanpham != 'all':
                lines = lines.filtered(lambda l: l.sanpham == truck.active_sanpham)'''
                
            # Sắp xếp theo daily, sanpham
            lines = lines.sorted(key=lambda l: (l.daily_id.name if l.daily_id else "", l.sanpham))
            
            truck.filtered_tructiep_deliver_line_ids = lines
    
    # 5. Các methods để thiết lập active_sanpham qua buttons
    def set_sanpham_all(self):
        self.active_sanpham = 'all'
        return True

    def set_sanpham_nuoc(self):
        self.active_sanpham = 'nuoc'
        return True

    def set_sanpham_tap(self):
        self.active_sanpham = 'tap'
        return True

    def set_sanpham_day(self):
        self.active_sanpham = 'day'
        return True

    def set_sanpham_dong(self):
        self.active_sanpham = 'dong'
        return True

    def set_sanpham_chen(self):
        self.active_sanpham = 'chen'
        return True

    invoice_xetainha_line_ids = fields.One2many(
    'rubber.deliver',
    'company_truck_id',  # Quan trọng: Thêm field relation
    compute='_compute_invoice_xetainha_line_ids',
    readonly=False,
    string='Mũ xe tải nhà'
    )

    # 3 trường one2many mới cho trang INVOICE
    invoice_tructiep_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',  # Quan trọng: Thêm field relation
        compute='_compute_invoice_tructiep_line_ids',
        readonly=False,
        string='Mũ trực tiếp'
    )

    invoice_chomu_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',  # Quan trọng: Thêm field relation
        compute='_compute_invoice_chomu_line_ids',
        readonly=False,
        string='Mũ chờ'
    )
    delivertap_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        string='Nhận mũ tạp',
        domain=[
            '|',
            '&', ('daily_name', '=', 'Xe tải nhà'), ('state', 'in', ['giao', 'nhan']),
            '&', ('daily_name', '!=', 'Xe tải nhà'), ('state', '=', 'mua'),
            ('sanpham', '=', 'tap')
        ]
    )
    # Phương thức tính toán cho invoice_xetainha_line_ids
    @api.depends('deliver_line_ids', 'deliver_line_ids.daily_id', 'deliver_line_ids.state', 'deliver_line_ids.ngay', 'ngaygiao')
    def _compute_invoice_xetainha_line_ids(self):
        for truck in self:
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.state in ['nhan','mua','invoice'] and 
                          l.ngay == truck.ngaygiao and
                          l.daily_id.name == 'Xe tải nhà'
            )
            truck.invoice_xetainha_line_ids = lines
    
    # Phương thức tính toán cho invoice_tructiep_line_ids
    @api.depends('deliver_line_ids', 'deliver_line_ids.daily_id', 'deliver_line_ids.to_id', 'deliver_line_ids.state', 'deliver_line_ids.ngay', 'ngaygiao')
    def _compute_invoice_tructiep_line_ids(self):
        for truck in self:
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.state in ['nhan','invoice'] and 
                          l.ngay == truck.ngaygiao and
                          l.daily_id.name != 'Xe tải nhà' and
                          l.to_id.name != 'TỔ Xe tải'
            )
            truck.invoice_tructiep_line_ids = lines
    
    # Phương thức tính toán cho invoice_chomu_line_ids
    @api.depends('deliver_line_ids', 'deliver_line_ids.daily_id', 'deliver_line_ids.to_id', 'deliver_line_ids.state', 'deliver_line_ids.ngay', 'ngaygiao')
    def _compute_invoice_chomu_line_ids(self):
        for truck in self:
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.state in ['mua','invoice'] and 
                          l.ngay == truck.ngaygiao and
                          l.daily_id.name != 'Xe tải nhà' and
                          l.to_id.name == 'TỔ Xe tải'
            )
            truck.invoice_chomu_line_ids = lines

    deliverday_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        string='Nhận mũ dây',
        domain=[
            '|',
            '&', ('daily_name', '=', 'Xe tải nhà'), ('state', 'in', ['giao', 'nhan']),
            '&', ('daily_name', '!=', 'Xe tải nhà'), ('state', '=', 'mua'),
            ('sanpham', '=', 'day')
        ]       
    )
    deliverdong_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        string='Nhận mũ đông',
        domain=[
            '|',
            '&', ('daily_name', '=', 'Xe tải nhà'), ('state', 'in', ['giao', 'nhan']),
            '&', ('daily_name', '!=', 'Xe tải nhà'), ('state', '=', 'mua'),
            ('sanpham', '=', 'dong')    
        ]
    )
    deliverchen_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        string='Nhận mũ chén',
        domain=[
            '|',
            '&', ('daily_name', '=', 'Xe tải nhà'), ('state', 'in', ['giao', 'nhan']),
            '&', ('daily_name', '!=', 'Xe tải nhà'), ('state', '=', 'mua'),
            ('sanpham', '=', 'chen')
        ]
    )
    
    sell_line_ids = fields.One2many('rubber.sell', 'company_truck_id', tracking=True, string='Bán mũ nước')
    selltap_line_ids = fields.One2many('rubber.sell', 'company_truck_id', tracking=True, string='Bán mũ tạp', domain=[('sanpham','=','tap')])
    sellday_line_ids = fields.One2many('rubber.sell', 'company_truck_id', tracking=True, string='Bán mũ dây', domain=[('sanpham','=','day')])
    selldong_line_ids = fields.One2many('rubber.sell', 'company_truck_id', tracking=True, string='Bán mũ đông', domain=[('sanpham','=','dong')])
    sellchen_line_ids = fields.One2many('rubber.sell', 'company_truck_id', tracking=True, string='Bán mũ chén', domain=[('sanpham','=','chen')])
    haohut_nuoc = fields.Float('Hao hụt', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    tylehh_nuoc = fields.Float('Tỷ lệ hao hụt (%)', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    haohutdo_nuoc = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    tylehhdo_nuoc = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    haohutqk_nuoc = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    tylehhqk_nuoc = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    soluong_nuoc = fields.Float('SL nước nhận', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    do_nuoc = fields.Float('Độ nước nhận', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    quykho_nuoc = fields.Float('QK nước nhận', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    soluongban_nuoc = fields.Float('SL nước bán', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    doban_nuoc = fields.Float('Độ nước bán', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    quykhoban_nuoc = fields.Float('QK nước bán', default='0', digits='One Decimal', compute='_compute_haohut_nuoc')
    haohut_tap = fields.Float('Hao hụt', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    tylehh_tap = fields.Float('Tỷ lệ hao hụt (%)', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    haohutdo_tap = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    tylehhdo_tap = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    haohutqk_tap = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    tylehhqk_tap = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    soluong_tap = fields.Float('Nhận', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    do_tap = fields.Float('Độ nhận', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    quykho_tap = fields.Float('Quy khô nhận', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    soluongban_tap = fields.Float('SL nước bán', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    doban_tap = fields.Float('Độ nước bán', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    quykhoban_tap = fields.Float('QK nước bán', default='0', digits='One Decimal', compute='_compute_haohut_tap')
    haohut_day = fields.Float('Hao hụt', default='0', digits='One Decimal', compute='_compute_haohut_day')
    tylehh_day = fields.Float('Tỷ lệ hao hụt (%)', default='0', digits='One Decimal', compute='_compute_haohut_day')
    haohutdo_day = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_day')
    tylehhdo_day = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_day')
    haohutqk_day = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_day')
    tylehhqk_day = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_day')
    haohut_dong = fields.Float('Hao hụt', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    soluong_day = fields.Float('Nhận', default='0', digits='One Decimal', compute='_compute_haohut_day')
    do_day = fields.Float('Độ nhận', default='0', digits='One Decimal', compute='_compute_haohut_day')
    quykho_day = fields.Float('Quy khô nhận', default='0', digits='One Decimal', compute='_compute_haohut_day')
    soluongban_day = fields.Float('SL nước bán', default='0', digits='One Decimal', compute='_compute_haohut_day')
    doban_day = fields.Float('Độ nước bán', default='0', digits='One Decimal', compute='_compute_haohut_day')
    quykhoban_day = fields.Float('QK nước bán', default='0', digits='One Decimal', compute='_compute_haohut_day')
    tylehh_dong = fields.Float('Tỷ lệ hao hụt (%)', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    haohutdo_dong = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    tylehhdo_dong = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    haohutqk_dong = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    tylehhqk_dong = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    soluong_dong = fields.Float('Nhận', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    do_dong = fields.Float('Độ nhận', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    quykho_dong = fields.Float('Quy khô nhận', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    soluongban_dong = fields.Float('SL nước bán', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    doban_dong = fields.Float('Độ nước bán', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    quykhoban_dong = fields.Float('QK nước bán', default='0', digits='One Decimal', compute='_compute_haohut_dong')
    haohut_chen = fields.Float('Hao hụt', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    tylehh_chen = fields.Float('Tỷ lệ hao hụt (%)', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    haohutdo_chen = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    tylehhdo_chen = fields.Float('Độ', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    haohutqk_chen = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    tylehhqk_chen = fields.Float('Quy khô', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    soluong_chen = fields.Float('Nhận', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    do_chen = fields.Float('Độ nhận', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    quykho_chen = fields.Float('Quy khô nhận', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    soluongban_chen = fields.Float('SL nước bán', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    doban_chen = fields.Float('Độ nước bán', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    quykhoban_chen = fields.Float('QK nước bán', default='0', digits='One Decimal', compute='_compute_haohut_chen')
    harvest_line_ids = fields.One2many('rubber.harvest', 'company_truck_id')
    harvesttap_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ tạp xe tải', domain=[('sanpham','=','tap'),('rubbersell_id','!=',False)])
    harvestday_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ dây xe tải', domain=[('sanpham','=','day'),('rubbersell_id','!=',False)])
    harvestdong_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ đông xe tải', domain=[('sanpham','=','dong'),('rubbersell_id','!=',False)])
    harvestchen_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ chén xe tải', domain=[('sanpham','=','chen'),('rubbersell_id','!=',False)])
    harvest1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ nước trực tiếp', domain=[('sanpham','=','nuoc'),('rubbersell_id','=',False)])
    harvesttap1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ tạp trực tiếp', domain=[('sanpham','=','tap'),('rubbersell_id','=',False)])
    harvestday1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ dây trực tiếp', domain=[('sanpham','=','day'),('rubbersell_id','=',False)])
    harvestdong1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ đông trực tiếp', domain=[('sanpham','=','dong'),('rubbersell_id','=',False)])
    harvestchen1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ chén trực tiếp', domain=[('sanpham','=','chen'),('rubbersell_id','=',False)])
    #nhannuoc = fields.Boolean(compute='_compute_nhannuoc', string='Nhận mũ nước xe tải')
    nhantap = fields.Boolean(compute='_compute_nhantap', string='Nhận mũ tạp xe tải')
    nhanday = fields.Boolean(compute='_compute_nhanday', string='Nhận mũ dây xe tải')
    nhandong = fields.Boolean(compute='_compute_nhandong', string='Nhận mũ đông xe tải')
    nhanchen = fields.Boolean(compute='_compute_nhanchen', string='Nhận mũ chén xe tải')
    #nhannuoc1 = fields.Boolean(compute='_compute_nhannuoc', string='Nhận mũ nước trực tiếp')
    nhantap1 = fields.Boolean(compute='_compute_nhantap', string='Nhận mũ tạp trực tiếp')
    nhanday1 = fields.Boolean(compute='_compute_nhanday', string='Nhận mũ dây trực tiếp')
    nhandong1 = fields.Boolean(compute='_compute_nhandong', string='Nhận mũ đông trực tiếp')
    nhanchen1 = fields.Boolean(compute='_compute_nhanchen', string='Nhận mũ chén trực tiếp')
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    debug = fields.Html('Debug Info')    

    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)

    @api.depends('ngaygiao')
    def _compute_ngay(self):
        for rec in self:
            rec.thang = '01'
            rec.nam = '2024'
            rec.nam_kt = '2024'
            #if rec.recorded == True:
            rec.thang = datetime.strptime(str(rec.ngaygiao),'%Y-%m-%d').strftime('%m')
            rec.nam = datetime.strptime(str(rec.ngaygiao),'%Y-%m-%d').strftime('%Y')
            if rec.thang == '01':
                rec.nam_kt = str(int(rec.nam) - 1)
            else:
                rec.nam_kt = rec.nam

    
        
    def mua_mu(self):
        self.ensure_one()
        # Get current user's department
        current_department = self.env.user.department_id
        if not current_department:
            raise UserError(_("Current user does not have a department assigned."))

        # Search for rubber.date with ngay = self.ngaygiao and to = current user's department
        rubber_date = self.env['rubber.date'].search([
            ('ngay', '=', self.ngaygiao),
            ('to', '=', current_department.id)
        ], limit=1)

        if not rubber_date:
            rubber_date = self.env['rubber.date'].create({
                'ngay': self.ngaygiao,
                'to': current_department.id,
            })

        return {
            'name': _('Mua mũ'),
            'type': 'ir.actions.act_window',
            'res_model': 'rubber.deliver',
            'view_mode': 'form',
            'view_id': self.env.ref('caosu.rubber_deliver_buy_view_form').id,
            'target': 'new',
            'context': dict(self._context, **{
                'default_company_truck_id': self.id,
                'default_rubberbydate_id': rubber_date.id,
                'default_to_id': current_department.id,
                'default_state': 'mua'
            })
        }
    
    
    
    @api.depends('delivertap_line_ids')
    def _compute_nhantap(self):
        self.ensure_one()
        self.nhantap = False
        self.nhantap1 = False
        rbd = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'tap'),
            ('state', 'in', ['giao', 'nhan', 'mua'])
        ])
        if len(rbd) > 0:
            self.nhantap = True
        else:
            self.nhantap = False
        rbd1 = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'tap'),
            ('state', 'in', ['giao', 'nhan', 'mua'])
        ])
        if len(rbd1) > 0:
            self.nhantap1 = True
        else:
            self.nhantap1 = False
    
    @api.depends('deliverday_line_ids')
    def _compute_nhanday(self):
        self.ensure_one()
        self.nhanday = False
        self.nhanday1 = False
        rbd = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'day'),
            ('state', 'in', ['giao', 'nhan', 'mua'])
        ])
        if len(rbd) > 0:
            self.nhanday = True
        else:
            self.nhanday = False
        rbd1 = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'day'),
            ('state', 'in', ['giao', 'nhan', 'mua'])
        ])
        if len(rbd1) > 0:
            self.nhanday1 = True
        else:
            self.nhanday1 = False

    @api.depends('deliverdong_line_ids')
    def _compute_nhandong(self):
        self.ensure_one()
        self.nhandong = False
        self.nhandong1 = False
        rbd = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'dong'),
            ('state', 'in', ['giao', 'nhan', 'mua'])
        ])
        if len(rbd) > 0:
            self.nhandong = True
        else:
            self.nhandong = False
        rbd1 = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'dong'),
            ('state', 'in', ['giao', 'nhan', 'mua'])
        ])
        if len(rbd1) > 0:
            self.nhandong1 = True
        else:
            self.nhandong1 = False

    @api.depends('deliverchen_line_ids')
    def _compute_nhanchen(self):
        self.ensure_one()
        self.nhanchen = False
        self.nhanchen1 = False
        rbd = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'chen'),
            ('state', 'in', ['giao', 'nhan', 'mua'])
        ])
        if len(rbd) > 0:
            self.nhanchen = True
        else:
            self.nhanchen = False
        rbd1 = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'chen'),
            ('state', 'in', ['giao', 'nhan', 'mua'])
        ])
        if len(rbd1) > 0:
            self.nhanchen1 = True
        else:
            self.nhanchen1 = False

    @api.depends('active_sanpham', 'filtered_deliver_line_ids', 'deliver_line_ids','sell_line_ids')
    def _compute_haohut_nuoc(self):
        for rec in self:
            if len(rec.filtered_deliver_line_ids) > 0:
                nhan = 0
                donhan = 0
                qknhan = 0
                for line in rec.filtered_deliver_line_ids:
                        nhan += line.soluongtt
                        donhan += line.dott * line.soluongtt
                        qknhan += line.quykhott 
                if nhan > 0:
                    donhan = donhan / nhan
                rec.soluong_nuoc = nhan
                rec.do_nuoc = donhan
                rec.quykho_nuoc = qknhan

            rec.soluongban_nuoc = 0
            rec.doban_nuoc = 0
            rec.quykhoban_nuoc = 0
            rec.haohut_nuoc = 0
            rec.tylehh_nuoc = 0
            rec.haohutdo_nuoc = 0
            rec.tylehhdo_nuoc = 0
            rec.haohutqk_nuoc = 0
            rec.tylehhqk_nuoc = 0
            rec.soluong_nuoc = 0
            rec.do_nuoc = 0
            rec.quykho_nuoc = 0
            haohut_nuoc = 0
            tylehh_nuoc = 0
            haohutdo_nuoc = 0
            tylehhdo_nuoc = 0
            haohutqk_nuoc = 0
            tylehhqk_nuoc = 0
               
            if len(rec.deliver_line_ids) > 0 and len(rec.sell_line_ids) > 0:
                nhan = 0
                ban = 0
                donhan = 0
                doban = 0
                qknhan = 0
                qkban = 0
                for line in rec.deliver_line_ids:
                    nhan += line.soluongtt
                    donhan += line.dott * line.soluongtt
                    qknhan += line.quykhott
                if nhan > 0:
                    donhan = donhan / nhan
                rec.soluong_nuoc = nhan
                rec.do_nuoc = donhan
                rec.quykho_nuoc = qknhan
                for line in rec.sell_line_ids:
                    ban += line.soluong
                    doban += line.do * line.soluong
                    qkban += line.quykho
                if ban > 0:
                    doban = doban / ban
                if nhan > 0:
                    haohut_nuoc = ban - nhan
                    tylehh_nuoc = haohut_nuoc / nhan * 100
                if donhan > 0:
                    haohutdo_nuoc = doban - donhan
                    tylehhdo_nuoc = haohutdo_nuoc / donhan * 100
                if qknhan > 0:
                    haohutqk_nuoc = qkban - qknhan
                    tylehhqk_nuoc = haohutqk_nuoc / qknhan * 100
                rec.soluongban_nuoc = ban
                rec.doban_nuoc = doban
                rec.quykhoban_nuoc = qkban
                rec.haohut_nuoc = haohut_nuoc
                rec.tylehh_nuoc = tylehh_nuoc
                rec.haohutdo_nuoc = haohutdo_nuoc
                rec.tylehhdo_nuoc = tylehhdo_nuoc
                rec.haohutqk_nuoc = haohutqk_nuoc
                rec.tylehhqk_nuoc = tylehhqk_nuoc
        
    @api.depends('delivertap_line_ids','selltap_line_ids')
    def _compute_haohut_tap(self):
        for rec in self:
            rec.soluongban_tap = 0
            rec.doban_tap = 0
            rec.quykhoban_tap = 0
            rec.haohut_tap = 0
            rec.tylehh_tap = 0
            rec.haohutdo_tap = 0
            rec.tylehhdo_tap = 0
            rec.haohutqk_tap = 0
            rec.tylehhqk_tap = 0
            rec.soluong_tap = 0
            rec.do_tap = 0
            rec.quykho_tap = 0
            haohut_tap = 0
            tylehh_tap = 0
            haohutdo_tap = 0
            tylehhdo_tap = 0
            haohutqk_tap = 0
            tylehhqk_tap = 0
            if len(rec.delivertap_line_ids) > 0 and len(rec.selltap_line_ids) > 0:
                nhan = 0
                ban = 0
                donhan = 0
                doban = 0
                qknhan = 0
                qkban = 0
                for line in rec.delivertap_line_ids:
                    nhan += line.soluongtt
                    donhan += line.dott * line.soluongtt
                    qknhan += line.quykhott
                if nhan > 0:
                    donhan = donhan / nhan
                rec.soluong_tap = nhan
                rec.do_tap = donhan
                rec.quykho_tap = qknhan
                for line in rec.selltap_line_ids:
                    ban += line.soluong
                    doban += line.do * line.soluong
                    qkban += line.quykho
                if ban > 0:
                    doban = doban / ban
                if nhan > 0:
                    haohut_tap = ban - nhan
                    tylehh_tap = haohut_tap / nhan * 100
                if donhan > 0:
                    haohutdo_tap = doban - donhan
                    tylehhdo_tap = haohutdo_tap / donhan * 100
                if qknhan > 0:
                    haohutqk_tap = qkban - qknhan
                    tylehhqk_tap = haohutqk_tap / qknhan * 100
                rec.soluongban_tap = ban
                rec.doban_tap = doban
                rec.quykhoban_tap = qkban
                rec.haohut_tap = haohut_tap
                rec.tylehh_tap = tylehh_tap
                rec.haohutdo_tap = haohutdo_tap
                rec.tylehhdo_tap = tylehhdo_tap
                rec.haohutqk_tap = haohutqk_tap
                rec.tylehhqk_tap = tylehhqk_tap

    @api.depends('deliverday_line_ids','sellday_line_ids')
    def _compute_haohut_day(self):
        for rec in self:
            rec.soluongban_day = 0
            rec.doban_day = 0
            rec.quykhoban_day = 0
            rec.haohut_day = 0
            rec.tylehh_day = 0
            rec.haohutdo_day = 0
            rec.tylehhdo_day = 0
            rec.haohutqk_day = 0
            rec.tylehhqk_day = 0
            rec.soluong_day = 0
            rec.do_day = 0
            rec.quykho_day = 0
            haohut_day = 0
            tylehh_day = 0
            haohutdo_day = 0
            tylehhdo_day = 0
            haohutqk_day = 0
            tylehhqk_day = 0
            if len(rec.deliverday_line_ids) > 0 and len(rec.sellday_line_ids) > 0:
                nhan = 0
                ban = 0
                donhan = 0
                doban = 0
                qknhan = 0
                qkban = 0
                for line in rec.deliverday_line_ids:
                    nhan += line.soluongtt
                    donhan += line.dott * line.soluongtt
                    qknhan += line.quykhott
                if nhan > 0:
                    donhan = donhan / nhan
                rec.soluong_day = nhan
                rec.do_day = donhan
                rec.quykho_day = qknhan
                for line in rec.sellday_line_ids:
                    ban += line.soluong
                    doban += line.do * line.soluong
                    qkban += line.quykho
                if ban > 0:
                    doban = doban / ban
                if nhan > 0:
                    haohut_day = ban - nhan
                    tylehh_day = haohut_day / nhan * 100
                if donhan > 0:
                    haohutdo_day = doban - donhan
                    tylehhdo_day = haohutdo_day / donhan * 100
                if qknhan > 0:
                    haohutqk_day = qkban - qknhan
                    tylehhqk_day = haohutqk_day / qknhan * 100
                rec.soluongban_day = ban
                rec.doban_day = doban
                rec.quykhoban_day = qkban
                rec.haohut_day = haohut_day
                rec.tylehh_day = tylehh_day
                rec.haohutdo_day = haohutdo_day
                rec.tylehhdo_day = tylehhdo_day
                rec.haohutqk_day = haohutqk_day
                rec.tylehhqk_day = tylehhqk_day

    @api.depends('deliverdong_line_ids','selldong_line_ids')
    def _compute_haohut_dong(self):
        for rec in self:
            rec.soluongban_dong = 0
            rec.doban_dong = 0
            rec.quykhoban_dong = 0
            rec.haohut_dong = 0
            rec.tylehh_dong = 0
            rec.haohutdo_dong = 0
            rec.tylehhdo_dong = 0
            rec.haohutqk_dong = 0
            rec.tylehhqk_dong = 0
            rec.soluong_dong = 0
            rec.do_dong = 0
            rec.quykho_dong = 0
            haohut_dong = 0
            tylehh_dong = 0
            haohutdo_dong = 0
            tylehhdo_dong = 0
            haohutqk_dong = 0
            tylehhqk_dong = 0
            if len(rec.deliverdong_line_ids) > 0 and len(rec.selldong_line_ids) > 0:
                nhan = 0
                ban = 0
                donhan = 0
                doban = 0
                qknhan = 0
                qkban = 0
                for line in rec.deliverdong_line_ids:
                    nhan += line.soluongtt
                    donhan += line.dott * line.soluongtt
                    qknhan += line.quykhott
                if nhan > 0:
                    donhan = donhan / nhan
                rec.soluong_dong = nhan
                rec.do_dong = donhan
                rec.quykho_dong = qknhan
                for line in rec.selldong_line_ids:
                    ban += line.soluong
                    doban += line.do * line.soluong
                    qkban += line.quykho
                if ban > 0:
                    doban = doban / ban
                if nhan > 0:
                    haohut_dong = ban - nhan
                    tylehh_dong = haohut_dong / nhan * 100
                if donhan > 0:
                    haohutdo_dong = doban - donhan
                    tylehhdo_dong = haohutdo_dong / donhan * 100
                if qknhan > 0:
                    haohutqk_dong = qkban - qknhan
                    tylehhqk_dong = haohutqk_dong / qknhan * 100
                rec.soluongban_dong = ban
                rec.doban_dong = doban
                rec.quykhoban_dong = qkban
                rec.haohut_dong = haohut_dong
                rec.tylehh_dong = tylehh_dong
                rec.haohutdo_dong = haohutdo_dong
                rec.tylehhdo_dong = tylehhdo_dong
                rec.haohutqk_dong = haohutqk_dong
                rec.tylehhqk_dong = tylehhqk_dong

    @api.depends('deliverchen_line_ids','sellchen_line_ids')
    def _compute_haohut_chen(self):
        for rec in self:
            rec.soluongban_chen = 0
            rec.doban_chen = 0
            rec.quykhoban_chen = 0
            rec.haohut_chen = 0
            rec.tylehh_chen = 0
            rec.haohutdo_chen = 0
            rec.tylehhdo_chen = 0
            rec.haohutqk_chen = 0
            rec.tylehhqk_chen = 0
            rec.soluong_chen = 0
            rec.do_chen = 0
            rec.quykho_chen = 0
            haohut_chen = 0
            tylehh_chen = 0
            haohutdo_chen = 0
            tylehhdo_chen = 0
            haohutqk_chen = 0
            tylehhqk_chen = 0
            if len(rec.deliverchen_line_ids) > 0 and len(rec.sellchen_line_ids) > 0:
                nhan = 0
                ban = 0
                donhan = 0
                doban = 0
                qknhan = 0
                qkban = 0
                for line in rec.deliverchen_line_ids:
                    nhan += line.soluongtt
                    donhan += line.dott * line.soluongtt
                    qknhan += line.quykhott
                if nhan > 0:
                    donhan = donhan / nhan
                rec.soluong_chen = nhan
                rec.do_chen = donhan
                rec.quykho_chen = qknhan
                for line in rec.sellchen_line_ids:
                    ban += line.soluong
                    doban += line.do * line.soluong
                    qkban += line.quykho
                if ban > 0:
                    doban = doban / ban
                if nhan > 0:
                    haohut_chen = ban - nhan
                    tylehh_chen = haohut_chen / nhan * 100
                if donhan > 0:
                    haohutdo_chen = doban - donhan
                    tylehhdo_chen = haohutdo_chen / donhan * 100
                if qknhan > 0:
                    haohutqk_chen = qkban - qknhan
                    tylehhqk_chen = haohutqk_chen / qknhan * 100
                rec.soluongban_chen = ban
                rec.doban_chen = doban
                rec.quykhoban_chen = qkban
                rec.haohut_chen = haohut_chen
                rec.tylehh_chen = tylehh_chen
                rec.haohutdo_chen = haohutdo_chen
                rec.tylehhdo_chen = tylehhdo_chen
                rec.haohutqk_chen = haohutqk_chen
                rec.tylehhqk_chen = tylehhqk_chen

    @api.constrains('ngaygiao')
    def _check_rubberdate_unique(self):
        companytruck_counts = self.search_count([('ngaygiao','=',self.ngaygiao),('id','!=',self.id)])
        if companytruck_counts > 0:
            raise ValidationError("Nhận và bán ngày " + str(datetime.strptime(str(self.ngaygiao),'%Y-%m-%d').strftime('%d/%m/%Y')) + " đã tồn tại.")
        '''if len(self.env['rubber.date'].search([('ngay','=',self.ngaygiao)])) == False:
            raise ValidationError(_('Ngày ' + str(datetime.strptime(str(self.ngaygiao),'%Y-%m-%d').strftime('%d/%m/%Y')) + ' không có mũ giao.'))'''

    '''def _compute_recorded(self):
        for rec in self:            
            rec.recorded = True'''   
                        
                
    def action_create_sale_order_from_selected_lines(self):
        self.ensure_one()
        
        # Get SELECTED rubber.deliver lines
        selected_lines = (self.invoice_xetainha_line_ids + 
                        self.invoice_tructiep_line_ids + 
                        self.invoice_chomu_line_ids).filtered(lambda l: l.is_selected)
        
        if not selected_lines:
            raise UserError(_("No lines selected. Please select at least one line."))
        
        # Group lines by daily_id and to_id
        lines_by_daily_to = defaultdict(list)
        for line in selected_lines:
            if not line.daily_ban:
                raise UserError(_("Line for product %s has no partner (daily_id).") % line.sanpham)
            
            key = (line.daily_ban, line.to_id)
            lines_by_daily_to[key].append(line)
        debug_line = f"line: {lines_by_daily_to}"
        self.debug = (self.debug or '') + debug_line
        # Create sale orders for each partner+team combination
        SaleOrder = self.env['sale.order']
        SaleOrderLine = self.env['sale.order.line']
        Partner = self.env['res.partner']
        Product = self.env['product.product']
        
        # Map sanpham values to product codes (same as in your original function)
        sanpham_map = {
            'nuoc': 'MUNUOC',
            'tap': 'MUTAP',
            'day': 'MUDAY',
            'dong': 'MUDONG',
            'chen': 'MUCHEN',
        }
        
        created_orders = []
        for (daily_ban, to_id), lines in lines_by_daily_to.items():
            # Find max ngay for date_order
            max_ngay = max(line.ngay for line in lines if line.ngay)
            
            # Get analytic account from to_id
            analytic_account_id = to_id.analytic_account_id.id if to_id and to_id.analytic_account_id else False
            
            # Create sale order
            sale_order_vals = {
                'partner_id': daily_ban.id,
                'date_order': max_ngay,
                'commitment_date': max_ngay,
                'expected_date': max_ngay,
                'analytic_account_id': analytic_account_id,
                #'user_id': self.env.user.id,
                # Add other sale order fields as needed
            }
            
            sale_order = SaleOrder.create(sale_order_vals)
            created_orders.append(sale_order)
            
            # Create sale order lines
            for line in lines:
                default_code = sanpham_map.get(line.sanpham)
                if not default_code:
                    continue  # Skip if mapping not found
                    
                product = Product.search([('default_code', '=', default_code)], limit=1)
                if not product:
                    continue  # Skip if no matching product
                    
                # Get price using existing method
                price, price_type_code = self._get_rubber_price(line)
                
                # Create order line based on price type
                if price_type_code == 'giamutap':
                    SaleOrderLine.create({
                        'order_id': sale_order.id,
                        'product_id': product.id,
                        'product_uom_qty': line.soluongtt,
                        'price_unit': price,
                        'commitment_date': line.ngay,
                    })
                else:
                    SaleOrderLine.create({
                        'order_id': sale_order.id,
                        'product_id': product.id,
                        'sanluong': line.soluongtt,
                        'do': line.dott,
                        'product_uom_qty': line.dott * line.soluongtt / 100,
                        'price_unit': price,
                        'commitment_date': line.ngay,
                    })
                '''debug_line = f"order_line: {product.id}, ' \
                              'sanluong': {line.soluongtt}, ' \
                                'do': {line.dott}, ' \
                              'product_uom_qty': {line.soluongtt}, ' \
                                'commitment_date': {line.ngay}"

                self.debug = (self.debug or '') + debug_line'''
                # Update the rubber.deliver line to mark it as processed
                line.write({
                    'sale_order_id': sale_order.id,
                    'state': 'invoice'  # Change state to 'invoice'
                })
        # After creating sale orders, deselect all processed lines
        selected_lines.write({'is_selected': False})
        # Show the created sale orders
        if not created_orders:
            return {'type': 'ir.actions.act_window_close'}
            
        action = {
            'name': _('Created Sale Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', [order.id for order in created_orders])],
        }
        
        if len(created_orders) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = created_orders[0].id
            
        return action    
        
        
    def _get_rubber_price(self, invoice_line):      
        # Find to_id record where name matches harvest_line.to (char)
        
        domain = [
            ('daily_id', '=', invoice_line.daily_id.id),             
            ('ngay_hieuluc', '<', invoice_line.ngay),
            ('to_id', '=', invoice_line.to_id.id)                      
        ]       
        
        if invoice_line.sanpham == 'nuoc':
            domain.append(('price_type_id.code', '=', 'giamunuoc'))
        elif invoice_line.sanpham == 'tap':
            domain.append('|')
            domain.append(('price_type_id.code', '=', 'giamutap'))
            domain.append(('price_type_id.code', '=', 'giamutap_do'))
        elif invoice_line.sanpham == 'dong':
            domain.append(('price_type_id.code', '=', 'giamudong'))
        elif invoice_line.sanpham == 'day':
            domain.append(('price_type_id.code', '=', 'giamuday'))
        elif invoice_line.sanpham == 'chen':
            domain.append(('price_type_id.code', '=', 'giamuchen'))
        else:
            domain.append(('price_type_id.code', '=', ''))
        # Append domain to debug field            
        price = self.env['rubber.price'].search(domain, limit=1)
        '''debug_line = f"Domain: {domain}, Price: {price.gia if price else 'N/A'}\n"
        self.debug = (self.debug or '') + debug_line'''
        if price:
            if price.price_type_id.code == 'giamutap_do' or price.price_type_id.code == 'giamunuoc':
                return price.gia * 100, price.price_type_id.code
            else:
                return price.gia, price.price_type_id.code
        return 0.0, None
    def action_select_all_invoice_lines(self):
        """Select all invoice lines"""
        lines = self.invoice_xetainha_line_ids + self.invoice_tructiep_line_ids + self.invoice_chomu_line_ids
        lines.write({'is_selected': True})
        return True

    def action_deselect_all_invoice_lines(self):
        """Deselect all invoice lines"""
        lines = self.invoice_xetainha_line_ids + self.invoice_tructiep_line_ids + self.invoice_chomu_line_ids
        lines.write({'is_selected': False})
        return True