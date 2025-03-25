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
    # Mu nuoc
    nuoc_thu = fields.Float('Mũ nước cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    nuoc_giao = fields.Float('Mũ nước thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    nuoc_ban = fields.Float('Mũ nước giao xe', store=True, compute='_compute_nuocgiao', tracking=True, digits='One Decimal')
    nuoc_daily = fields.Float('Mũ nước đại lý', store=True, compute='_compute_nuocgiao', tracking=True, digits='One Decimal')
    nuoc_ton = fields.Float('Mũ nước tồn', store=True, compute='_compute_nuocton', digits='One Decimal')
    nuoc_tonkk = fields.Float('Mũ nước tồn kiểm kê', store=True, digits='One Decimal')
    nuocnkk = fields.Date('Ngày KKLK', readonly=True)
    nuockk = fields.Boolean('Kiểm kê')
    nuoc_haohut = fields.Float('Mũ nước hao hụt', store=True, compute='_compute_nuochh', tracking=True, digits='One Decimal')
    nuoc_tlhh = fields.Float('Tỷ lệ nước hao hụt', store=True, compute='_compute_nuochh', tracking=True, digits='One Decimal')
    # Mu tap
    tap_thu = fields.Float('Mũ tạp cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    tap_giao = fields.Float('Mũ tạp thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    tap_ban = fields.Float('Mũ tạp giao xe', store=True, compute='_compute_tapgiao', tracking=True, digits='One Decimal')
    tap_daily = fields.Float('Mũ tạp đại lý', store=True, compute='_compute_tapgiao', tracking=True, digits='One Decimal')
    tap_ton = fields.Float('Mũ tạp tồn', store=True, compute='_compute_tapton', digits='One Decimal')
    tap_tonkk = fields.Float('Mũ nước tồn kiểm kê', store=True, digits='One Decimal')
    tapkk = fields.Boolean('Kiểm kê')
    tapnkk = fields.Date('Ngày KKLK', readonly=True)
    tap_haohut = fields.Float('Mũ tạp hao hụt', store=True, compute='_compute_taphh', tracking=True, digits='One Decimal')
    tap_tlhh = fields.Float('Tỷ lệ tạp hao hụt', store=True, compute='_compute_taphh', tracking=True, digits='One Decimal')
    # Mu day
    day_thu = fields.Float('Mũ dây cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    day_giao = fields.Float('Mũ dây thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    day_ban = fields.Float('Mũ dây giao xe', store=True, compute='_compute_daygiao', tracking=True, digits='One Decimal')
    day_daily = fields.Float('Mũ dây đại lý', store=True, compute='_compute_daygiao', tracking=True, digits='One Decimal')
    day_ton = fields.Float('Mũ dây tồn', store=True, compute='_compute_dayton', digits='One Decimal')
    day_tonkk = fields.Float('Mũ dây tồn kiểm kê', store=True, digits='One Decimal')
    daykk = fields.Boolean('Kiểm kê')
    daynkk = fields.Date('Ngày KKLK', readonly=True)
    day_haohut = fields.Float('Mũ dây hao hụt', store=True, compute='_compute_dayhh', tracking=True, digits='One Decimal')
    day_tlhh = fields.Float('Tỷ lệ dây hao hụt', store=True, compute='_compute_dayhh', tracking=True, digits='One Decimal')
    # Mu dong
    dong_thu = fields.Float('Mũ đông cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    dong_giao = fields.Float('Mũ đông thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    dong_ban = fields.Float('Mũ đông giao xe', store=True, compute='_compute_donggiao', tracking=True, digits='One Decimal')
    dong_daily = fields.Float('Mũ đông đại lý', store=True, compute='_compute_donggiao', tracking=True, digits='One Decimal')
    dong_ton = fields.Float('Mũ đông tồn', store=True, compute='_compute_dongton', digits='One Decimal')
    dong_tonkk = fields.Float('Mũ đông tồn kiểm kê', store=True, digits='One Decimal')
    dongkk = fields.Boolean('Kiểm kê')
    dongnkk = fields.Date('Ngày KKLK', readonly=True)
    dong_haohut = fields.Float('Mũ đông hao hụt', store=True, compute='_compute_donghh', tracking=True, digits='One Decimal')
    dong_tlhh = fields.Float('Tỷ lệ đông hao hụt', store=True, compute='_compute_donghh', tracking=True, digits='One Decimal')
    # Mu chen
    chen_thu = fields.Float('Mũ chén cân CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    chen_giao = fields.Float('Mũ chén thực tế', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    chen_ban = fields.Float('Mũ chén giao xe', store=True, compute='_compute_chengiao', tracking=True, digits='One Decimal')
    chen_daily = fields.Float('Mũ chén đại lý', store=True, compute='_compute_chengiao', tracking=True, digits='One Decimal')
    chen_ton = fields.Float('Mũ chén tồn', store=True, compute='_compute_chenton', digits='One Decimal')
    chen_tonkk = fields.Float('Mũ chén tồn kiểm kê', store=True, digits='One Decimal')
    chenkk = fields.Boolean('Kiểm kê')
    chennkk = fields.Date('Ngày KKLK', readonly=True)
    chen_haohut = fields.Float('Mũ chén hao hụt', store=True, compute='_compute_chenhh', tracking=True, digits='One Decimal')
    chen_tlhh = fields.Float('Tỷ lệ chén hao hụt', store=True, compute='_compute_chenhh', tracking=True, digits='One Decimal')
    #
    do_tb = fields.Float('Độ trung bình CN', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
    do_ban = fields.Float('Độ bán', digits='One Decimal')
    do_giao = fields.Float('Độ thực tế', digits='One Decimal', store=True)
    do_haohut = fields.Float('Độ hao hụt %', store=True, compute='_compute_thu', tracking=True, digits='One Decimal')
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
    quykho = fields.Float('Quy Khô', default='0',store=True, digits='Zero Decimal')
    lan_kt = fields.Integer('Lần kt', default='0',store=True, digits='Product Unit of Measure')
    dao_kt = fields.Integer('Dao kt', default='0',store=True, digits='Product Unit of Measure')
    mulantruoc = fields.Float('Lần trước', default='0',store=True, digits='Product Unit of Measure')
    chenhlechmu = fields.Float('Mũ +/-', default='0',store=True, digits='Product Unit of Measure')
    chenhlechmu_state = fields.Boolean('CLM', default=True,store=True)
    mudaotruoc = fields.Float('Dao trước', default='0',store=True, digits='Product Unit of Measure')
    chenhlechkho = fields.Float('Khô +/-', default='0',store=True, digits='One Decimal')
    chenhlechkho_state = fields.Boolean('CLK', default=True,store=True)
    nam_kt = fields.Char('Năm khai thác', compute='_compute_ngay', store=True)
    dotap = fields.Float('Độ tạp ban đầu', digits='One Decimal', default=35)
    ngaygiao = fields.Date('Ngày giao')
    caoxa = fields.Boolean('Cạo xả', default=False)
    thongbao = fields.Char(compute='_compute_thongbao', string='Thông báo', default='', readonly=True)
    
    @api.depends('nuoc_thu', 'ke', 'mutrangthung', 'do_giao', 'rubber_line_ids')
    def _compute_thongbao(self):
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

    @api.onchange('kichthich')
    def _onchange_kichthich(self):
        for rec in self:
            if rec.recorded == True:
                if len(rec.rubber_line_ids) > 0:
                    for line in rec.rubber_line_ids:
                        line.kichthich = rec.kichthich

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
        for rec in self:
            if rec.recorded == True:
                y = 0
                x = 0
                z = 0
                i = 0
                j = 0
                k = 0
                l = 0
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
                rec.tongmu = x + y
                rec.dong_thu = i
                rec.day_thu = j
                rec.nuoc_giao = y - rec.ke - rec.mutrangthung
                rec.tap_giao = x + rec.ke + rec.mutrangthung + rec.xe
                rec.chen_giao = k - rec.ke - rec.mutrangthung
                rec.dong_giao = i - rec.ke - rec.mutrangthung
                rec.day_giao = j - rec.ke - rec.mutrangthung
                if y > 0:
                    rec.do_tb = z / y
                    rec.do_haohut = rec.do_tb - rec.do_giao

    @api.onchange('nuoc_tonkk','tap_tonkk','day_tonkk','dong_tonkk','chen_tonkk')
    def _onchange_tonkk(self):
        for rec in self:
            if rec.nuoc_tonkk < 0 or rec.tap_tonkk < 0 or rec.day_tonkk < 0 or rec.dong_tonkk < 0 or rec.chen_tonkk < 0:
                raise UserError("Tồn phải lớn hơn hoặc bằng 0. Nhập lại tồn.")
    
    @api.depends('deliver_line_ids')
    def _compute_nuocgiao(self):
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
    def _compute_tapgiao(self):
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
    def _compute_daygiao(self):
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
    def _compute_donggiao(self):
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
    def _compute_chengiao(self):
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

    @api.depends('do_ban','do_giao')
    def _compute_dohaohut(self):
        for rec in self:
            if rec.recorded == True:
                if rec.do_ban == 0:
                    rec.do_haohut = rec.do_giao - rec.do_tb
                else:
                    rec.do_haohut = rec.do_ban - rec.do_tb
    
    @api.depends('nuoc_giao','nuoc_ban','nuoc_daily')
    def _compute_nuocton(self):
        for rec in self:
            if rec.recorded == True:
                rds = rec.env['rubber.date'].search([('ngay','<', rec.ngay),('to_name','=',rec.to_name)])
                rds = rds.sorted(key=lambda r: r.ngay)
                nuoc_ton = 0
                nuockk = False
                nuoc_tonkk = 0
                if len(rds) > 0:
                    nuoc_ton = rds[len(rds) - 1].nuoc_ton
                    nuockk = rds[len(rds) - 1].nuockk
                    nuoc_tonkk = rds[len(rds) - 1].nuoc_tonkk
                if nuockk == True:
                    rec.nuoc_ton = nuoc_tonkk + rec.nuoc_giao - rec.nuoc_ban - rec.nuoc_daily
                else:
                    rec.nuoc_ton = nuoc_ton + rec.nuoc_giao - rec.nuoc_ban - rec.nuoc_daily

    @api.depends('tap_giao','tap_ban','tap_daily')
    def _compute_tapton(self):
        for rec in self:
            if rec.recorded == True:
                rds = rec.env['rubber.date'].search([('ngay','<', rec.ngay),('to_name','=',rec.to_name)])
                rds = rds.sorted(key=lambda r: r.ngay)
                tap_ton = 0
                tapkk = False
                tap_tonkk = 0
                if len(rds) > 0:
                    tap_ton = rds[len(rds) - 1].tap_ton
                    tapkk = rds[len(rds) - 1].tapkk
                    tap_tonkk = rds[len(rds) - 1].tap_tonkk
                if tapkk == True:
                    rec.tap_ton = tap_tonkk + rec.tap_giao - rec.tap_ban - rec.tap_daily
                else:
                    rec.tap_ton = tap_ton + rec.tap_giao - rec.tap_ban - rec.tap_daily

    @api.depends('day_giao','day_ban','day_daily')
    def _compute_dayton(self):
        for rec in self:
            if rec.recorded == True:
                rds = rec.env['rubber.date'].search([('ngay','<', rec.ngay),('to_name','=',rec.to_name)])
                rds = rds.sorted(key=lambda r: r.ngay)
                day_ton = 0
                daykk = False
                day_tonkk = 0
                if len(rds) > 0:
                    day_ton = rds[len(rds) - 1].day_ton
                    daykk = rds[len(rds) - 1].daykk
                    day_tonkk = rds[len(rds) - 1].day_tonkk
                if daykk == True:
                    rec.day_ton = day_tonkk + rec.day_giao - rec.day_ban - rec.day_daily
                else:
                    rec.day_ton = day_ton + rec.day_giao - rec.day_ban - rec.day_daily

    @api.depends('dong_giao','dong_ban','dong_daily')
    def _compute_dongton(self):
        for rec in self:
            if rec.recorded == True:
                rds = rec.env['rubber.date'].search([('ngay','<', rec.ngay),('to_name','=',rec.to_name)])
                rds = rds.sorted(key=lambda r: r.ngay)
                dong_ton = 0
                dongkk = False
                dong_tonkk = 0
                if len(rds) > 0:
                    dong_ton = rds[len(rds) - 1].dong_ton
                    dongkk = rds[len(rds) - 1].dongkk
                    dong_tonkk = rds[len(rds) - 1].dong_tonkk
                if dongkk == True:
                    rec.dong_ton = dong_tonkk + rec.dong_giao - rec.dong_ban - rec.dong_daily
                else:
                    rec.dong_ton = dong_ton + rec.dong_giao - rec.dong_ban - rec.dong_daily

    @api.depends('chen_giao','chen_ban','chen_daily')
    def _compute_chenton(self):
        for rec in self:
            if rec.recorded == True:
                rds = rec.env['rubber.date'].search([('ngay','<', rec.ngay),('to_name','=',rec.to_name)])
                rds = rds.sorted(key=lambda r: r.ngay)
                chen_ton = 0
                chenkk = False
                chen_tonkk = 0
                if len(rds) > 0:
                    chen_ton = rds[len(rds) - 1].chen_ton
                    chenkk = rds[len(rds) - 1].chenkk
                    chen_tonkk = rds[len(rds) - 1].chen_tonkk
                if chenkk == True:
                    rec.chen_ton = chen_tonkk + rec.chen_giao - rec.chen_ban - rec.chen_daily
                else:
                    rec.chen_ton = chen_ton + rec.chen_giao - rec.chen_ban - rec.chen_daily

    @api.depends('nuockk','nuoc_ton','nuoc_tonkk')
    def _compute_nuochh(self):
        for rec in self:
            if rec.recorded == True:
                """ rds = rec.env['rubber.date'].search([('ngay','<', rec.ngay),('to_name','=',rec.to_name)])
                rds = rds.sorted(key=lambda r: r.ngay)
                y = 0
                for x in range(1, 31):
                    if rds[len(rds) - x + 1].nuockk == True:
                        y = x
                        break """
                if rec.nuockk == True:
                    rec.nuoc_haohut = rec.nuoc_ton - rec.nuoc_tonkk
                    rec.nuocnkk = rec.ngay
                else:
                    rec.nuoc_haohut = 0
                    rec.nuockk = False

    @api.depends('tapkk','tap_ton','tap_tonkk')
    def _compute_taphh(self):
        for rec in self:
            if rec.recorded == True:
                if rec.tapkk == True:
                    rec.tap_haohut = rec.tap_ton - rec.tap_tonkk
                    rec.tapnkk = rec.ngay
                else:
                    rec.tap_haohut = 0
                    rec.tapnkk = False

    @api.depends('daykk','day_ton','day_tonkk')
    def _compute_dayhh(self):
        for rec in self:
            if rec.recorded == True:
                if rec.daykk == True:
                    rec.day_haohut = rec.day_ton - rec.day_tonkk
                    rec.daynkk = rec.ngay
                else:
                    rec.day_haohut = 0
                    rec.daynkk = False

    @api.depends('dongkk','dong_ton','dong_tonkk')
    def _compute_donghh(self):
        for rec in self:
            if rec.recorded == True:
                if rec.dongkk == True:
                    rec.dong_haohut = rec.dong_ton - rec.dong_tonkk
                    rec.dongnkk = rec.ngay
                else:
                    rec.dong_haohut = 0
                    rec.dongnkk = 0

    @api.depends('chenkk','chen_ton','chen_tonkk')
    def _compute_chenhh(self):
        for rec in self:
            if rec.recorded == True:
                if rec.chenkk == True:
                    rec.chen_haohut = rec.chen_ton - rec.chen_tonkk
                    rec.chennkk = rec.ngay
                else:
                    rec.chen_haohut = 0
                    rec.chennkk = 0

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