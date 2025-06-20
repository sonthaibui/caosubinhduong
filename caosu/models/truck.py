from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class RubberTruck(models.Model):
    _name = "rubber.truck"
    _description = "Rubber Truck Model"

    daily = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer', '=', 'True')])
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
    recorded = fields.Boolean('recorded', default=False, compute='_compute_recorded')
    sanpham_id = fields.Many2one('sanpham', string='Sản phẩm')
    all_deliver_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        string='All Delivery Lines'
    )
    delivermu_line_ids = fields.One2many(
        'rubber.deliver', 
        'company_truck_id', 
        string='Delivery Lines',
        compute='_compute_delivermu_line_ids',
        store=True
    )
    deliver_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        string='Nhận mũ nước',
        domain=[
            '|',
            '&', ('daily_name', '=', 'Xe tải nhà'), ('state', 'in', ['giao', 'nhan']),
            '&', ('daily_name', '!=', 'Xe tải nhà'), ('state', '=', 'mua'),
            ('sanpham', '=', 'nuoc')
        ]
    )
    delivertap_line_ids = fields.One2many('rubber.deliver', 'company_truck_id', string='Nhận mũ tạp', domain=[('sanpham','=','tap'),('state','in',['giao','mua','nhan'])])
    deliverday_line_ids = fields.One2many('rubber.deliver', 'company_truck_id', string='Nhận mũ dây', domain=[('sanpham','=','day'),('state','in',['giao','mua','nhan'])])
    deliverdong_line_ids = fields.One2many('rubber.deliver', 'company_truck_id', string='Nhận mũ đông', domain=[('sanpham','=','dong'),('state','in',['giao','mua','nhan'])])
    deliverchen_line_ids = fields.One2many('rubber.deliver', 'company_truck_id', string='Nhận mũ chén', domain=[('sanpham','=','chen'),('state','in',['giao','mua','nhan'])])
    sell_line_ids = fields.One2many('rubber.sell', 'company_truck_id', tracking=True, string='Bán mũ nước', domain=[('sanpham','=','nuoc')])
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
    harvest_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string="Mũ nước xe tải", domain=[('sanpham','=','nuoc'),('rubbersell_id','!=',False)])
    harvesttap_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ tạp xe tải', domain=[('sanpham','=','tap'),('rubbersell_id','!=',False)])
    harvestday_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ dây xe tải', domain=[('sanpham','=','day'),('rubbersell_id','!=',False)])
    harvestdong_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ đông xe tải', domain=[('sanpham','=','dong'),('rubbersell_id','!=',False)])
    harvestchen_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ chén xe tải', domain=[('sanpham','=','chen'),('rubbersell_id','!=',False)])
    harvest1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ nước trực tiếp', domain=[('sanpham','=','nuoc'),('rubbersell_id','=',False)])
    harvesttap1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ tạp trực tiếp', domain=[('sanpham','=','tap'),('rubbersell_id','=',False)])
    harvestday1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ dây trực tiếp', domain=[('sanpham','=','day'),('rubbersell_id','=',False)])
    harvestdong1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ đông trực tiếp', domain=[('sanpham','=','dong'),('rubbersell_id','=',False)])
    harvestchen1_line_ids = fields.One2many('rubber.harvest', 'company_truck_id', string='Mũ chén trực tiếp', domain=[('sanpham','=','chen'),('rubbersell_id','=',False)])
    nhannuoc = fields.Boolean(compute='_compute_nhannuoc', string='Nhận mũ nước xe tải')
    nhantap = fields.Boolean(compute='_compute_nhantap', string='Nhận mũ tạp xe tải')
    nhanday = fields.Boolean(compute='_compute_nhanday', string='Nhận mũ dây xe tải')
    nhandong = fields.Boolean(compute='_compute_nhandong', string='Nhận mũ đông xe tải')
    nhanchen = fields.Boolean(compute='_compute_nhanchen', string='Nhận mũ chén xe tải')
    nhannuoc1 = fields.Boolean(compute='_compute_nhannuoc', string='Nhận mũ nước trực tiếp')
    nhantap1 = fields.Boolean(compute='_compute_nhantap', string='Nhận mũ tạp trực tiếp')
    nhanday1 = fields.Boolean(compute='_compute_nhanday', string='Nhận mũ dây trực tiếp')
    nhandong1 = fields.Boolean(compute='_compute_nhandong', string='Nhận mũ đông trực tiếp')
    nhanchen1 = fields.Boolean(compute='_compute_nhanchen', string='Nhận mũ chén trực tiếp')
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    
    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)

    @api.depends('ngaygiao')
    def _compute_ngay(self):
        for rec in self:
            rec.thang = '01'
            rec.nam = '2024'
            rec.nam_kt = '2024'
            if rec.recorded == True:
                rec.thang = datetime.strptime(str(rec.ngaygiao),'%Y-%m-%d').strftime('%m')
                rec.nam = datetime.strptime(str(rec.ngaygiao),'%Y-%m-%d').strftime('%Y')
                if rec.thang == '01':
                    rec.nam_kt = str(int(rec.nam) - 1)
                else:
                    rec.nam_kt = rec.nam

    @api.depends('ngaygiao', 'sanpham_id', 'all_deliver_line_ids')
    def _compute_delivermu_line_ids(self):
        for truck in self:
            lines = truck.all_deliver_line_ids.filtered(
                lambda l: l.ngay == truck.ngaygiao and
                        (l.soluong != 0 or l.soluongtt != 0) and
                        l.state in ['giao', 'nhan', 'mua'])
            
            if truck.sanpham_id:
                lines = lines.filtered(
                    lambda l: l.sanpham_id == truck.sanpham_id
                )
            else:
                # Sort by daily, then sanpham
                lines = lines.sorted(key=lambda l: (l.daily, l.sanpham_id))
            truck.delivermu_line_ids = lines
        
    def mua_mu(self):
        self.ensure_one()
        if len(self.env['rubber.date'].search([('ngay','=',self.ngaygiao),('to_name', '=', 'TỔ Xe tải')])) == False:
            self.env['rubber.date'].create({'ngay': self.ngaygiao,
                'to': self.env['hr.department'].search([('name', '=', 'TỔ Xe tải')])[0].id,
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
                'default_rubberbydate_id': self.env['rubber.date'].search([('ngay','=',self.ngaygiao),('to_name','=','TỔ Xe tải')])[0].id,
                'default_state': 'mua'})
            }
    
    @api.depends('deliver_line_ids')
    def _compute_nhannuoc(self):
        self.ensure_one()
        self.nhannuoc = False
        self.nhannuoc1 = False
        rbd = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'nuoc'),            
        ])
        
        
        if len(rbd) > 0:
            self.nhannuoc = True
        else:
            self.nhannuoc = False
        rbd1 = self.env['rubber.deliver'].search([
            ('ngay', '=', self.ngaygiao),
            '|',
            ('soluong', '!=', 0),
            ('soluongtt', '!=', 0),
            ('sanpham', '=', 'nuoc'),
            ('state', 'in', ['giao', 'nhan', 'mua'])
        ])
        if len(rbd1) > 0:
            self.nhannuoc1 = True
        else:
            self.nhannuoc1 = False
    
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

    @api.depends('deliver_line_ids','sell_line_ids')
    def _compute_haohut_nuoc(self):
        for rec in self:
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

    def _compute_recorded(self):
        for rec in self:
            rec.recorded = False
            if len(rec.deliver_line_ids) > 0:
                rec.recorded = True
            elif str(rec.id).replace('NewId_', '')[0:2] != "0x":
                if len(self.env['rubber.date'].search([('ngay','=',rec.ngaygiao)])) > 0:
                    rec.recorded = True
                    rds = self.env['rubber.date'].search([('ngay','=',rec.ngaygiao)])
                    for rd in rds:
                        if len(self.env['rubber.deliver'].search([('daily_name','=','Xe tải nhà'),('ngay','=',rd.ngay),('state','in',['giao','nhan'])])) > 0:
                            drs = self.env['rubber.deliver'].search([('daily_name','=','Xe tải nhà'),('ngay','=',rd.ngay),('state','in',['giao','nhan'])])
                            for dr in drs:
                                dr.company_truck_id = rec.id
                                dr.soluongtt = dr.soluong
                                dr.dott = dr.do
                        if len(self.env['rubber.deliver'].search([('to','=','TỔ Xe tải'),('ngay','=',rd.ngay),('state','=','mua')])) > 0:
                            drs = self.env['rubber.deliver'].search([('to','=','TỔ Xe tải'),('ngay','=',rd.ngay),('state','=','mua')])
                            for dr in drs:
                                dr.company_truck_id = rec.id
                        if len(self.env['rubber.deliver'].search([('to','!=','TỔ Xe tải'),('daily_name','!=','Xe tải nhà'),('ngay','=',rd.ngay),('state','in',['giao','nhan'])])) > 0:
                            drs = self.env['rubber.deliver'].search([('to','!=','TỔ Xe tải'),('daily_name','!=','Xe tải nhà'),('ngay','=',rd.ngay),('state','in',['giao','nhan'])])
                            for dr in drs:
                                dr.company_truck_id = rec.id
                                if len(self.env['rubber.harvest'].search([('rubberdeliver_id','=',dr.id)])) > 0:
                                    hrs = self.env['rubber.harvest'].search([('rubberdeliver_id','=',dr.id)])
                                    for hr in hrs:
                                        hr.company_truck_id = rec.id