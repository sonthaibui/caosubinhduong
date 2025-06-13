from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class RubberByDate(models.Model):
    _name = "rubber.date"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Rubber Date Model"
    _rec_name = 'recname'

    active = fields.Boolean('Active', default=True)
    congthuc_kt = fields.Selection([('1', 'CT1'),('2', 'CT2'),('3', 'CT3'),('4', 'CT4'),('5', 'CT5'),('10', 'Nutri')], string="Công thức", default='10')
    ctktup = fields.Many2one('ctkt', string='CT úp', default=lambda self: self._default_ctkt())
    daily_day = fields.Many2one('res.partner', string='Đại lý dây', domain=[('is_customer', '=', 'True')])
    daily_dong = fields.Many2one('res.partner', string='Đại lý đông', domain=[('is_customer', '=', 'True')])
    daily_tap = fields.Many2one('res.partner', string='Đại lý tạp', domain=[('is_customer', '=', 'True')])
    daily_nuoc = fields.Many2one('res.partner', string='Đại lý nước', domain=[('is_customer', '=', 'True')])
    daoup = fields.Integer('Phiên')
    daongua = fields.Char('Dao ngửa')
    ghi_chu = fields.Text('Ghi chú', store=True)
    note = fields.Html('Note')
    ke = fields.Float('Mũ ké', digits='One Decimal')
    xe = fields.Float('Mũ tạp xe', digits='Product Price')
    kt_daoup = fields.Char('Dao kích thích')
    miengcao1 = fields.Char('Miệng cạo 1')
    kt_loai = fields.Char('Công thức KT')
    lo = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C')], string='Lô', default='a', required=True, tracking=True, store=True)
    miengcao = fields.Char('Miệng cạo')
    ngay = fields.Date('Ngày', default=fields.Datetime.now(), required=True, tracking=True, store=True)
    ngay_format = fields.Char(string='Ngày', compute='_compute_ngay_format', store=True)

    @api.depends('ngay')
    def _compute_ngay_format(self):
        for record in self:
            if record.ngay:
                record.ngay_format = datetime.strptime(str(record.ngay), '%Y-%m-%d').strftime('%d . %m')
            else:
                record.ngay_format = ''
    currency_id = fields.Many2one('res.currency', string='Currency', 
        default=lambda self: self.env.company.currency_id)
    # Mu nuoc
    nuoc_thu = fields.Float('Mũ nước cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    nuoc_giao = fields.Float('Mũ nước thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    nuoc_ban = fields.Float('Mũ nước giao xe', store=True, compute='_compute_nuocban', tracking=True, digits='One Decimal')
    nuoc_daily = fields.Float('Mũ nước đại lý', store=True, compute='_compute_nuocban', tracking=True, digits='One Decimal')
    nuoc_ton = fields.Float('Mũ nước tồn', store=True, compute='_compute_nuocton', digits='One Decimal')
    nuoc_tonkk = fields.Float('Mũ nước tồn kiểm kê', store=True, digits='One Decimal')
    nuocnkk = fields.Date('Ngày KKLK', readonly=True)
    nuockk = fields.Boolean('Kiểm kê')
    nuoc_haohut = fields.Float('Mũ nước hao hụt', compute='_compute_haohut', store=True)
    nuoc_tlhh = fields.Float('Tỷ lệ nước hao hụt', store=True, compute='_compute_nuochh', tracking=True, digits='One Decimal')
    nuoc_hhkk = fields.Float('Mũ nước hao hụt kiểm kê', store=True, compute='_compute_nuochh', tracking=True, digits='One Decimal')
    # Mu tap
    tap_thu = fields.Float('Mũ tạp cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    tap_giao = fields.Float('Mũ tạp thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    tap_ban = fields.Float('Mũ tạp giao xe', store=True, compute='_compute_tapban', tracking=True, digits='One Decimal')
    tap_daily = fields.Float('Mũ tạp đại lý', store=True, compute='_compute_tapban', tracking=True, digits='One Decimal')
    tap_ton = fields.Float('Mũ tạp tồn', store=True, compute='_compute_tapton', digits='One Decimal')
    tap_tonkk = fields.Float('Mũ nước tồn kiểm kê', store=True, digits='One Decimal')
    tapkk = fields.Boolean('Kiểm kê')
    tapnkk = fields.Date('Ngày KKLK', readonly=True)
    tap_haohut = fields.Float('Mũ tạp hao hụt', compute='_compute_haohut', store=True)
    tap_tlhh = fields.Float('Tỷ lệ tạp hao hụt', store=True, compute='_compute_taphh', tracking=True, digits='One Decimal')
    tap_hhkk = fields.Float('Mũ tạp hao hụt kiểm kê', store=True, compute='_compute_taphh', tracking=True, digits='One Decimal')
    # Mu day
    day_thu = fields.Float('Mũ dây cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    day_giao = fields.Float('Mũ dây thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    day_ban = fields.Float('Mũ dây giao xe', store=True, compute='_compute_dayban', tracking=True, digits='One Decimal')
    day_daily = fields.Float('Mũ dây đại lý', store=True, compute='_compute_dayban', tracking=True, digits='One Decimal')
    day_ton = fields.Float('Mũ dây tồn', store=True, compute='_compute_dayton', digits='One Decimal')
    day_tonkk = fields.Float('Mũ dây tồn kiểm kê', store=True, digits='One Decimal')
    daykk = fields.Boolean('Kiểm kê')
    daynkk = fields.Date('Ngày KKLK', readonly=True)
    day_haohut = fields.Float('Mũ dây hao hụt', compute='_compute_haohut', store=True)
    day_tlhh = fields.Float('Tỷ lệ dây hao hụt', store=True, compute='_compute_dayhh', tracking=True, digits='One Decimal')
    day_hhkk = fields.Float('Mũ dây hao hụt kiểm kê', store=True, compute='_compute_dayhh', tracking=True, digits='One Decimal')
    # Mu dong
    dong_thu = fields.Float('Mũ đông cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    dong_giao = fields.Float('Mũ đông thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    dong_ban = fields.Float('Mũ đông giao xe', store=True, compute='_compute_dongban', tracking=True, digits='One Decimal')
    dong_daily = fields.Float('Mũ đông đại lý', store=True, compute='_compute_dongban', tracking=True, digits='One Decimal')
    dong_ton = fields.Float('Mũ đông tồn', store=True, compute='_compute_dongton', digits='One Decimal')
    dong_tonkk = fields.Float('Mũ đông tồn kiểm kê', store=True, digits='One Decimal')
    dongkk = fields.Boolean('Kiểm kê')
    dongnkk = fields.Date('Ngày KKLK', readonly=True)
    dong_haohut = fields.Float('Mũ đông hao hụt', compute='_compute_haohut', store=True)
    dong_tlhh = fields.Float('Tỷ lệ đông hao hụt', store=True, compute='_compute_donghh', tracking=True, digits='One Decimal')
    dong_hhkk = fields.Float('Mũ đông hao hụt kiểm kê', store=True, compute='_compute_donghh', tracking=True, digits='One Decimal')
    # Mu chen
    chen_thu = fields.Float('Mũ chén cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    chen_giao = fields.Float('Mũ chén thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    chen_ban = fields.Float('Mũ chén giao xe', store=True, compute='_compute_chenban', tracking=True, digits='One Decimal')
    chen_daily = fields.Float('Mũ chén đại lý', store=True, compute='_compute_chenban', tracking=True, digits='One Decimal')
    chen_ton = fields.Float('Mũ chén tồn', store=True, compute='_compute_chenton', digits='One Decimal')
    chen_tonkk = fields.Float('Mũ chén tồn kiểm kê', store=True, digits='One Decimal')
    chenkk = fields.Boolean('Kiểm kê')
    chennkk = fields.Date('Ngày KKLK', readonly=True)
    chen_haohut = fields.Float('Mũ chén hao hụt', compute='_compute_haohut', store=True)
    chen_tlhh = fields.Float('Tỷ lệ chén hao hụt', store=True, compute='_compute_chenhh', tracking=True, digits='One Decimal')
    chen_hhkk = fields.Float('Mũ chén hao hụt kiểm kê', store=True, compute='_compute_chenhh', tracking=True, digits='One Decimal')
       
    tyle_nuoc_haohut = fields.Html(compute='_compute_tyle_haohut_html', store=False)
    tyle_tap_haohut = fields.Html(compute='_compute_tyle_haohut_html', store=False)
    tyle_day_haohut = fields.Html(compute='_compute_tyle_haohut_html', store=False)
    tyle_dong_haohut = fields.Html(compute='_compute_tyle_haohut_html', store=False)
    tyle_chen_haohut = fields.Html(compute='_compute_tyle_haohut_html', store=False)
    tyle_do_haohut = fields.Html(compute='_compute_tyle_haohut_html', store=False)
    #
    do_tb = fields.Float('Độ CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    do_ban = fields.Float('Độ bán', digits='One Decimal')
    do_giao = fields.Float('Độ thực tế', digits='One Decimal', store=True)
    do_haohut = fields.Float('Độ hao hụt %', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    dolech = fields.Float(
        string="Độ lệch", 
        compute="_compute_dolech", 
        store=True,
        help="Độ lệch giữa độ giao và độ trung bình",
        digits='One Decimal'
    )
     
    do_tap = fields.Float('Độ tạp', compute='_compute_do_mu', store=True)
    do_chen = fields.Float('Độ chén', compute='_compute_do_mu', store=True)
    do_dong = fields.Float('Độ đông', compute='_compute_do_mu', store=True)
    do_day = fields.Float('Độ dây', compute='_compute_do_mu', store=True)
    
    thoitiet = fields.Char('Thời tiết')
    thoigian_cao = fields.Char('Thời gian cạo')
    thoigian_trut = fields.Char('Thời gian trút')
    to = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True)
    to_name = fields.Char(string='Tên Tổ', related='to.name', store=True)
    tongmu = fields.Float('Tổng mũ', store=True, compute='_compute_thu', tracking=True, digits='Product Price')
    mutrangthung = fields.Float('Mũ tráng thùng', digits='One Decimal')
    recname = fields.Char('Rec Name', compute='_compute_recname')
    thang = fields.Char('Tháng', compute='_compute_ngay', store=True)
    nam = fields.Char('Năm', compute='_compute_ngay', store=True)
    rubber_line_ids = fields.One2many('rubber', 'rubberbydate_id', string='Sản lượng CN')
    deliver_line_ids = fields.One2many('rubber.deliver', 'rubberbydate_id', string='Mũ giao', tracking=True)
    kichthich = fields.Boolean('KT', default=False)
    recorded = fields.Boolean('recorded', default=False, compute='_compute_recorded')
    quykho = fields.Float('Quy Khô', compute='_compute_quykho', store=True, digits='Zero Decimal')
    lan_kt = fields.Integer('Lần kt', default='0',store=True, digits='Product Unit of Measure')
    dao_kt = fields.Integer('Dao kt', default='0',store=True, digits='Product Unit of Measure')
    mulantruoc = fields.Float('Lần trước', compute='_compute_mulantruoc', store=True, digits='Product Unit of Measure')
    chenhlechmu = fields.Float('Mũ +/-', compute='_compute_chenhlechmu', store=True, digits='Product Unit of Measure')    
    mudaotruoc = fields.Float('Dao trước', default='0',store=True, digits='Product Unit of Measure')
    chenhlechkho = fields.Float('Khô +/-', compute='_compute_chenhlechkho', store=True)   
    nam_kt = fields.Char('Năm khai thác', compute='_compute_ngay', store=True)
    dotap = fields.Float('Độ tạp ban đầu', digits='One Decimal', default=35)
    ngaygiao = fields.Date('Ngày giao')
    caoxa = fields.Boolean('Cạo xả', default=False)
    thongbao = fields.Char( string='Thông báo', default='', readonly=True) #compute='_compute_thongbao',
    giaday = fields.Monetary('Giá mũ dây', digits='Zero Decimal', compute='_compute_rubber_prices', store=True) #
    gianuoc = fields.Monetary('Giá mũ nước', digits='Zero Decimal', compute='_compute_rubber_prices', store=True) #
    tien = fields.Monetary(
        string="Tiền", 
        compute="_compute_tien", 
        store=True, 
        currency_field='currency_id',
        digits='Product Price'
    )
    giatap = fields.Monetary('Giá mũ tạp', digits='Zero Decimal', compute='_compute_rubber_prices', store=True) #
    giatap_do = fields.Monetary('Giá mũ tạp độ', digits='Zero Decimal', compute='_compute_rubber_prices', store=True) #
    giadong = fields.Monetary('Giá mũ đông', digits='Zero Decimal', compute='_compute_rubber_prices', store=True) #
    giachen = fields.Monetary('Giá mũ chén', digits='Zero Decimal', compute='_compute_rubber_prices', store=True) #
    kholantruoc = fields.Float('Khô lần trước', compute='_compute_kholantruoc', store=True, digits='Product Unit of Measure')
    
    @api.depends('nuoc_thu', 'ke', 'mutrangthung', 'do_giao', 'rubber_line_ids')
    def _compute_thongbao(self):
        # skip during onchange/autosave of rubber_line_ids
        if self.env.context.get('skip_rubberline_compute'):
            return
        self.thongbao = ''
        ke = ''
        mutrangthung = ''
        do_giao = ''

        if self.ke == 0:
            ke = 'Chưa nhập mũ ké. '
        elif self.ke > 0:
            ke = ''

        if self.mutrangthung == 0:
            mutrangthung = 'Chưa nhập mũ tráng thùng. '
        elif self.mutrangthung > 0:
            mutrangthung = ''

        if self.do_giao == 0:
            do_giao = 'Chưa nhập độ thực tế. '
        elif self.do_giao > 0 and self.do_giao <= 100:
            do_giao = ''

        if self.nuoc_thu > 0:
            self.thongbao = ke + mutrangthung + do_giao

    @api.onchange('ke')
    def _onchange_ke(self):
        for rec in self:
            if rec.ke < 0:
                raise UserError(_("Mũ ké không được nhỏ hơn 0."))
            
    @api.onchange('xe')
    def _onchange_xe(self):
        for rec in self:
            if rec.xe < 0:
                raise UserError(_("Mũ tạp xe không được nhỏ hơn 0."))

    @api.onchange('mutrangthung')
    def _onchange_mutrangthung(self):
        for rec in self:
            if rec.mutrangthung < 0:
                raise UserError("Mũ tráng thùng không được nhỏ hơn 0.")

    @api.onchange('do_giao')
    def _onchange_do_giao(self):
        for rec in self:
            if rec.do_giao > 100:
                raise UserError("Độ thực tế không được vượt quá 100.")
            elif rec.do_giao < 0:
                raise UserError("Độ thực tế không được nhỏ hơn 0.")

    @api.onchange('kichthich')
    def _onchange_kichthich(self):
        for rec in self:
            if rec.recorded == True:
                if len(rec.rubber_line_ids) > 0:
                    for line in rec.rubber_line_ids:
                        line.kichthich = rec.kichthich
    
    @api.onchange('nuoc_tonkk','tap_tonkk','day_tonkk','dong_tonkk','chen_tonkk')
    def _onchange_tonkk(self):
        for rec in self:
            if rec.nuoc_tonkk < 0 or rec.tap_tonkk < 0 or rec.day_tonkk < 0 or rec.dong_tonkk < 0 or rec.chen_tonkk < 0:
                raise UserError("Tồn phải lớn hơn hoặc bằng 0. Nhập lại tồn.")
    
    @api.depends('ngay')
    def _compute_ngay(self):
        for rec in self:
            rec.thang = '01'
            rec.nam = '2024'
            rec.nam_kt = '2024'
            if rec.recorded == True:
                rec.thang = datetime.strptime(str(rec.ngay),'%Y-%m-%d').strftime('%m')
                rec.nam = datetime.strptime(str(rec.ngay),'%Y-%m-%d').strftime('%Y')
                if rec.thang == '01':
                    rec.nam_kt = str(int(rec.nam) - 1)
                else:
                    rec.nam_kt = rec.nam

    def _compute_recorded(self):
        for rec in self:
            if len(rec.rubber_line_ids) > 0:
                rec.recorded = True
            elif str(rec.id).replace('NewId_', '')[0:2] != "0x":
                rec.recorded = True
                if rec.to.name != 'TỔ Chung' or rec.to.name != 'TỔ Xe tải':
                    if len(self.env['plantation'].search([('to', '=', rec.to.id),('lo', '=', rec.lo)])) == False:
                        raise UserError(_("Department "  " doesn't have any plantation.")) #+ rec.to.name.upper() + " lot " + rec.lo.upper() +
                    else:
                        plants = self.env['plantation'].search([('to', '=', rec.to.id),('lo', '=', rec.lo)])
                        for plant in plants:
                            """ if plant.active == True and plant.employee_id.name.split('-')[1][-1] != 'a':
                                if self.env['rubber.salary'].search([('employee_id','=',plant.employee_id.id)]).id == False:
                                    self.env['rubber.salary'].create({'to': rec.to.id, 'employee_id': plant.employee_id.id})
                                if self.env['rubber.salary'].search([('employee_id','=',plant.employee_id.id)]):
                                    rs = self.env['rubber.salary'].search([('employee_id','=',plant.employee_id.id)])
                                    self.env['rubber'].create({'rubberbydate_id': rec.id, 'rubbersalary_id': rs.id, 'plantation_id': plant.id}) """
                            if plant.active == True and plant.employee_id.name.split('-')[1][-1] != 'a':
                                if self.env['rubber.salary'].search([('employee_id','=',plant.employee_id.id)]).id == False:
                                    self.env['rubber.salary'].create({'to': rec.to.id, 'employee_id': plant.employee_id.id})
                                if self.env['rubber.salary'].search([('employee_id','=',plant.employee_id.id)]):
                                    rs = self.env['rubber.salary'].search([('employee_id','=',plant.employee_id.id)])
                                    self.env['rubber'].create({'rubberbydate_id': rec.id, 'rubbersalary_id': rs.id, 'plantation_id': plant.id})

    @api.depends('to','ngay')
    def _compute_recname(self):
        for rec in self:
            if rec.recorded == True:
                if rec.to and rec.ngay:
                    rec.recname = rec.to.name + ' - ' + datetime.strptime(str(rec.ngay),'%Y-%m-%d').strftime('%d/%m/%Y')

    @api.depends('ke','mutrangthung','caoxa','rubber_line_ids','do_giao','dotap','xe')
    def _compute_thu(self):
        # skip during onchange/autosave of rubber_line_ids
        if self.env.context.get('skip_rubberline_compute'):
            return
        for rec in self:
            if rec.recorded == True:
                y = x = z = i = j = k = l = 0
                for line in rec.rubber_line_ids:
                    line.cong = line.munuoc1 + line.munuoc2 + line.munuoc3 + line.mutap1 + line.mutap2
                    line.caoxa = rec.caoxa
                    if line.congnuoc == 0 and line.muchen > 0:
                        l += line.muchen
                    y += line.congnuoc
                    x += line.congtap
                    z += line.do * line.congnuoc
                    i += line.mudong
                    j += line.muday
                    k += line.muchen
                if rec.caoxa == True:
                    rec.tap_thu = x
                    rec.chen_thu = k
                else:
                    rec.tap_thu = x + l
                    rec.chen_thu = k - l
                rec.nuoc_thu = y
                rec.tongmu = x + y + i + k
                rec.dong_thu = i
                rec.day_thu = j

                rds = rec.env['rubber.date'].search([
                    ('ngay', '<', rec.ngay),
                    ('to_name', '=', rec.to_name)
                ], order='ngay')
                prev_nuoc_ton = rds[-1].nuoc_ton if rds else 0
                prev_tap_ton = rds[-1].tap_ton if rds else 0
                prev_day_ton = rds[-1].day_ton if rds else 0
                prev_dong_ton = rds[-1].dong_ton if rds else 0
                prev_chen_ton = rds[-1].chen_ton if rds else 0

                rec.nuoc_giao = y - rec.ke - rec.mutrangthung + prev_nuoc_ton
                rec.tap_giao = x + rec.ke + rec.mutrangthung + rec.xe + prev_tap_ton
                rec.chen_giao = k - rec.ke - rec.mutrangthung + prev_chen_ton
                rec.dong_giao = i - rec.ke - rec.mutrangthung + prev_dong_ton
                rec.day_giao = j - rec.ke - rec.mutrangthung + prev_day_ton

                if y > 0:
                    rec.do_tb = z / y
                    rec.do_haohut = rec.do_tb - rec.do_giao
    
    #Tinh mu giao
    @api.depends('deliver_line_ids')
    def _compute_nuocban(self):
        for rec in self:
            if rec.recorded == True:
                rec.nuoc_ban = 0
                rec.nuoc_daily = 0
                giaoxe_nuoc = 0
                daily_nuoc = 0
                if len(rec.deliver_line_ids) > 0:
                    for line in rec.deliver_line_ids:
                        if line.daily.name == 'Xe tải nhà' and line.sanpham == 'nuoc':
                            giaoxe_nuoc += line.soluong
                        elif line.daily.name != 'Xe tải nhà' and line.sanpham == 'nuoc':
                            daily_nuoc += line.soluong
                rec.nuoc_ban = giaoxe_nuoc
                rec.nuoc_daily = daily_nuoc

    @api.depends('deliver_line_ids')
    def _compute_tapban(self):
        for rec in self:
            if rec.recorded == True:
                rec.tap_ban = 0
                rec.tap_daily = 0
                giaoxe_tap = 0
                daily_tap = 0
                if len(rec.deliver_line_ids) > 0:
                    for line in rec.deliver_line_ids:
                        if line.daily.name == 'Xe tải nhà' and line.sanpham == 'tap':
                            giaoxe_tap += line.soluong
                        elif line.daily.name != 'Xe tải nhà' and line.sanpham == 'tap':
                            daily_tap += line.soluong
                rec.tap_ban = giaoxe_tap
                rec.tap_daily = daily_tap

    @api.depends('deliver_line_ids')
    def _compute_dayban(self):
        for rec in self:
            if rec.recorded == True:
                rec.day_ban = 0
                rec.day_daily = 0
                giaoxe_day = 0
                daily_day = 0
                if len(rec.deliver_line_ids) > 0:
                    for line in rec.deliver_line_ids:
                        if line.daily.name == 'Xe tải nhà' and line.sanpham == 'day':
                            giaoxe_day += line.soluong
                        elif line.daily.name != 'Xe tải nhà' and line.sanpham == 'day':
                            daily_day += line.soluong
                rec.day_ban = giaoxe_day
                rec.day_daily = daily_day

    @api.depends('deliver_line_ids')
    def _compute_dongban(self):
        for rec in self:
            if rec.recorded == True:
                rec.dong_ban = 0
                rec.dong_daily = 0
                giaoxe_dong = 0
                daily_dong = 0
                if len(rec.deliver_line_ids) > 0:
                    for line in rec.deliver_line_ids:
                        if line.daily.name == 'Xe tải nhà' and line.sanpham == 'dong':
                            giaoxe_dong += line.soluong
                        elif line.daily.name != 'Xe tải nhà' and line.sanpham == 'dong':
                            daily_dong += line.soluong
                rec.dong_ban = giaoxe_dong
                rec.dong_daily = daily_dong

    @api.depends('deliver_line_ids')
    def _compute_chenban(self):
        for rec in self:
            if rec.recorded == True:
                rec.chen_ban = 0
                rec.chen_daily = 0
                giaoxe_chen = 0
                daily_chen = 0
                if len(rec.deliver_line_ids) > 0:
                    for line in rec.deliver_line_ids:
                        if line.daily.name == 'Xe tải nhà' and line.sanpham == 'chen':
                            giaoxe_chen += line.soluong
                        elif line.daily.name != 'Xe tải nhà' and line.sanpham == 'chen':
                            daily_chen += line.soluong
                rec.chen_ban = giaoxe_chen
                rec.chen_daily = daily_chen    
    
    #Tinh mu ton
    @api.depends('nuoc_giao','nuoc_ban','nuoc_daily', 'nuoc_tonkk', 'nuockk', 'nuoc_haohut')
    def _compute_nuocton(self):
        for rec in self:
            if rec.recorded:
                rds = rec.env['rubber.date'].search([
                    ('ngay', '<', rec.ngay),
                    ('to_name', '=', rec.to_name)
                ], order='ngay')
                prev_nuoc_ton = 0
                if rds:
                    prev_nuoc_ton = rds[-1].nuoc_ton
                tyle1, tyle2 = rec.get_tylehaohut('nuoc_haohut', rec.ngay)[:2]
                val = rec.nuoc_haohut / rec.nuoc_giao * 100 if rec.nuoc_giao else 0
                if tyle2 is not None and val < tyle2:
                    rec.nuoc_ton = rec.nuoc_tonkk if rec.nuockk else prev_nuoc_ton
                else:
                    rec.nuoc_ton = rec.nuoc_tonkk if rec.nuockk else prev_nuoc_ton + rec.nuoc_giao - rec.nuoc_ban - rec.nuoc_daily

    @api.depends('tap_giao','tap_ban','tap_daily', 'tap_tonkk', 'tapkk', 'tap_haohut')
    def _compute_tapton(self):
        for rec in self:
            if rec.recorded:
                rds = rec.env['rubber.date'].search([
                    ('ngay', '<', rec.ngay),
                    ('to_name', '=', rec.to_name)
                ], order='ngay')
                prev_tap_ton = 0
                if rds:
                    prev_tap_ton = rds[-1].tap_ton
                tyle1, tyle2 = rec.get_tylehaohut('tap_haohut', rec.ngay)[:2]
                val = rec.tap_haohut / rec.tap_giao * 100 if rec.tap_giao else 0
                if tyle2 is not None and val < tyle2:
                    rec.tap_ton = rec.tap_tonkk if rec.tapkk else prev_tap_ton
                else:
                    rec.tap_ton = rec.tap_tonkk if rec.tapkk else prev_tap_ton + rec.tap_giao - rec.tap_ban - rec.tap_daily

    @api.depends('day_giao','day_ban','day_daily', 'day_tonkk', 'daykk', 'day_haohut')
    def _compute_dayton(self):
        for rec in self:
            if rec.recorded:
                rds = rec.env['rubber.date'].search([
                    ('ngay', '<', rec.ngay),
                    ('to_name', '=', rec.to_name)
                ], order='ngay')
                prev_day_ton = 0
                if rds:
                    prev_day_ton = rds[-1].day_ton
                tyle1, tyle2 = rec.get_tylehaohut('day_haohut', rec.ngay)[:2]
                val = rec.day_haohut / rec.day_giao * 100 if rec.day_giao else 0
                if tyle2 is not None and val < tyle2:
                    rec.day_ton = rec.day_tonkk if rec.daykk else prev_day_ton
                else:
                    rec.day_ton = rec.day_tonkk if rec.daykk else prev_day_ton + rec.day_giao - rec.day_ban - rec.day_daily

    @api.depends('dong_giao','dong_ban','dong_daily', 'dong_tonkk', 'dongkk', 'dong_haohut')
    def _compute_dongton(self):
        for rec in self:
            if rec.recorded:
                rds = rec.env['rubber.date'].search([
                    ('ngay', '<', rec.ngay),
                    ('to_name', '=', rec.to_name)
                ], order='ngay')
                prev_dong_ton = 0
                if rds:
                    prev_dong_ton = rds[-1].dong_ton
                tyle1, tyle2 = rec.get_tylehaohut('dong_haohut', rec.ngay)[:2]
                val = rec.dong_haohut / rec.dong_giao * 100 if rec.dong_giao else 0
                if tyle2 is not None and val < tyle2:
                    rec.dong_ton = rec.dong_tonkk if rec.dongkk else prev_dong_ton
                else:
                    rec.dong_ton = rec.dong_tonkk if rec.dongkk else prev_dong_ton + rec.dong_giao - rec.dong_ban - rec.dong_daily

    @api.depends('chen_giao','chen_ban','chen_daily', 'chen_tonkk', 'chenkk', 'chen_haohut')
    def _compute_chenton(self):
        for rec in self:
            if rec.recorded:
                rds = rec.env['rubber.date'].search([
                    ('ngay', '<', rec.ngay),
                    ('to_name', '=', rec.to_name)
                ], order='ngay')
                prev_chen_ton = 0
                if rds:
                    prev_chen_ton = rds[-1].chen_ton
                tyle1, tyle2 = rec.get_tylehaohut('chen_haohut', rec.ngay)[:2]
                val = rec.chen_haohut / rec.chen_giao * 100 if rec.chen_giao else 0
                if tyle2 is not None and val < tyle2:
                    rec.chen_ton = rec.chen_tonkk if rec.chenkk else prev_chen_ton
                else:
                    rec.chen_ton = rec.chen_tonkk if rec.chenkk else prev_chen_ton + rec.chen_giao - rec.chen_ban - rec.chen_daily

    #Tinh mu hao hut
    @api.depends('nuoc_giao', 'nuoc_ban', 'nuoc_daily',
                 'tap_giao', 'tap_ban', 'tap_daily',
                 'day_giao', 'day_ban', 'day_daily',
                 'dong_giao', 'dong_ban', 'dong_daily',
                 'chen_giao', 'chen_ban', 'chen_daily')
    def _compute_haohut(self):
        for rec in self:
            rec.nuoc_haohut = rec.nuoc_giao - rec.nuoc_ban - rec.nuoc_daily
            rec.tap_haohut = rec.tap_giao - rec.tap_ban - rec.tap_daily
            rec.day_haohut = rec.day_giao - rec.day_ban - rec.day_daily
            rec.dong_haohut = rec.dong_giao - rec.dong_ban - rec.dong_daily
            rec.chen_haohut = rec.chen_giao - rec.chen_ban - rec.chen_daily

    @api.depends('do_ban','do_giao')
    def _compute_dohaohut(self):
        for rec in self:
            if rec.recorded == True:
                if rec.do_ban == 0:
                    rec.do_haohut = rec.do_giao - rec.do_tb
                else:
                    rec.do_haohut = rec.do_ban - rec.do_tb

    #Tinh mu hao hut kiem ke
    @api.depends('nuockk','nuoc_ton','nuoc_tonkk')
    def _compute_nuochh(self):
        for rec in self:
            if rec.recorded == True:

                if rec.nuockk == True:
                    rec.nuoc_hhkk = rec.nuoc_ton - rec.nuoc_tonkk                    
                    rec.nuocnkk = rec.ngay
                else:                   
                    rec.nuoc_hhkk = 0
                    rec.nuockk = False

    @api.depends('tapkk','tap_ton','tap_tonkk')
    def _compute_taphh(self):
        for rec in self:
            if rec.recorded == True:
                if rec.tapkk == True:
                    rec.tap_hhkk = rec.tap_ton - rec.tap_tonkk                    
                    rec.tapnkk = rec.ngay
                else:                    
                    rec.tap_hhkk = 0
                    rec.tapnkk = False

    @api.depends('daykk','day_ton','day_tonkk')
    def _compute_dayhh(self):
        for rec in self:
            if rec.recorded == True:
                if rec.daykk == True:
                    rec.day_hhkk = rec.day_ton - rec.day_tonkk                    
                    rec.daynkk = rec.ngay
                else:                    
                    rec.day_hhkk = 0
                    rec.daynkk = False

    @api.depends('dongkk','dong_ton','dong_tonkk')
    def _compute_donghh(self):
        for rec in self:
            if rec.recorded == True:
                if rec.dongkk == True:
                    rec.dong_hhkk = rec.dong_ton - rec.dong_tonkk                    
                    rec.dongnkk = rec.ngay
                else:                    
                    rec.dong_hhkk = 0
                    rec.dongnkk = 0

    @api.depends('chenkk','chen_ton','chen_tonkk')
    def _compute_chenhh(self):
        for rec in self:
            if rec.recorded == True:
                if rec.chenkk == True:
                    rec.chen_hhkk = rec.chen_ton - rec.chen_tonkk                    
                    rec.chennkk = rec.ngay
                else:                    
                    rec.chen_hhkk = 0
                    rec.chennkk = 0

    @api.depends('do_giao', 'tongmu')
    def _compute_quykho(self):
        for record in self:
            if record.do_giao > 0:
                record.quykho = record.tongmu * (record.do_giao - 3) / 100
            else:
                record.quykho = 0

    @api.depends('do_giao', 'do_tb')
    def _compute_dolech(self):
        for rec in self:
            rec.dolech = rec.do_giao - rec.do_tb

    @api.constrains('to','ngay','lo')
    def _check_rubberdate_unique(self):
        rubberdate_counts = self.search_count([('to','=',self.to.id),('ngay','=',self.ngay),('lo','=',self.lo),('id','!=',self.id)])
        if rubberdate_counts > 0:
            raise ValidationError("Nhập sản lượng " + self.to.name.lower() + " ngày " + str(datetime.strptime(str(self.ngay),'%Y-%m-%d').strftime('%d/%m/%Y')) + " lô " + self.lo.upper() + " đã tồn tại.")
        
    @api.model
    def _default_ctkt(self):
        default_ctkt = self.env['ctkt'].search([('name','=','Chưa bôi')], limit=1)
        if not default_ctkt:
            # Create a default ctkt record if none exist
            default_ctkt = self.env['ctkt'].create({'name': 'Chưa bôi'})
        return default_ctkt.id
    
    @api.onchange('ctktup')
    def _onchange_ctktup(self):
        for line in self.rubber_line_ids:
            if not line.occtktup:
                line.ctktup = self.ctktup

    @api.depends('daily_day', 'daily_nuoc', 'daily_tap', 'daily_dong', 'ngay', 'to')
    def _compute_rubber_prices(self):
        RubberPrice = self.env['rubber.price']
        ProductTemplate = self.env['product.template']
        ResPartner = self.env['res.partner']
        
        # Find the relevant product IDs once
        day_product = ProductTemplate.search([
            '|', ('name', 'ilike', 'mũ dây'), ('name', '=', 'Mũ dây')
        ], limit=1)
        
        nuoc_product = ProductTemplate.search([
            '|', ('name', 'ilike', 'mũ nước'), ('name', '=', 'Mũ nước')
        ], limit=1)
        
        tap_product = ProductTemplate.search([
            '|', ('name', 'ilike', 'mũ tạp'), ('name', '=', 'Mũ tạp')
        ], limit=1)
        
        dong_product = ProductTemplate.search([
            '|', ('name', 'ilike', 'mũ đông'), ('name', '=', 'Mũ đông')
        ], limit=1)
        
        chen_product = ProductTemplate.search([
            '|', ('name', 'ilike', 'mũ chén'), ('name', '=', 'Mũ chén')
        ], limit=1)
        
        # Find the "Đại lý xe tải" partner
        xetai_partner = ResPartner.search([('name', '=', 'Đại lý xe tải')], limit=1)
        
        for rec in self:
            # For mũ dây
            if day_product:
                # Try to find price for the daily_day if available
                if rec.daily_day and rec.to:
                    rec.giaday = RubberPrice.get_price(day_product.id, rec.to.id, rec.daily_day.id, rec.ngay)
                # If no daily_day or price is 0, try using "Đại lý xe tải"
                if not rec.daily_day or rec.giaday == 0:
                    if xetai_partner and rec.to:
                        rec.giaday = RubberPrice.get_price(day_product.id, rec.to.id, xetai_partner.id, rec.ngay)
                    else:
                        rec.giaday = 0
                    
            # For mũ nước
            if nuoc_product:
                # Try to find price for the daily_nuoc if available
                if rec.daily_nuoc and rec.to:
                    rec.gianuoc = RubberPrice.get_price(nuoc_product.id, rec.to.id, rec.daily_nuoc.id, rec.ngay)
                # If no daily_nuoc or price is 0, try using "Đại lý xe tải"
                if not rec.daily_nuoc or rec.gianuoc == 0:
                    if xetai_partner and rec.to:
                        rec.gianuoc = RubberPrice.get_price(nuoc_product.id, rec.to.id, xetai_partner.id, rec.ngay)
                    else:
                        rec.gianuoc = 0
            
            # For mũ tạp
            if tap_product:
                # Try to find price for the daily_tap if available
                if rec.daily_tap and rec.to:
                    rec.giatap = RubberPrice.get_price(tap_product.id, rec.to.id, rec.daily_tap.id, rec.ngay)
                # If no daily_tap or price is 0, try using "Đại lý xe tải"
                if not rec.daily_tap or rec.giatap == 0:
                    if xetai_partner and rec.to:
                        rec.giatap = RubberPrice.get_price(tap_product.id, rec.to.id, xetai_partner.id, rec.ngay)
                    else:
                        rec.giatap = 0
            
            # For mũ đông
            if dong_product:
                # Try to find price for the daily_dong if available
                if rec.daily_dong and rec.to:
                    rec.giadong = RubberPrice.get_price(dong_product.id, rec.to.id, rec.daily_dong.id, rec.ngay)
                # If no daily_dong or price is 0, try using "Đại lý xe tải"
                if not rec.daily_dong or rec.giadong == 0:
                    if xetai_partner and rec.to:
                        rec.giadong = RubberPrice.get_price(dong_product.id, rec.to.id, xetai_partner.id, rec.ngay)
                    else:
                        rec.giadong = 0
            
            # For mũ chén
            if chen_product:
                # Default dealer for mũ chén is usually the same as mũ nước
                dealer_id = rec.daily_nuoc.id if rec.daily_nuoc else None
                
                if dealer_id and rec.to:
                    rec.giachen = RubberPrice.get_price(chen_product.id, rec.to.id, dealer_id, rec.ngay)
                # If no dealer or price is 0, try using "Đại lý xe tải"
                if not dealer_id or rec.giachen == 0:
                    if xetai_partner and rec.to:
                        rec.giachen = RubberPrice.get_price(chen_product.id, rec.to.id, xetai_partner.id, rec.ngay)
                    else:
                        rec.giachen = 0

    @api.depends('to', 'ngay')
    def _compute_do_mu(self):
        DoMu = self.env['do.mu']
        for rec in self:
            do_vals = DoMu.get_do([rec.to.id], rec.ngay)
            rec.do_tap = do_vals.get('do_mutap', 0)
            rec.do_chen = do_vals.get('do_muchen', 0)
            rec.do_dong = do_vals.get('do_mudong', 0)
            rec.do_day = do_vals.get('do_muday', 0)
            
    @api.depends('nuoc_thu', 'day_thu', 'tap_thu', 'dong_thu', 'chen_thu', 
            'gianuoc', 'giaday', 'giadong', 'giachen', 'giatap', 'giatap_do',
            'do_giao', 'do_tb')
    def _compute_tien(self):
        for rec in self:
            # If do_giao is not set, use average degree
            do = rec.do_tb if rec.do_giao == 0 else rec.do_giao
            
            # Calculate money for each rubber type
            money_nuoc = rec.nuoc_ban * do * rec.gianuoc if rec.nuoc_ban != 0 else rec.nuoc_thu * do * rec.gianuoc
            money_chen = rec.chen_ban * do * rec.giachen if rec.chen_ban != 0 else rec.chen_thu * do * rec.giachen
            money_dong = rec.dong_ban * do * rec.giadong if rec.dong_ban != 0 else rec.dong_thu * do * rec.giadong
            money_day = rec.day_ban * rec.giaday if rec.day_ban != 0 else rec.day_thu * rec.giaday  # No percentage for day rubber
            
            # Modified logic for mũ tạp with two different prices
            tap_quantity = rec.tap_ban if rec.tap_ban != 0 else rec.tap_thu
            
            if rec.giatap == 0 and rec.giatap_do != 0:
                money_tap = tap_quantity * do * rec.giatap_do
            elif rec.giatap != 0 and rec.giatap_do == 0:
                money_tap = tap_quantity * rec.giatap
            else:
                money_tap = 0
            
            # Sum all values
            rec.tien = money_nuoc + money_chen + money_tap + money_dong + money_day

    def update_rubber_prices(self):
        """Manually update rubber prices based on the latest price data"""
        for record in self:
            record._compute_rubber_prices()
            record.write({
                'giaday': record.giaday,
                'gianuoc': record.gianuoc,
                'giachen': record.giaday,
                'giadong': record.giadong,
                'giatap': record.giatap,
                'giatap_do': record.giatap_do,
            })

    @api.depends('to_name', 'lo', 'nam_kt', 'ngay', 'thang', 'lan_kt', 'dao_kt')
    def _compute_mulantruoc(self):
        for record in self:
            rbd = self.env['rubber.date'].search([
                ('to_name', '=', record.to_name),
                ('lo', '=', record.lo),
                ('nam_kt', '=', record.nam_kt),
                ('ngay', '<', record.ngay),
                ('lan_kt', '<', record.lan_kt),
                ('dao_kt', '=', record.dao_kt)
            ], order="ngay desc", limit=1)
            
            rbd = rbd.filtered(lambda r: r.thang != "02")
            #rbd = rbd.filtered(lambda r: r.thang != "01") # tháng 1 tính của năm trước
            #rbd = rbd.filtered(lambda r: r.thang != "02") # tháng 2 tính của năm trước
            
            if rbd:  # Không phải dao đầu tiên của năm khai thác
                record.mulantruoc = rbd[0].tongmu
            else:
                record.mulantruoc = 0

    @api.depends('tongmu', 'mulantruoc')
    def _compute_chenhlechmu(self):
        for record in self:
            record.chenhlechmu = record.tongmu - record.mulantruoc

    @api.depends('quykho', 'kholantruoc')
    def _compute_chenhlechkho(self):
        for record in self:
            if record.kholantruoc != 0:
                record.chenhlechkho = (record.quykho - record.kholantruoc) / record.kholantruoc  
            else:
                record.chenhlechkho = 0

    @api.depends('to_name', 'lo', 'nam_kt', 'ngay', 'thang', 'lan_kt', 'dao_kt')
    def _compute_kholantruoc(self):
        for record in self:
            rbd = self.env['rubber.date'].search([
                ('to_name', '=', record.to_name),
                ('lo', '=', record.lo),
                ('nam_kt', '=', record.nam_kt),
                ('ngay', '<', record.ngay),
                ('lan_kt', '<', record.lan_kt),
                ('dao_kt', '=', record.dao_kt)
            ], order="ngay desc", limit=1)
            
            rbd = rbd.filtered(lambda r: r.thang != "02")
            
            if rbd:  # Không phải dao đầu tiên của năm khai thác
                record.kholantruoc = rbd[0].quykho
            else:
                record.kholantruoc = 0

    def recompute_calculated_fields(self):
        """Recompute all calculated fields for selected records"""
        for record in self:
            # Force recomputation of all fields
            record._compute_quykho()
            record._compute_mulantruoc()
            record._compute_kholantruoc()
            record._compute_chenhlechmu()
            record._compute_chenhlechkho()
            
            # Update the database with new values
            record.write({
                'quykho': record.quykho,
                'mulantruoc': record.mulantruoc,
                'kholantruoc': record.kholantruoc,
                'chenhlechmu': record.chenhlechmu,
                'chenhlechkho': record.chenhlechkho
            })
        return True

    @api.model
    def recompute_all_records(self):
        """Recompute calculated fields for all rubber date records"""
        # Process in batches to avoid memory issues
        batch_size = 100
        total = self.search_count([])
        processed = 0
        
        while processed < total:
            records = self.search([], limit=batch_size, offset=processed)
            if not records:
                break
                
            records.recompute_calculated_fields()
            processed += len(records)
            self.env.cr.commit()  # Commit after each batch
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Recomputation Complete'),
                'message': f'Recomputed fields for {processed} records',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def recompute_giao_all(self):
        """Recompute nuoc_giao, tap_giao, day_giao, dong_giao, chen_giao for all records, including previous *_ton"""
        batch_size = 100
        total = self.search_count([])
        processed = 0

        while processed < total:
            records = self.search([], limit=batch_size, offset=processed)
            if not records:
                break
            records._compute_thu()
            processed += len(records)
            self.env.cr.commit()  # Commit after each batch

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Recomputation Complete'),
                'message': f'Recomputed *_giao fields for {processed} records',
                'type': 'success',
                'sticky': False,
            }
        }
    @api.model
    def recompute_haohut_all(self):
        """Recompute *_haohut for all records"""
        batch_size = 100
        total = self.search_count([])
        processed = 0

        while processed < total:
            records = self.search([], limit=batch_size, offset=processed)
            if not records:
                break
            records._compute_haohut()
            processed += len(records)
            self.env.cr.commit()  # Commit after each batch

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Recomputation Complete'),
                'message': f'Recomputed *_haohut fields for {processed} records',
                'type': 'success',
                'sticky': False,
            }
        }

    @api.model
    def recompute_ban_all(self):
        """Recompute *_ban fields for all records"""
        batch_size = 100
        total = self.search_count([])
        processed = 0

        while processed < total:
            records = self.search([], limit=batch_size, offset=processed)
            if not records:
                break
            records._compute_nuocban()
            records._compute_tapban()
            records._compute_dayban()
            records._compute_dongban()
            records._compute_chenban()
            processed += len(records)
            self.env.cr.commit()  # Commit after each batch

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Recomputation Complete'),
                'message': f'Recomputed *_ban fields for {processed} records',
                'type': 'success',
                'sticky': False,
            }
        }
   
    def write(self, vals):
        # skip during onchange/autosave of rubber_line_ids
        if self.env.context.get('skip_rubberline_compute'):
            return
        # Prevent infinite recursion by using a context flag
        if self.env.context.get('skip_nuocton_propagation'):
            return super().write(vals)

        # Store old values before write
        old_values = {}
        kk_fields = [
            ('nuockk', 'nuoc_tonkk', '_compute_nuocton', ['nuockk', 'nuocnkk']),
            ('tapkk', 'tap_tonkk', '_compute_tapton', ['tapkk', 'tapnkk']),
            ('daykk', 'day_tonkk', '_compute_dayton', ['daykk', 'daynkk']),
            ('dongkk', 'dong_tonkk', '_compute_dongton', ['dongkk', 'dongnkk']),
            ('chenkk', 'chen_tonkk', '_compute_chenton', ['chenkk', 'chennkk']),
        ]
        for rec in self:
            old_values[rec.id] = {}
            for field_kk, field_tonkk, _, _ in kk_fields:
                old_values[rec.id][field_kk] = getattr(rec, field_kk)
                old_values[rec.id][field_tonkk] = getattr(rec, field_tonkk)

        res = super().write(vals)

        # Now propagate if value changed
        for field_kk, field_tonkk, compute_method, stop_fields in kk_fields:
            if field_kk in vals or field_tonkk in vals:
                for rec in self:
                    old_kk = old_values[rec.id][field_kk]
                    new_kk = vals.get(field_kk, old_kk)
                    old_tonkk = old_values[rec.id][field_tonkk]
                    new_tonkk = vals.get(field_tonkk, old_tonkk)
                    if old_kk != new_kk or old_tonkk != new_tonkk:
                        later_records = self.env['rubber.date'].search([
                            ('to_name', '=', rec.to_name),
                            ('ngay', '>', rec.ngay)
                        ], order='ngay')
                        for lr in later_records:
                            getattr(lr.with_context(skip_nuocton_propagation=True), compute_method)()
                            if any(getattr(lr, f) for f in stop_fields):
                                break

        return res

    def get_tylehaohut(self, field_code, date):
        """Return the latest tylehaohut1, tylehaohut2, color1, color2, color3 for a field_code and date"""
        rec = self.env['tylehaohut.mu'].search([
            ('field_code', '=', field_code),
            ('date', '<=', date)
        ], order='date desc', limit=1)
        if rec:
            return rec.tylehaohut1, rec.tylehaohut2, rec.color1, rec.color2, rec.color3
        return None, None, None, None, None

    def _compute_tyle_haohut_html(self):
        for rec in self:
            # ĐỘ
            tyle1, tyle2, color1, color2, color3 = rec.get_tylehaohut('do_haohut', rec.ngay)
            val = -rec.dolech / rec.do_tb * 100 if rec.do_tb is not None and rec.do_tb != 0 else 0
            color = ''
            if tyle1 is not None and tyle2 is not None:
                if val < tyle1:
                    color = color1 or 'green'
                elif val < tyle2:
                    color = color2 or 'brown'
                else:
                    color = color3 or 'red'
            rec.tyle_do_haohut = f'<span style="color:{color};">{val:.0f}%</span>'
            # NƯỚC
            tyle1, tyle2, color1, color2, color3 = rec.get_tylehaohut('nuoc_haohut', rec.ngay)
            val = rec.nuoc_haohut / rec.nuoc_giao * 100 if rec.nuoc_giao else 0
            color = ''
            if tyle1 is not None and tyle2 is not None:
                if val < tyle1:
                    color = color1 or 'green'
                elif val < tyle2:
                    color = color2 or 'brown'
                else:
                    color = color3 or 'red'
            rec.tyle_nuoc_haohut = f'<span style="color:{color};">{val:.0f}%</span>'

            # TẠP
            tyle1, tyle2, color1, color2, color3 = rec.get_tylehaohut('tap_haohut', rec.ngay)
            val = rec.tap_haohut / rec.tap_giao * 100 if rec.tap_giao else 0
            color = ''
            if tyle1 is not None and tyle2 is not None:
                if val < tyle1:
                    color = color1 or 'green'
                elif val < tyle2:
                    color = color2 or 'brown'
                else:
                    color = color3 or 'red'
            rec.tyle_tap_haohut = f'<span style="color:{color};">{val:.0f}%</span>'

            # DÂY
            tyle1, tyle2, color1, color2, color3 = rec.get_tylehaohut('day_haohut', rec.ngay)
            val = rec.day_haohut / rec.day_giao * 100 if rec.day_giao else 0
            color = ''
            if tyle1 is not None and tyle2 is not None:
                if val < tyle1:
                    color = color1 or 'green'
                elif val < tyle2:
                    color = color2 or 'brown'
                else:
                    color = color3 or 'red'
            rec.tyle_day_haohut = f'<span style="color:{color};">{val:.0f}%</span>'

            # ĐÔNG
            tyle1, tyle2, color1, color2, color3 = rec.get_tylehaohut('dong_haohut', rec.ngay)
            val = rec.dong_haohut / rec.dong_giao * 100 if rec.dong_giao else 0
            color = ''
            if tyle1 is not None and tyle2 is not None:
                if val < tyle1:
                    color = color1 or 'green'
                elif val < tyle2:
                    color = color2 or 'brown'
                else:
                    color = color3 or 'red'
            rec.tyle_dong_haohut = f'<span style="color:{color};">{val:.0f}%</span>'

            # CHÉN
            tyle1, tyle2, color1, color2, color3 = rec.get_tylehaohut('chen_haohut', rec.ngay)
            val = rec.chen_haohut / rec.chen_giao * 100 if rec.chen_giao else 0
            color = ''
            if tyle1 is not None and tyle2 is not None:
                if val < tyle1:
                    color = color1 or 'green'
                elif val < tyle2:
                    color = color2 or 'brown'
                else:
                    color = color3 or 'red'
            rec.tyle_chen_haohut = f'<span style="color:{color};">{val:.0f}%</span>'

