from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Allowance(models.Model):
    _name = "allowance"
    _description = "Allowance Model"

    employee_id = fields.Many2one('hr.employee', string='Công nhân')
    empname = fields.Char('CN', compute='_compute_empname')
    dgta = fields.Float('ĐGT Lô A', digits='Product Price')
    dgtb = fields.Float('ĐGT Lô B', digits='Product Price')
    dgtc = fields.Float('ĐGT Lô C', digits='Product Price')
    bymonth = fields.Boolean('By month', default=True)
    byyear = fields.Boolean('By year', default=False)
    tienung = fields.Float('Tiền ứng 1', digits='Product Price')
    ungtien = fields.Float('Tiền ứng 2', digits='Product Price')
    tienmuon = fields.Float('Tiền mượn', digits='Product Price')
    tiendao = fields.Float('Tiền dao', digits='Product Price')
    boithuoc = fields.Float('Bôi thuốc', digits='Product Price')
    boikeo = fields.Float('Bôi keo', digits='Product Price')
    giacomang = fields.Float('Gia cố máng', digits='Product Price')
    phucap = fields.Float('Phụ cấp', digits='Product Price')
    quykho = fields.Float('Quy khô', compute='_compute_quykho', digits='One Decimal')
    quykho_drc = fields.Float('Quy khô', compute='_compute_quykho_drc', digits='One Decimal')
    quykho_nam = fields.Float('Quy khô năm', digits='Product Price', compute='_compute_quykho')
    thuong_qk = fields.Float('Thưởng quy khô', digits='Product Price')
    thuong_cc = fields.Float('Thưởng chuyên cần', digits='Product Price', compute='_compute_ngaynghi')
    sophan = fields.Float('Số phần', default='1.0', digits='One Decimal')
    caochoang = fields.Float('Cạo choàng', digits='Product Price')
    duongxau = fields.Float('Đường xấu', digits='Product Price')
    itmu = fields.Float('Ít mũ', digits='Product Price')
    chiendo = fields.Float('Chiên độ', digits='Product Price')
    somang = fields.Integer('Số máng')
    giamang = fields.Float('Giá máng', digits='One Decimal')
    tienmang = fields.Float('Tiền máng', digits='Product Price', compute='_compute_mang')
    ttmang = fields.Float('Thanh toán máng', digits='Product Price')
    caoxa = fields.Float('Cạo Xả', digits='One Decimal')
    bddm = fields.Float('Bắn dây dẫn mũ', digits='Product Price')
    bdgv = fields.Float('Buộc đá, gắn váy', digits='Product Price')
    bdgvmu = fields.Float('Buộc đá, gắn váy miệng úp', digits='Product Price')
    tienphan = fields.Float('Tiền phân', digits='Product Price')
    luongthangtruoc = fields.Float('Lương tháng trước', digits='Product Price')
    tienvattu = fields.Float('Tiền gom tô, nắp kiềng, váy', digits='Product Price')
    tienvattu1 = fields.Float('Tiền giữ vật tư(-)', digits='Product Price')
    tienbh = fields.Float('Tiền BH', digits='Product Price')
    tiencuoinam = fields.Float('Tiền gửi xe máy', digits='Product Price')
    tiengomto = fields.Float('Tiền giữ gom tô', digits='Product Price')
    rubbersalary_id = fields.Many2one('rubber.salary', string='Phiếu Lương', ondelete='set null')
    salaryboard_id = fields.Many2one('salary.board', string='Bảng Lương', ondelete='cascade')
    employeebenefit_id = fields.Many2one('employee.benefit', string='Phúc Lợi Nhân Viên', ondelete='cascade')
    allowancebymonth_id = fields.Many2one('allowance.by.month', string='Phụ cấp theo tháng', ondelete='cascade')
    startdate = fields.Date('Ngày bắt đầu', required=True,store=True)
    enddate = fields.Date('Ngày kết thúc', required=True,store=True)
    thang = fields.Char('Tháng')
    nam = fields.Char('Năm')
    sttcn = fields.Char('STT')
    ngaylam = fields.Char('Ngày vắng', compute='_compute_ngaylam')
    ngnghi = fields.Integer('Ngày nghỉ')
    chuyencan = fields.Float('Chuyên cần', digits='Product Price')
    cophep = fields.Integer('Có phép')
    kophep = fields.Integer('Không phép')
    dixa = fields.Float('Đi xa', digits='Product Price')
    mmcn = fields.Float('Mở miệng cạo ngửa', digits='Product Price')
    mmcu = fields.Float('Mở miệng cạo úp', digits='Product Price')
    bkrtgn = fields.Float('Buộc kiềng, rãi tô, gắn nắp', digits='Product Price')
    rmdm = fields.Float('Rong mương, đóng máng', digits='Product Price')
    rct = fields.Float('Rập cờ, thước', digits='Product Price')
    bkrtmn = fields.Float('Buộc kiềng, rãi tô, miệng ngửa', digits='Product Price')
    xdn = fields.Float('Xỏ dây nắp', digits='Product Price')
    tbm = fields.Float('Tiền bấm máng', digits='Product Price')
    rutbot = fields.Float('Rút bớt PL', compute='_compute_rutbot', digits='Product Price')
    dongthem = fields.Float('Đóng thêm', compute='_compute_rutbot', digits='Product Price')
    ruttt = fields.Float('Rút tiền thưởng', compute='_compute_rutbot', digits='Product Price')
    ttth = fields.Float('Tăng/giảm tiền thưởng', compute='_compute_tong', digits='Product Price')
    ltn = fields.Float('Lương thực nhận', compute='_compute_tongluong', digits='Product Price')
    ltn1 = fields.Float('LTN 1 tháng trước', compute='_compute_tongluong', digits='Product Price')
    ltn2 = fields.Float('LTN 2 tháng trước', compute='_compute_tongluong', digits='Product Price')
    nctb = fields.Float('Nhân công trang bị', compute='_compute_tongluong', digits='Product Price')
    tongluong = fields.Float('Tổng lương', compute='_compute_tongluong', digits='Product Price')
    conlai = fields.Float('Còn lại', compute='_compute_tongluong', digits='Product Price')
    kynhan = fields.Char('Ký nhận')
    ghichu = fields.Char('Ghi chú')
    tichcuc = fields.Selection([
        ('1', 'Bình thường'), ('2', 'Tích cực'),('3', 'Rất tích cực')
    ], string='Tích cực', default='2', required=True)
    thuong_tc = fields.Float('Thưởng tích cực')
    ngay_bd = fields.Date('Ngày làm', default=fields.Datetime.now(), required=True)
    songay = fields.Integer('Số ngày làm', compute='_compute_songay')
    thuong_tn = fields.Float('Thưởng thâm niên')
    thuong_dx = fields.Float('Thưởng đi xa')
    thuong_sl = fields.Float('Thưởng sản lượng', digits='Product Price')
    tongthuong = fields.Float('Tổng thưởng', compute='_compute_tongthuong')
    tamvong = fields.Float('Tầm vong', digits='Product Price')
    truidao = fields.Float('Trui dao', digits='Product Price')
    bandao = fields.Float('Bán dao', digits='Product Price')
    banlinhtinh = fields.Float('Bán vật tư', digits='Product Price')
    to500 = fields.Integer('500', compute='_compute_tien')
    to200 = fields.Integer('200', compute='_compute_tien')
    to100 = fields.Integer('100', compute='_compute_tien')
    to50 = fields.Integer('50', compute='_compute_tien')
    to20 = fields.Integer('20', compute='_compute_tien')
    to10 = fields.Integer('10', compute='_compute_tien')
    cophep = fields.Integer('CP', default=0)
    kophep = fields.Integer('KP', default=0)

    @api.onchange('dgta','dgtb','dgtc')
    def _onchange_dgt(self):
        for rec in self:
            if self.env['rubber'].search([('empname', '=', rec.employee_id.name),('thang', '=', rec.thang),('nam', '=', rec.nam)]):
                rbs = self.env['rubber'].search([('empname', '=', rec.employee_id.name)])
                for line in rbs:
                    if line.thang == rec.thang and line.nam == rec.nam:
                        if line.lo == 'a':
                            line.dongia_tang = rec.dgta
                        elif line.lo == 'b':
                            line.dongia_tang = rec.dgtb
                        elif line.lo == 'c':
                            line.dongia_tang = rec.dgtc

    @api.depends('employee_id')   
    def _compute_empname(self):
        for rec in self:
            rec.empname = rec.employee_id.name.split('-')[0]

    @api.depends('employee_id', 'thang', 'nam')   
    def _compute_ngaylam(self):
        for rec in self:
            rec.ngaylam = ""
            cophep = 0
            kophep = 0
            ngaylam = ''
            rbs = self.env['rubber'].search([('empname','=',rec.employee_id.name)])
            for rb in rbs:
                if rb.thang == rec.thang and rb.nam == rec.nam:
                    if rb.phep == 'cp':
                        cophep += 1
                    if rb.phep == 'kp':
                        kophep += 1
            ngaylam = 'CP: ' + str(cophep) + ', KP: ' + str(kophep)
            rec.ngaylam = ngaylam
    
    @api.depends('thang','nam','employee_id')
    def _compute_rutbot(self):
        for rec in self:
            rec.rutbot = 0
            rec.ruttt = 0
            rec.dongthem = 0
            rec.ttth = 0
            rws = self.env['reward'].search([('thang','=',rec.thang),('nam','=',rec.nam),('employee_id','=',rec.employee_id.id)])
            if len(rws) > 0:
                rec.rutbot = rws[0].rutbot
                rec.ruttt = rws[0].ruttt
                rec.dongthem = rws[0].dongthem
                rec.ttth = rws[0].ttth

    @api.depends('somang', 'giamang')
    def _compute_mang(self):
        for rec in self:
            rec.tienmang = rec.somang * rec.giamang

    @api.depends('employee_id','chuyencan','caochoang','thuong_sl','itmu','duongxau','boithuoc','luongthangtruoc','boikeo','giacomang','tiengomto','tienvattu1','tienvattu','xdn','bddm','bkrtmn','bkrtgn','mmcu','mmcn','ttmang','rct','rmdm','bdgv','bdgvmu','tienphan','tienung','ungtien','tiendao','chiendo','tiengomto','tbm','tamvong','truidao','bandao','banlinhtinh','tienmuon','tienbh','rutbot','ruttt','dongthem')
    def _compute_tongluong(self):
        for rec in self:
            rbs = self.env['rubber'].search([('empname','=',rec.employee_id.name)])
            tongluong = 0
            rec.ltn = 0
            rec.ltn1 = 0
            rec.ltn2 = 0
            rec.conlai = 0
            if int(rec.thang) - 1 < 10:
                alw1 = self.env['allowance'].search([('employee_id','=',rec.employee_id.id),('thang','=','0' + str(int(rec.thang) - 1))])
            else:
                alw1 = self.env['allowance'].search([('employee_id','=',rec.employee_id.id),('thang','=',str(int(rec.thang) - 1))])
            if int(rec.thang) - 2 < 10:
                alw2 = self.env['allowance'].search([('employee_id','=',rec.employee_id.id),('thang','=','0' + str(int(rec.thang) - 2))])
            else:
                alw2 = self.env['allowance'].search([('employee_id','=',rec.employee_id.id),('thang','=',str(int(rec.thang) - 2))])
            if len(alw1) == 1:
                rec.ltn1 = alw1[0].ltn
            if len(alw2) == 1:
                rec.ltn2 = alw2[0].ltn
            for rb in rbs:
                if rb.thang == rec.thang and rb.nam == rec.nam:
                    tongluong += rb.tongtien
            rec.ltn = tongluong + rec.chuyencan + rec.caochoang + rec.thuong_sl + rec.itmu + rec.duongxau + rec.boithuoc + rec.luongthangtruoc + rec.phucap
            rec.nctb = rec.bdgvmu + rec.bdgv + rec.rmdm + rec.rct + rec.ttmang + rec.mmcn + rec.mmcu + rec.bkrtgn + rec.bkrtmn + rec.bddm + rec.xdn + rec.tienvattu - rec.tienvattu1 - rec.tiengomto + rec.giacomang + rec.boikeo
            rec.tongluong = rec.ltn + rec.nctb + rec.tienphan
            if rec.tongluong > 0:
                conlai = rec.tongluong - rec.tienung - rec.ungtien - rec.tiendao - rec.chiendo - rec.tbm - rec.tamvong - rec.truidao - rec.bandao - rec.banlinhtinh - rec.tienmuon - rec.tiencuoinam - rec.tienbh + rec.rutbot + rec.ruttt - rec.dongthem
                mod = conlai % 10000
                if mod >= 5000:
                    conlai = conlai - mod + 10000
                else:
                    conlai = conlai - mod
                rec.conlai = conlai

    @api.depends('employee_id')
    def _compute_ngaynghi(self):
        for rec in self:
            rws = self.env['reward'].search([('employee_id','=',rec.employee_id.id)])
            chuyencan = 0
            for rw in rws:
                if rw.nam == rec.nam:
                    chuyencan += rw.chuyencan
            rec.thuong_cc = chuyencan
    
    @api.depends('employee_id', 'sophan')
    def _compute_quykho(self):
        for rec in self:
            rbs = self.env['rubber'].search([('empname','=',rec.employee_id.name)])
            quykho = 0
            quykho_nam = 0
            for rb in rbs:
                if rb.nam == rec.nam and rb.thang == rec.thang:
                    quykho += rb.quykho
                if rb.nam == rec.nam:
                    quykho_nam += rb.quykho
            if rec.sophan > 0:
                rec.quykho = quykho / rec.sophan
                rec.quykho_nam = quykho_nam / rec.sophan
    @api.depends('employee_id')
    def _compute_quykho_drc(self):
        for rec in self:
            rbs = self.env['rubber'].search([('empname','=',rec.employee_id.name)])
            quykho_drc = 0            
            for rb in rbs:
                if rb.nam == rec.nam and rb.thang == rec.thang and rb.to == rec.allowancebymonth_id.department_id.name:
                    quykho_drc += rb.quykho_drc                
            rec.quykho_drc = quykho_drc
                

    @api.depends('ngay_bd')
    def _compute_songay(self):
        for rec in self:
            rec.songay = (fields.Date.today() - rec.ngay_bd).days

    @api.depends('thuong_cc','thuong_qk','thuong_tc','thuong_tn','thuong_dx','thuong_sl')
    def _compute_tongthuong(self):
        for rec in self:
            rec.tongthuong = rec.thuong_cc + rec.thuong_qk + rec.thuong_tc + rec.thuong_tn + rec.thuong_dx + rec.thuong_sl

    @api.depends('conlai')
    def _compute_tien(self):
        for rec in self:
            rec.to500 = int(rec.conlai // 500000)
            rec.to200 = int((rec.conlai % 500000) // 200000)
            rec.to100 = int(((rec.conlai % 500000) % 200000) // 100000)
            rec.to50 = int((((rec.conlai % 500000) % 200000) % 100000) // 50000)
            rec.to20 = int(((((rec.conlai % 500000) % 200000) % 100000) % 50000) // 20000)
            rec.to10 = int((((((rec.conlai % 500000) % 200000) % 100000) % 50000) % 20000) // 10000)
