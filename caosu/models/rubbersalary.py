from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import date
import calendar

class RubberSalary(models.Model):
    _name = "rubber.salary"
    _description = "Rubber Salary"
    _rec_name = 'name'

    to = fields.Many2one('hr.department', required=True, string='Tổ')
    to_name = fields.Char(string='Tên Tổ', related='to.name')
    to_name1 = fields.Char('Tổ Tên', compute='_compute_toname')
    ref = fields.Char('Reference', compute='_compute_ref')
    employee_id = fields.Many2one('hr.employee', string='Công nhân', required=True)
    empname = fields.Char('CN', compute='_compute_empname')
    empname1 = fields.Char('CN1', compute='_compute_empname')
    bymonth = fields.Boolean('By Month', default=False, readonly=False)
    sttcn = fields.Char('STT CN')
    name = fields.Char('name', related='employee_id.name')
    company_id = fields.Many2one('res.company', store=True, copy=False,
        string="Company", default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
        related='company_id.currency_id')
    active = fields.Boolean('Active', default=True)
    startdate = fields.Date('Ngày bắt đầu', required=True,store=True)
    enddate = fields.Date('Ngày kết thúc', required=True,store=True)
    thang = fields.Selection([
        ('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), ('05', '05'), ('06', '06'),
        ('07', '07'), ('08', '08'), ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'),
    ], string='Tháng', default=str(fields.Datetime.now().strftime('%m')), required=True) 
    nam = fields.Selection([
        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
    ], string='Năm', default=str(fields.Datetime.now().year), required=True)
    namkt = fields.Char('Năm khai thác', compute='_compute_plt',store=True)
    thangkt = fields.Char('Tháng khai thác', compute='_compute_plt')
    textthang = fields.Char('Tháng', default='Bảng tính lương tháng')
    textnam = fields.Char('Năm', default='Năm')
    empty = fields.Char('Empty')
    quykho = fields.Float('Tổng quy khô', digits='One Decimal', compute='_compute_khotien')
    tiennuoc = fields.Float('tiennuoc', digits='Product Price', compute='_compute_khotien')
    tienday = fields.Float('tienday', digits='Product Price', compute='_compute_khotien')
    tiendong = fields.Float('tiendong', digits='Product Price', compute='_compute_khotien')
    tienchen = fields.Float('tienchen', digits='Product Price', compute='_compute_khotien')
    phucap1 = fields.Float('phucap1', digits='Product Price', compute='_compute_khotien')
    tongtien = fields.Monetary('Tổng cộng', compute='_compute_khotien')
    rubber_line_ids = fields.One2many(
        'rubber', 'rubbersalary_id',
        compute='_compute_lines', store=False
    )
    reward_line_ids = fields.One2many(
        'reward', 'rubbersalary_id',
        compute='_compute_lines', store=False
    )
    reward_id = fields.Many2one('reward', string='Reward', readonly=True)
    tongtien_reward = fields.Monetary('Tiền thưởng năm', compute='_compute_thuong')
    tienung = fields.Float('Trừ tiền ưng', compute='_compute_phucap', digits='Product Price')
    tiendao = fields.Float('Tiền dao', compute='_compute_phucap', digits='Product Price')
    boithuoc = fields.Float('Bôi thuốc', compute='_compute_phucap', digits='Product Price')
    boikeo = fields.Float('Bôi keo', compute='_compute_phucap', digits='Product Price')
    giacomang = fields.Float('Gia cố máng', compute='_compute_phucap', digits='Product Price')
    chuyencan = fields.Float('Chuyên cần', compute='_compute_phucap', digits='Product Price')
    thuongsl = fields.Float('Thưởng sản lượng', compute='_compute_phucap', digits='Product Price')
    ngaylam = fields.Char('Ngày vắng', compute='_compute_phucap')
    phucap = fields.Float('Phụ cấp', compute='_compute_phucap', digits='Product Price')
    quykho1 = fields.Float('Quy khô tương đương 1 phần', compute='_compute_phucap', digits='One Decimal')
    sophan = fields.Float('Số phần', default='1.0', compute='_compute_phucap', digits='One Decimal')
    caochoang = fields.Float('Cạo choàng', compute='_compute_phucap', digits='Product Price')
    duongxau = fields.Float('Đường xấu', compute='_compute_phucap', digits='Product Price')
    dixa = fields.Float('Đi xa', compute='_compute_phucap', digits='Product Price')
    itmu = fields.Float('Ít mũ', compute='_compute_phucap', digits='Product Price')
    ttmang = fields.Float('Thanh toán máng', digits='Product Price', compute='_compute_phucap')
    tienmuon = fields.Float('Trừ tiền mượn', compute='_compute_phucap', digits='Product Price')
    tienbh = fields.Float('Tiền BH', compute='_compute_phucap', digits='Product Price')
    luongthangtruoc = fields.Float('Lương tháng trước', digits='Product Price', compute='_compute_phucap')
    caoxa = fields.Float('Cạo xả', compute='_compute_phucap', digits='Product Price')
    bdgv = fields.Float('Buộc đá, gắn váy', digits='Product Price', compute='_compute_phucap')
    bdgvmu = fields.Float('Buộc đá, gắn váy miệng úp', digits='Product Price', compute='_compute_phucap')
    bddm = fields.Float('Bắn dây dẫn mũ', compute='_compute_phucap', digits='Product Price')
    mmcn = fields.Float('Mở miệng cạo ngửa', compute='_compute_phucap', digits='Product Price')
    mmcu = fields.Float('Mở miệng cạo úp', compute='_compute_phucap', digits='Product Price')
    bkrtgn = fields.Float('Buộc kiềng, rãi tô, gắn nắp', compute='_compute_phucap', digits='Product Price')
    tienphan = fields.Float('Tiền phân', compute='_compute_phucap', digits='Product Price')
    rmdm = fields.Float('Rong mương, đóng máng', compute='_compute_phucap', digits='Product Price')
    rct = fields.Float('Rập cờ, thước', compute='_compute_phucap', digits='Product Price')
    bkrtmn = fields.Float('Buộc kiềng, rãi tô, miệng ngửa', compute='_compute_phucap', digits='Product Price')
    xdn = fields.Float('Xỏ dây nắp', compute='_compute_phucap', digits='Product Price')
    tbm = fields.Float('Tiền bấm máng', compute='_compute_phucap', digits='Product Price')
    chiendo = fields.Float('Chiên độ', compute='_compute_phucap', digits='Product Price')
    tienvattu = fields.Float('Tiền gom tô, nắp kiềng, váy', compute='_compute_phucap', digits='Product Price')
    tienvattu1 = fields.Float('Tiền giữ vật tư (-)', compute='_compute_phucap', digits='Product Price')
    tiencuoinam = fields.Float('Tiền thưởng cuối năm', compute='_compute_phucap', digits='Product Price')
    tiengomto = fields.Float('Tiền giữ gom tô', compute='_compute_phucap', digits='Product Price')
    tamvong = fields.Float('Tầm vong', compute='_compute_phucap', digits='Product Price')
    truidao = fields.Float('Trui dao', compute='_compute_phucap', digits='Product Price')
    bandao = fields.Float('Bán dao', compute='_compute_phucap', digits='Product Price')
    ghichu = fields.Char('Ghi chú', compute='_compute_phucap', digits='Product Price')
    banlinhtinh = fields.Float('Bán vật tư', compute='_compute_phucap', digits='Product Price')
    tientangdg = fields.Float('Tiền tăng đơn giá', compute='_compute_khotien', digits='Product Price')
    ngaycao = fields.Integer('Ngày cạo', compute='_compute_khotien')
    tongtienr = fields.Monetary('Còn lại làm tròn', readonly=True)
    tongluong = fields.Monetary('Tổng lương', readonly=True)
    conlai = fields.Monetary('Còn lại', readonly=True)
    rutbot = fields.Float('Rút bớt', digits='Product Price', compute='_compute_plt')
    ruttt = fields.Float('Rút tiền thưởng', digits='Product Price', compute='_compute_plt')
    dongthem = fields.Float('Đóng thêm', digits='Product Price', compute='_compute_plt')
    # Phuc loi  
    tick = fields.Boolean('Recompute Quy Khô', default=False)

    @api.constrains('employee_id','thang','nam')
    def _check_rubbersalary_unique(self):
        allowancebymonth_counts = self.search_count([('employee_id','=',self.employee_id.id),('thang','=',self.thang),('nam','=',self.nam),('id','!=',self.id)])
        if allowancebymonth_counts > 0:
            raise ValidationError(_("Phiếu lương công nhân" + self.employee_id.name.lower() + " tháng " + self.thang + "/" + self.nam + " đã tồn tại."))

    @api.depends('to')
    def _compute_ref(self):
        for rec in self:
            rec.ref = 'To' + rec.to.name[3:6]

    @api.depends('employee_id','startdate','enddate','thang','nam')
    def _compute_plt(self):
        for rec in self:
            rw = self.env['reward'].search([('employee_id','=',rec.employee_id.id),('nam','=',rec.nam),('thang','=',rec.thang)])            
            rec.rutbot = rw.rutbot
            rec.ruttt = rw.ruttt
            rec.dongthem = rw.dongthem
            if rec.thang == '01':
                rec.namkt = str(int(rec.nam) - 1)
                rec.thangkt = '1'
            else:
                rec.namkt = rec.nam
                rec.thangkt = rec.thang
            

    @api.depends('to')
    def _compute_toname(self):
        for rec in self:
            rec.to_name1 = rec.to.name.replace('TỔ','Tổ')

    @api.depends('employee_id')
    def _compute_sttcn(self):
        plant = self.env['plantation'].search([('to', '=', self.employee_id.id),('lo', '=', 'a')])
        for rec in self:
            rec.sttcn = plant.sttcn

    @api.depends('employee_id')   
    def _compute_empname(self):
        for rec in self:
            rec.empname = rec.employee_id.name.split('-')[0]
            rec.empname1 = rec.employee_id.name.split('-')[0].replace(' ', '_')
                   
    @api.depends('employee_id', 'thang', 'nam', 'to')
    def _compute_phucap(self):
        for rec in self:
            # Search for related allowance records
            als = self.env['allowance'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('thang', '=', rec.thang),
                ('nam', '=', rec.nam),
                ('allowancebymonth_id.department_id', '=', rec.to.id)
            ])
            if als:                
                rec.boithuoc = als[0].boithuoc
                rec.boikeo = als[0].boikeo
                rec.ghichu = als[0].ghichu
                rec.giacomang = als[0].giacomang
                rec.chuyencan = als[0].chuyencan
                rec.thuongsl = als[0].thuong_sl
                rec.ngaylam = als[0].ngaylam
                rec.phucap = als[0].phucap
                rec.sophan = als[0].sophan
                rec.quykho1 = als[0].quykho_drc
                rec.caochoang = als[0].caochoang
                rec.duongxau = als[0].duongxau
                rec.tienvattu = als[0].tienvattu
                rec.tienbh = als[0].tienbh
                rec.itmu = als[0].itmu
                rec.tiencuoinam = als[0].tiencuoinam
                rec.mmcn = als[0].mmcn
                rec.mmcu = als[0].mmcu
                rec.bkrtgn = als[0].bkrtgn
                rec.tienphan = als[0].tienphan
                rec.luongthangtruoc = als[0].luongthangtruoc
                rec.bkrtmn = als[0].bkrtmn
                rec.bdgv = als[0].bdgv
                rec.bdgvmu = als[0].bdgvmu
                rec.rct = als[0].rct
                rec.rmdm = als[0].rmdm
                rec.xdn = als[0].xdn
                rec.ttmang = als[0].ttmang
                rec.caoxa = als[0].caoxa
                rec.bddm = als[0].bddm
                rec.tongluong = rec.tongtien + rec.boithuoc + rec.boikeo + rec.giacomang + rec.chuyencan + rec.thuongsl + rec.phucap + rec.caochoang + rec.duongxau + rec.itmu + rec.tienvattu + rec.mmcn + rec.mmcu + rec.bkrtgn + rec.bkrtmn + rec.rct + rec.rmdm + rec.xdn + rec.ttmang + rec.bddm + rec.caoxa + rec.bdgv + rec.bdgvmu + rec.luongthangtruoc + rec.tienphan + rec.rutbot - rec.dongthem + rec.ruttt
                rec.tienvattu1 = als[0].tienvattu1
                rec.tienung = als[0].tienung + als[0].ungtien 
                rec.tienmuon = als[0].tienmuon
                rec.tiendao = als[0].tiendao
                rec.chiendo = als[0].chiendo
                rec.tiengomto = als[0].tiengomto
                rec.tbm = als[0].tbm
                rec.tamvong = als[0].tamvong
                rec.truidao = als[0].truidao
                rec.bandao = als[0].bandao
                rec.banlinhtinh = als[0].banlinhtinh
                rec.conlai = rec.tongluong - rec.tienvattu1  - rec.tienung - rec.tiendao - rec.chiendo - rec.tiengomto - rec.tbm - rec.tamvong - rec.truidao - rec.bandao - rec.banlinhtinh - rec.tienmuon - rec.tienbh - rec.tiencuoinam
                mod = rec.conlai % 10000
                if mod >= 5000:
                    rec.tongtienr = rec.conlai - mod + 10000
                else:
                    rec.tongtienr = rec.conlai - mod
            else:
                rec.tienung = 0
                rec.tiendao = 0
                rec.boithuoc = 0
                rec.boikeo = 0
                rec.ghichu = ''
                rec.giacomang = 0
                rec.chuyencan = 0
                rec.thuongsl = 0
                rec.ngaylam = ""
                rec.phucap = 0
                rec.sophan = 0
                rec.quykho1 = 0
                rec.caochoang = 0
                rec.duongxau = 0
                rec.itmu = 0
                rec.chiendo = 0
                rec.tienvattu = 0
                rec.tienvattu1 = 0
                rec.tienbh = 0
                rec.tiencuoinam = 0
                rec.tiengomto = 0
                rec.tongtienr = 0
                rec.luongthangtruoc = 0
                rec.mmcn = 0
                rec.mmcu = 0
                rec.bkrtgn = 0
                rec.tienphan = 0
                rec.bkrtmn = 0
                rec.bdgv = 0
                rec.bdgvmu = 0
                rec.ttmang = 0
                rec.caoxa = 0
                rec.tienmuon = 0
                rec.bddm = 0
                rec.rct = 0
                rec.rmdm = 0
                rec.xdn = 0
                rec.tbm = 0
                rec.tamvong = 0
                rec.truidao = 0
                rec.bandao = 0
                rec.banlinhtinh = 0
                rec.tongluong = 0
                rec.conlai = 0

    @api.depends('rubber_line_ids')
    def _compute_khotien(self):
        for rec in self:
            total_quykho = total_tongtien = total_tientangdg = 0.0
            total_tiennuoc = total_tienday = total_tiendong = 0.0
            total_tienchen = total_phucap1 = 0.0
            count_days = 0

            for line in rec.rubber_line_ids:
                total_quykho     += line.quykho
                total_tongtien   += line.tongtien
                total_tientangdg += line.tientangdg
                total_tiennuoc   += line.tiennuoc
                total_tienday    += line.tienday
                total_tiendong   += line.tiendong
                total_tienchen   += line.tienchen
                total_phucap1    += getattr(line, 'phucap1', 0.0)
                count_days       += 1

            rec.quykho     = total_quykho
            rec.tongtien   = total_tongtien
            rec.tientangdg = total_tientangdg
            rec.tiennuoc   = total_tiennuoc
            rec.tienday    = total_tienday
            rec.tiendong   = total_tiendong
            rec.tienchen   = total_tienchen
            rec.phucap1    = total_phucap1
            rec.ngaycao    = count_days

    @api.depends('rubber_line_ids')
    def _compute_thuong(self):
        for rec in self:
            if rec.env['reward'].search([('employee_id','=', rec.name),('thang','=', rec.thang)]):            
                rec.tongtien_reward = rec.env['reward'].search([('employee_id','=', rec.name),('thang','=', rec.thang)]).tongtien_luyke
            else:
                rec.tongtien_reward = 0

    @api.depends('startdate', 'enddate', 'to', 'employee_id', 'thang', 'nam', 'namkt')
    def _compute_lines(self):
        Rubber = self.env['rubber']
        Reward = self.env['reward']
        for rec in self:
            # if missing any key date/employee, set to empty recordsets
            if not (rec.startdate and rec.enddate and rec.to and rec.employee_id and rec.thang and rec.nam):
                rec.rubber_line_ids = Rubber.browse()  # empty recordset
                rec.reward_line_ids = Reward.browse()
                continue

            rubbers = Rubber.search([
                ('rubbersalary_id','=', rec.id),
                ('ngay',      '>=', rec.startdate),
                ('ngay',      '<=', rec.enddate),
                ('rubberbydate_id.to',      '=', rec.to.id),
            ])
            # build your reward domain…
            base_dom = [
                ('employee_id','=', rec.employee_id.id),
                ('rewardbymonth_id.to','=', rec.to.id),
                ('namkt','=', rec.namkt),
            ]
            if rec.thang == '01':
                domain = base_dom
            else:               
                # for months > 01, restrict rewards to thang in [02 .. current thang]
                domain = base_dom + [
                    ('thang', '>', '01'),
                    ('thang', '<=', rec.thang),
                ]
            rewards = Reward.search(domain)
            rec.update({'rubber_line_ids' : rubbers})            
            rec.update({'reward_line_ids' : rewards})

    @api.onchange('thang', 'nam')
    def _onchange_thang_nam(self):
        for rec in self:
            if rec.thang and rec.nam:
                y = int(rec.nam)
                m = int(rec.thang)
                # first day of month
                rec.startdate = date(y, m, 1)
                # last day of month
                last_day = calendar.monthrange(y, m)[1]
                rec.enddate = date(y, m, last_day)

    def write(self, vals):
        res = super(RubberSalary, self).write(vals)
        if 'tick' in vals:
            # Find related reward records and trigger recomputation
            rewards = self.env['reward'].search([('rubbersalary_id', '=', self.id)])
            rewards._compute_quykho()
        return res
