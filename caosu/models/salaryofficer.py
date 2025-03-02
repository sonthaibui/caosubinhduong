from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import calendar

class SalaryOfficer(models.Model):
    _name = 'salary.officer'
    _description = 'Salary Officer Model'

    stt = fields.Char('STT')
    employee_id = fields.Many2one('hr.employee', string='Họ và Tên')
    empname = fields.Char('Họ Tên', compute='_compute_empname')
    name = fields.Char('Name', related='employee_id.name')
    toname = fields.Char('Tổ', related='employee_id.department_id.name')
    ngaycong = fields.Integer('Ngày công')
    lcb = fields.Float('Lương CB', digits='Product Price')
    trachnhiem = fields.Float('Trách nhiệm', digits='Product Price')
    thuongcd = fields.Float('Thưởng chủ động', digits='Product Price')
    xangdt = fields.Float('PC xăng, ĐT', digits='Product Price')
    dixa = fields.Float('PC đi xa', digits='Product Price')
    rxmt = fields.Float('PC rửa xe MT', digits='Product Price')
    tienan = fields.Float('Tiền ăn', digits='Product Price')
    vsb = fields.Float('Tiền VS bồn', digits='Product Price')
    ctn = fields.Float('Cạo TN', digits='Product Price')
    tructet = fields.Float('Trực tết', digits='Product Price')
    ngaytt = fields.Float('Ngày trực tết', digits='Product Price')
    ngayphep = fields.Float('Ngày phép', digits='Product Price')
    tienung = fields.Float('Trừ tiền ứng', digits='Product Price')
    tiengui = fields.Float('Trừ tiền gửi', digits='Product Price')
    tienquy = fields.Float('Tiền quỹ', digits='Product Price')
    tienmuon = fields.Float('Tiền mượn', digits='Product Price')
    thuongtl = fields.Float('Thưởng TL', digits='Product Price')
    thang13 = fields.Float('Tháng 13', digits='Product Price')
    quankho = fields.Float('Tiền quản kho', digits='Product Price')
    tngm = fields.Float('Trách nhiệm giao mũ', digits='Product Price')
    tongcong = fields.Float('Thực nhận', compute='_compute_tongcong', digits='Product Price')  
    kyten = fields.Char('Ký tên')
    ghichu = fields.Char('Ghi chú')
    thang = fields.Char('Tháng')
    nam = fields.Char('Năm')
    company_id = fields.Many2one('res.company', store=True, copy=False,
        string="Company", default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
        related='company_id.currency_id')
    ngayphep_hf = fields.Boolean(default=False)
    ctn_hf = fields.Boolean(default=False)
    tiengui_hf = fields.Boolean(default=False)
    tienquy_hf = fields.Boolean(default=False)    
    thuongtl_hf = fields.Boolean(default=False)
    thang13_hf = fields.Boolean(default=False)
    quankho_hf = fields.Boolean(default=False)
    tong = fields.Float('Tổng cộng', digits='Product Price', compute='_compute_ltn')
    ltn = fields.Float('Lương thực nhận', digits='Product Price', compute='_compute_ltn')
    diachi = fields.Selection(related='employee_id.diachi', string='Địa chỉ')
    cophep = fields.Integer('Nghỉ có phép')
    kophep = fields.Integer('Nghỉ không phép')
    phucloi = fields.Float('Phúc lợi', digits='Product Price')
    tmtt = fields.Float('TM tháng trước', digits='Product Price')
    tmtn = fields.Float('TM tháng này', digits='Product Price')
    tmtr = fields.Float('TM trả', digits='Product Price')
    tmcl = fields.Float('TM còn lại', digits='Product Price')
    salaryofficerbymonth_id = fields.Many2one('salary.officer.by.month', string='Bảng lương văn phòng', ondelete='cascade')
    pltext = fields.Char('Diễn giải PL')
    phucloitl = fields.Float('PL tích lũy', digits='Product Price')#, compute='_compute_phucloitl')
    phucloitln = fields.Float('PL TL năm', digits='Product Price')#, compute='_compute_phucloitl')
    rutbot = fields.Float('Rút bớt', digits='Product Price')
    dongthem = fields.Float('Đóng thêm', digits='Product Price')
    chialai = fields.Float('Chia lãi', digits='Product Price')
    conlai = fields.Float('Còn lại', digits='Product Price', compute='_compute_conlai')
    conlai1 = fields.Float('Còn lại', digits='Product Price', compute='_compute_conlai1')
    gopy = fields.Html('Góp ý')
    now = fields.Date('now', default=fields.Datetime.now())
    tylerut = fields.Float('Tỷ lệ rút', digits='Product Price')
    rutpl = fields.Float('Rút PL 1 lần', compute='_compute_rutpl', digits='Product Price')
    tylerut_hf = fields.Boolean(default=False)
    rutpl_hf = fields.Boolean(default=False)
    
    tong_html = fields.Html(string='Tổng cộng', digits='Product Price', compute='_compute_bold_text')

    @api.depends('tong')
    def _compute_bold_text(self):
        for record in self:
            record.tong_html = f"<b>{record.tong}</b>"
            



    @api.model_create_multi
    def create(self, vals):
        res =  super(SalaryOfficer, self).create(vals)
        res.ngaycong = calendar.monthrange(int(res.nam), int(res.thang))[1]
        sos = self.env['salary.officer'].search([('employee_id','=',res.employee_id.id)])
        if len(sos) > 0:
            sos = sos.sorted(key=lambda s: s.id)
            res.trachnhiem = sos[len(sos) - 2].trachnhiem
            res.thuongcd = sos[len(sos) - 2].thuongcd
            res.xangdt = sos[len(sos) - 2].xangdt
            res.dixa = sos[len(sos) - 2].dixa
            res.rxmt = sos[len(sos) - 2].rxmt
            res.tienan = sos[len(sos) - 2].tienan
            res.vsb = sos[len(sos) - 2].vsb
            res.quankho = sos[len(sos) - 2].quankho
            res.tngm = sos[len(sos) - 2].tngm
        return res

    @api.onchange('rutbot')
    def _onchange_rutbot(self):
        for rec in self:
            if rec.rutbot > rec.phucloitln:
                raise UserError("Không thể rút quá sô tiền phúc lợi năm.")

    '''@api.depends('thang', 'nam', 'phucloi')
    def _compute_phucloitl(self):
        for rec in self:
            conlai = 0
            rwbs = self.env['salary.officer'].search([('nam','=',str(int(rec.nam) - 1)),('employee_id','=',rec.employee_id.id)])
            if len(rwbs) > 0:
                conlai = rwbs[0].conlai
            rws = self.env['salary.officer'].search([('nam','=',rec.nam)])
            pltl = 0
            pltln = 0
            for rw in rws:
                if rw.employee_id == rec.employee_id:
                    if int(rw.thang) <= int(rec.thang):
                        pltl += rw.phucloi
                    pltln += rw.phucloi
            rec.phucloitl = pltl
            rec.phucloitln = pltln + conlai'''

    @api.depends('phucloitl','rutbot','dongthem','chialai','tylerut')
    def _compute_conlai(self):
        for rec in self:
            rec.conlai = 0
            if rec.tylerut > 0:
                rec.conlai = 0
            else:
                rec.conlai = rec.phucloitl - rec.rutbot + rec.dongthem - rec.chialai
            rws = self.env['salary.officer'].search([('employee_id','=',rec.employee_id.id)])
            if len(rws) > 0:
                for rw in rws:
                    rw.conlai = rec.conlai

    @api.depends('phucloitl','rutbot','dongthem','chialai','tylerut')
    def _compute_conlai1(self):
        for rec in self:
            rec.conlai1 = 0
            if rec.tylerut > 0:
                rec.conlai1 = 0
            else:
                rec.conlai1 = rec.phucloitl - rec.rutbot + rec.dongthem - rec.chialai

    @api.depends('employee_id')
    def _compute_empname(self):
        for rec in self:
            rec.empname = rec.employee_id.name.replace('-vp', '')

    @api.onchange('cophep','kophep')
    def _onchange_phep(self):
        for rec in self:
            rec.phucloi = 0
            days = calendar.monthrange(int(rec.nam), int(rec.thang))[1]
            ngaylam = days - rec.cophep - rec.kophep
            tien = float(rec.diachi)
            if rec.cophep <=1 and rec.kophep == 0:
                rec.phucloi = tien / days * ngaylam
            elif rec.cophep == 2 and rec.kophep == 0:
                rec.phucloi = tien / days * ngaylam * 0.7
            elif rec.cophep == 3 and rec.kophep == 0:
                rec.phucloi = tien / days * ngaylam * 0.5
            elif rec.cophep == 4 and rec.kophep == 0:
                rec.phucloi = tien / days * ngaylam * 0.3
            elif rec.cophep > 4 or rec.kophep > 1:
                rec.phucloi = 0
            elif rec.cophep == 0 and rec.kophep == 1:
                rec.phucloi = tien / days * ngaylam * 0.5
            elif  rec.cophep == 1 and rec.kophep == 1:
                rec.phucloi = tien / days * ngaylam * 0.4
            elif rec.cophep == 2 and rec.kophep == 1:
                rec.phucloi = tien / days * ngaylam * 0.3

    @api.depends('tylerut','phucloitl')
    def _compute_rutpl(self):
        for rec in self:
            rec.rutpl = 0
            rec.rutpl = rec.tylerut * rec.phucloitl

    @api.depends('lcb','trachnhiem','xangdt','dixa','rxmt','tienan','vsb','thang','ngaycong','nam','quankho','tngm','thuongcd','tructet')
    def _compute_ltn(self):
        for rec in self:
            rec.tong = 0
            rec.ltn = 0
            days = calendar.monthrange(int(rec.nam), int(rec.thang))[1]
            rec.tong = rec.lcb + rec.trachnhiem + rec.xangdt + rec.dixa + rec.thuongcd + rec.rxmt + rec.tienan + rec.vsb + rec.quankho + rec.tngm
            rec.ltn = rec.tong * rec.ngaycong / days
    
    @api.depends('ltn','ctn','ngayphep','tienung','tiengui','tienquy','tmtr','thuongtl','thang13','rutpl','rutbot','tienmuon','x_tgrb','x_tgtn','tructet')
    def _compute_tongcong(self):
        for rec in self:
            rec.tongcong = rec.ltn + rec.rutpl + rec.x_tgrb + rec.ctn + rec.ngayphep - rec.tienung - rec.tiengui - rec.tienquy - rec.x_tgtn - rec.tienmuon + rec.thuongtl + rec.thang13 + rec.tructet

class SalaryOfficerByMonth(models.Model):
    _name = 'salary.officer.by.month'
    _description = 'Salary Officer By Month Model'
    _rec_name = "recname"

    thang = fields.Selection([
        ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'),
        ('07', '7'), ('08', '8'), ('09', '9'), ('10', '10'), ('11', '11'), ('12', '12'),
    ], string='Tháng', required=True, default=str(fields.Datetime.now().strftime('%m')))
    nam = fields.Selection([
        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
    ], string='Năm', default=str(fields.Datetime.now().year), required=True)
    recorded = fields.Boolean('recorded', default=False, compute='_compute_recorded')
    recname = fields.Char('recname', compute='_compute_recname')
    company_id = fields.Many2one('res.company', store=True, copy=False,
        string="Company", default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
        related='company_id.currency_id')
    salaryofficer_ids = fields.One2many('salary.officer', 'salaryofficerbymonth_id', string='Lương văn phòng')
    ngayphep_hf = fields.Boolean(default=False)
    ctn_hf = fields.Boolean(default=False)
    tiengui_hf = fields.Boolean(default=False)
    tienquy_hf = fields.Boolean(default=False)
    thuongtl_hf = fields.Boolean(default=False)
    thang13_hf = fields.Boolean(default=False)
    tylerut_hf = fields.Boolean(default=False)
    rutpl_hf = fields.Boolean(default=False)

    @api.constrains('thang','nam')
    def _check_salaryofficedepartment_unique(self):
        salaryofficerbymonth_counts = self.search_count([('thang','=',self.thang),('nam','=',self.nam),('id','!=',self.id)])
        if salaryofficerbymonth_counts > 0:
            raise ValidationError("Bảng lương văn phòng đã tồn tại!")
        
    @api.depends('thang', 'nam')
    def _compute_recname(self):
        for rec in self:
            if rec.recorded == True:
                rec.recname = rec.thang + '/' + rec.nam

    def _compute_recorded(self):
        for rec in self:
            if len(rec.salaryofficer_ids) > 0:
                rec.recorded = True
            elif str(rec.id).replace('NewId_', '')[0:2] != "0x":
                rec.recorded = True
                sos = self.env['salary.officer'].search([('salaryofficerbymonth_id.id','=',rec.id)])
                if len(sos) == 0:
                    emps = self.env['hr.employee'].search([('name', 'like', '-vp')])
                    if len(emps) == 0:
                        raise UserError(rec.to.name + ' không có nhân viên văn phòng.')
                    stt = 0
                    for emp in emps:
                        stt += 1
                        stt_text = ''
                        if stt < 10:
                            stt_text = '0' + str(stt)
                        else:
                            stt_text = str(stt)
                        """ lcb = 0
                        trachnhiem = 0
                        xangdt = 0
                        quankho = 0
                        tienan = 0
                        tngm = 0
                        vsb = 0
                        rxmt = 0
                        dixa = 0 """
                        """ if emp.id == 90:
                            lcb = 7000000
                            tienan = 1500000
                            tngm = 2000000
                            vsb = 1500000
                            rxmt = 900000
                            dixa = 1000000
                        elif emp.id == 96:
                            lcb = 6000000
                            trachnhiem = 2000000
                            xangdt = 1000000
                        elif emp.id == 80:
                            lcb = 9000000
                            trachnhiem = 2000000
                            xangdt = 2000000
                        elif emp.id == 87:
                            lcb = 6000000
                            trachnhiem = 2000000
                            xangdt = 1000000
                            quankho = 1000000
                        elif emp.id == 88:
                            lcb = 6000000
                            trachnhiem = 2000000
                            xangdt = 1000000
                        elif emp.id == 92:
                            lcb = 6000000
                            trachnhiem = 1000000
                            xangdt = 1000000
                        elif emp.id == 82:
                            lcb = 6000000
                            trachnhiem = 2000000
                            xangdt = 1000000 """
                        cophep = 0
                        kophep = 0
                        diachi = emp.diachi
                        phucloi = 0
                        days = calendar.monthrange(int(rec.nam), int(rec.thang))[1]
                        ngaylam = days - cophep - kophep
                        tien = float(diachi)
                        if cophep <=1 and kophep == 0:
                            phucloi = tien / days * ngaylam
                        elif cophep == 2 and kophep == 0:
                            phucloi = tien / days * ngaylam * 0.7
                        elif cophep == 3 and kophep == 0:
                            phucloi = tien / days * ngaylam * 0.5
                        elif cophep == 4 and kophep == 0:
                            phucloi = tien / days * ngaylam * 0.3
                        elif cophep > 4 or kophep > 1:
                            phucloi = 0
                        elif cophep == 0 and kophep == 1:
                            phucloi = tien / days * ngaylam * 0.5
                        elif  cophep == 1 and kophep == 1:
                            phucloi = tien / days * ngaylam * 0.4
                        elif cophep == 2 and kophep == 1:
                            phucloi = tien / days * ngaylam * 0.3
                        self.env['salary.officer'].create({'salaryofficerbymonth_id': rec.id, 'stt': stt_text, 'employee_id': emp.id, 'phucloi': phucloi,
                            'thang': rec.thang, 'nam': rec.nam}) #, 'lcb': lcb, 'tienan': tienan, 'vsb': vsb, 'rxmt': rxmt, 'dixa': dixa, 'tngm': tngm, 'trachnhiem': trachnhiem, 'xangdt': xangdt