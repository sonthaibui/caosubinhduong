from odoo import api, fields, models, _
import calendar
from odoo.exceptions import UserError, ValidationError

class Rubber(models.Model):
    _name = "rubber"
    _description = "Rubber Model"
    _rec_name = 'empname'

    active = fields.Boolean('Active', default=True)
    bymonth = fields.Boolean('By Month', default=True, readonly=False)
    congnuoc = fields.Float('Nước', store=True, compute='_compute_nuoc', digits='One Decimal')
    congtap = fields.Float('Tạp', store=True, compute='_compute_tap', digits='One Decimal')
    cong = fields.Float('Cộng', store=True, compute='_compute_cong', digits='One Decimal')
    do = fields.Float('Độ', default='0', digits='One Decimal', store=True)
    do_phancay = fields.Float('Độ CN', compute='_compute_do_phancay', digits='One Decimal', store=True)
    ghichu = fields.Char('Ghi chú')
    kichthich = fields.Boolean('KT-U', store=True, readonly=False, compute='_compute_kichthich') #Son sua
    ctktup = fields.Many2one('ctkt', string='CT úp', default=lambda self: self._default_ctkt())
    occtktup = fields.Boolean('OC CT úp', default = False, store=True)
    congthuc_kt = fields.Selection(related='rubberbydate_id.congthuc_kt', store=True, readonly=False) #Son them
    lan_kt = fields.Integer('Lần KT', related='rubberbydate_id.lan_kt',store=True, digits='Product Unit of Measure')#son them 23.6.24
    dao_kt = fields.Integer('Dao KT', related='rubberbydate_id.dao_kt',store=True, digits='Product Unit of Measure')
    muday = fields.Float('Dây', default='0', digits='One Decimal')
    mudong = fields.Float('Đông', default='0', digits='One Decimal')
    muchen = fields.Float('Chén', default='0', digits='One Decimal')
    munuoc1 = fields.Float('N1', default='0', digits='One Decimal')
    munuoc2 = fields.Float('N2', default='0', digits='One Decimal')
    munuoc3 = fields.Float('N3', default='0', digits='One Decimal')
    mutap1 = fields.Float('T1', default='0', digits='One Decimal')
    mutap2 = fields.Float('T2', default='0', digits='One Decimal')
    lo = fields.Selection(related='plantation_id.lo', store=True, readonly=False) #Son sua khong lay quan he nua
    ngay = fields.Date('Ngày', related='rubberbydate_id.ngay', store=True, readonly=False) #Son sua khong lay quan he nua
    thang = fields.Char('Tháng', related='rubberbydate_id.thang')
    nam = fields.Char('Năm', related='rubberbydate_id.nam')
    quykho = fields.Float('Quy khô', compute='_compute_quykho', store=True, digits='One Decimal')
    quykho_drc = fields.Float('QK-DRC', compute='_compute_quykho', store=True, digits='One Decimal')        
    dongia_nuoc = fields.Float('Giá nước', digits='Product Price')
    dongia_day = fields.Float('Giá dây', digits='Product Price')
    dongia_dong = fields.Float('Giá đông', digits='Product Price')
    dongia_chen = fields.Float('Giá chén', digits='Product Price')
    dongia_tang = fields.Float('Đơn giá tăng', digits='Product Price')
    tiennuoc = fields.Float('Tiền nước', compute='_compute_tiennuoc', digits='Product Price')
    tienday = fields.Float('Tiền dây', compute='_compute_tienday', digits='Product Price')
    tiendong = fields.Float('Tiền đông', compute='_compute_tiendong', digits='Product Price')
    tienchen = fields.Float('Tiền chén', compute='_compute_tienchen', digits='Product Price')
    phucap = fields.Float('Phụ cấp', digits='Product Price')
    tongtien = fields.Float('Tổng tiền', compute='_compute_tongtien', digits='Product Price')
    rubberbydate_id = fields.Many2one('rubber.date', string='Rubber By Date', ondelete='cascade')
    rubbersalary_id = fields.Many2one('rubber.salary', string='Rubber Salary', ondelete='set null')
    plantation_id = fields.Many2one('plantation', string='Phần cây', ondelete='cascade')
    empname = fields.Char('Tên Công Nhân', compute='_compute_empname', store=True)

    @api.depends('rubbersalary_id.employee_id.name')
    def _compute_empname(self):
        for rec in self:
            rec.empname = rec.rubbersalary_id.employee_id.name or False
    planname = fields.Selection(related='plantation_id.sttcn', store=True)    
    to = fields.Char('Tổ', compute='_compute_to', store=True)

    @api.depends('rubberbydate_id.to', 'rubberbydate_id.to.name')
    def _compute_to(self):
        for rec in self:
            rec.to = rec.rubberbydate_id.to.name if rec.rubberbydate_id.to else False
    miengcao = fields.Char('Miệng cạo', related='rubberbydate_id.miengcao', store=True, readonly=False) #Son them
    thoitiet = fields.Char('Thời tiết', related='rubberbydate_id.thoitiet', store=True, readonly=False) #Son them
    
    mulantruoc = fields.Float('Lần trước', default='0',store=True, digits='Product Unit of Measure')
    chenhlechmu = fields.Float('Mũ +/-', default='0', store=True, digits='Product Unit of Measure')
    chenhlechmu_state = fields.Boolean('CLM', default=True,store=True)
    mudaotruoc = fields.Float('Dao trước', default='0',store=True, digits='Product Unit of Measure')
    chenhlechkho = fields.Float('Khô +/-', default='0',store=True, digits='One Decimal')
    chenhlechkho_state = fields.Boolean('CLK', default=True,store=True)
    daoup = fields.Integer(related='rubberbydate_id.daoup',store=True, digits='Product Unit of Measure')
    nam_kt = fields.Char('Năm khai thác', related='rubberbydate_id.nam_kt')
    tientangdg = fields.Float('Tiền tăng đơn giá', compute='_compute_tientang', digits='Product Price')
    phep = fields.Selection([
        ('ko', 'Ko nghỉ'), ('cp', 'Có phép'), ('kp', 'Ko phép')
    ], string='Nghỉ', default='ko', required=True)
    caoxa = fields.Boolean('Cạo xả', default=True, readonly=True)
    
    @api.depends('ctktup') # Add the appropriate dependencies
    def _compute_kichthich(self):
        for rec in self:
            if rec.ctktup and rec.ctktup.name != "Chưa bôi":
                rec.kichthich = True
            else: rec.kichthich = False
    @api.onchange('ctktup')
    def _onchange_ctktup(self):
        self.occtktup = True            
        return {
            'value': {
                'occtktup': True
            }
        }
    @api.model
    def _default_ctkt(self):
        for rec in self:        
            if rec.rubberbydate_id.ctktup : 
            # phai lay gia tri cuar rubberbydate chu khong cho on change, neu ko thi bi gan Chua boi va phai sua ctktup cua rubberbydate moi tinh lai
                default_ctkt = rec.rubberbydate_id.ctktup
            else:            
                default_ctkt = self.env['ctkt'].search([('name', '=', 'Chưa bôi')], limit=1)
                if not default_ctkt:
                # Create a default ctkt record if none exist
                    default_ctkt = self.env['ctkt'].create({'name': 'Chưa bôi'})        
            return default_ctkt.id if default_ctkt else None
        
    @api.onchange('mutap1')
    def _onchange_mutap1(self):
        for rec in self:
            if rec.mutap1:
                if rec.to == 'TỔ 1' or rec.to == 'TỔ 140' or rec.to == 'TỔ 75':
                    if rec.munuoc1 == 0 and rec.munuoc2 == 0:
                        raise UserError(_("Công nhân " + rec.empname.split('-')[0] + 
                                          " không có mũ nước. Mũ tạp phải nhập qua cột mũ chén. Vui lòng sửa lại trước khi lưu."))

    @api.onchange('phep')
    def _onchange_cophep(self):
        for rec in self:
            rws = self.env['reward'].search([('employee_id','=',rec.rubbersalary_id.employee_id.id),('thang','=',rec.thang),('nam','=',rec.nam)])
            als = self.env['allowance'].search([('employee_id','=',rec.rubbersalary_id.employee_id.id),('thang','=',rec.thang),('nam','=',rec.nam)])
            if len(rws) == 1 and len(als) == 1:
                lp = rec._origin.read(["phep"])[0]["phep"]
                if lp == 'ko':
                    if rec.phep == 'cp':
                        rws[0].cophep += 1
                        als[0].cophep += 1
                    elif rec.phep == 'kp':
                        rws[0].kophep += 1
                        als[0].kophep += 1
                elif lp == 'cp':
                    if rec.phep == 'kp':
                        rws[0].cophep -= 1
                        rws[0].kophep += 1
                        als[0].cophep -= 1
                        als[0].kophep += 1
                    elif rec.phep == 'ko':
                        rws[0].cophep -= 1
                        als[0].cophep -= 1
                elif lp == 'kp':
                    if rec.phep == 'cp':
                        rws[0].cophep += 1
                        rws[0].kophep -= 1
                        als[0].cophep += 1
                        als[0].kophep -= 1
                    elif rec.phep == 'ko':
                        rws[0].kophep -= 1
                        als[0].kophep -= 1

                if rws[0].kophep > 0:
                    rws[0].chuyencan = 0
                elif rws[0].kophep == 0:
                    if rws[0].cophep == 0:
                        rws[0].chuyencan = 200000
                    elif rws[0].cophep == 1:
                        rws[0].chuyencan = 100000
                    elif rws[0].cophep >= 2:
                        rws[0].chuyencan = 0

                if als[0].kophep > 0:
                    als[0].chuyencan = 0
                elif als[0].kophep == 0:
                    if als[0].cophep == 0:
                        als[0].chuyencan = 300000
                    elif als[0].cophep == 1:
                        als[0].chuyencan = 150000
                    elif als[0].cophep >= 2:
                        als[0].chuyencan = 0

                days = calendar.monthrange(int(rws[0].nam), int(rws[0].thang))[1]
                ngaylam = days - rws[0].cophep - rws[0].kophep
                als[0].ngaylam = 'CP: ' + str(als[0].cophep) + ', KP: ' + str(als[0].kophep)
                tien = float(rws[0].diachi)
                if rws[0].cophep <=1 and rws[0].kophep == 0:
                    rws[0].phucloi = tien / days * ngaylam
                    rws[0].pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày' 
                elif rws[0].cophep == 2 and rws[0].kophep == 0:
                    rws[0].phucloi = tien / days * ngaylam * 0.7
                    rws[0].pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 70%'
                elif rws[0].cophep == 3 and rws[0].kophep == 0:
                    rws[0].phucloi = tien / days * ngaylam * 0.5
                    rws[0].pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 50%'
                elif rws[0].cophep == 4 and rws[0].kophep == 0:
                    rws[0].phucloi = tien / days * ngaylam * 0.3
                    rws[0].pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 30%'
                elif rws[0].cophep > 4 or rws[0].kophep > 1:
                    rws[0].phucloi = 0
                elif rws[0].cophep == 0 and rws[0].kophep == 1:
                    rws[0].phucloi = tien / days * ngaylam * 0.5
                    rws[0].pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 50%'
                elif  rws[0].cophep == 1 and rws[0].kophep == 1:
                    rws[0].phucloi = tien / days * ngaylam * 0.4
                    rws[0].pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 40%'
                elif rws[0].cophep == 2 and rws[0].kophep == 1:
                    rws[0].phucloi = tien / days * ngaylam * 0.3
                    rws[0].pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 30%'
            #else:
                #raise UserError(_("Chưa có xét thưởng tháng " + rec.thang + "."))
    
    @api.depends('munuoc1','munuoc2','munuoc3','muday','mudong','muchen')
    def _compute_nuoc(self):
        for rec in self:
            rec.congnuoc = rec.munuoc1 + rec.munuoc2 + rec.munuoc3
            """ if rec.congnuoc > 0:
                if len(rec.env['rubber.deliver'].search([('ngay','=',rec.ngay),('to','=',rec.to),('rubberbydate_id','=',rec.rubberbydate_id.id),('daily','=','Xe tải nhà'),('sanpham','=','nuoc')])) == False:
                    rec.env['rubber.deliver'].create({'rubberbydate_id': rec.rubberbydate_id.id, 'ngay': rec.ngay, 'sanpham': 'nuoc', 'to': rec.to})
            if rec.muday > 0:
                if len(rec.env['rubber.deliver'].search([('ngay','=',rec.ngay),('to','=',rec.to),('rubberbydate_id','=',rec.rubberbydate_id.id),('daily','=','Xe tải nhà'),('sanpham','=','day')])) == False:
                    rec.env['rubber.deliver'].create({'rubberbydate_id': rec.rubberbydate_id.id, 'ngay': rec.ngay, 'sanpham': 'day', 'to': rec.to})
            if rec.mudong > 0:
                if len(rec.env['rubber.deliver'].search([('ngay','=',rec.ngay),('to','=',rec.to),('rubberbydate_id','=',rec.rubberbydate_id.id),('daily','=','Xe tải nhà'),('sanpham','=','dong')])) == False:
                    rec.env['rubber.deliver'].create({'rubberbydate_id': rec.rubberbydate_id.id, 'ngay': rec.ngay, 'sanpham': 'dong', 'to': rec.to})
            if rec.muchen > 0:
                if len(rec.env['rubber.deliver'].search([('ngay','=',rec.ngay),('to','=',rec.to),('rubberbydate_id','=',rec.rubberbydate_id.id),('daily','=','Xe tải nhà'),('sanpham','=','chen')])) == False:
                    rec.env['rubber.deliver'].create({'rubberbydate_id': rec.rubberbydate_id.id, 'ngay': rec.ngay, 'sanpham': 'chen', 'to': rec.to}) """

    @api.onchange('do')
    def _onchange_do(self):
        for rec in self:
            if rec.do > 100:
                raise UserError(_("Độ không được vượt quá 100."))
            elif rec.do < 0:
                raise UserError(_("Độ không được nhỏ hơn 0."))
    
    @api.depends('mutap1','mutap2')
    def _compute_tap(self):
        for rec in self:
            rec.congtap = rec.mutap1 + rec.mutap2
            """ if rec.congtap > 0 and rec.congnuoc > 0:
                if len(rec.env['rubber.deliver'].search([('ngay','=',rec.ngay),('to','=',rec.to),('rubberbydate_id','=',rec.rubberbydate_id.id),('daily','=','Xe tải nhà'),('sanpham','=','tap')])) == False:
                        rec.env['rubber.deliver'].create({'rubberbydate_id': rec.rubberbydate_id.id, 'ngay': rec.ngay, 'sanpham': 'tap', 'to': rec.to})
            if rec.congtap > 0 and rec.to == 'TỔ 140':
                if len(rec.env['rubber.deliver'].search([('ngay','=',rec.ngay),('to','=',rec.to),('rubberbydate_id','=',rec.rubberbydate_id.id),('daily','=','Xe tải nhà'),('sanpham','=','tap')])) == False:
                        rec.env['rubber.deliver'].create({'rubberbydate_id': rec.rubberbydate_id.id, 'ngay': rec.ngay, 'sanpham': 'tap', 'to': rec.to}) """

    @api.depends('congnuoc','congtap')
    def _compute_cong(self):
        for rec in self:
            rec.cong = rec.congnuoc + rec.congtap

    @api.depends('cong','do_phancay')
    def _compute_quykho(self):            
        for rec in self:
            # base khô and DRC
            rec.quykho   = rec.cong * rec.do_phancay / 100
            rec.quykho_drc   = rec.cong * (rec.do_phancay - 3) / 100          

    @api.depends('quykho','dongia_nuoc')
    def _compute_tiennuoc(self):
        for rec in self:
            rec.tiennuoc = rec.quykho * rec.dongia_nuoc

    @api.depends('muday','dongia_day')
    def _compute_tienday(self):
        for rec in self:
            rec.tienday = rec.muday * rec.dongia_day
    
    @api.depends('muchen','dongia_chen')
    def _compute_tienchen(self):
        for rec in self:
            rec.tienchen = rec.muchen * rec.dongia_chen

    @api.depends('mudong','dongia_dong')
    def _compute_tiendong(self):
        for rec in self:
            rec.tiendong = rec.mudong * rec.dongia_dong

    @api.depends('quykho','dongia_tang')
    def _compute_tientang(self):
        for rec in self:
            rec.tientangdg = rec.quykho * rec.dongia_tang

    @api.depends('tiennuoc','tienday','phucap')
    def _compute_tongtien(self):
        for rec in self:
            rec.tongtien = rec.tiennuoc + rec.tienday + rec.phucap + rec.tientangdg + rec.tiendong + rec.tienchen

    @api.depends('do','rubberbydate_id.do_giao','rubberbydate_id.do_tb')
    def _compute_do_phancay(self):
        for rec in self:            
            if rec.do == 0:
                rec.do_phancay = rec.rubberbydate_id.do_giao
            else:
                rec.do_phancay = rec.do + rec.rubberbydate_id.do_giao - rec.rubberbydate_id.do_tb