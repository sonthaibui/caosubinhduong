from odoo import api, fields, models, _
import calendar

from odoo.exceptions import UserError

class SalaryOfficeStaff(models.Model):
    _name = "salary.office.staff"
    _description = "Salary Office Staff Model"

    stt = fields.Char('STT')
    employee_id = fields.Many2one('hr.employee', string='Họ và Tên')
    empname = fields.Char('Họ Tên', compute='_compute_empname')
    name = fields.Char('Name', related='employee_id.name')
    to = fields.Many2one('hr.department', string='Tổ', readonly=True)
    toname = fields.Char('Tổ', related='to.name')
    ngaycong = fields.Integer('Ngày công')
    mucluong = fields.Float('Mức lương', digits='Product Price')
    luongthuc = fields.Float('Lương thực nhận', digits='Product Price', compute='_compute_luongthuc')
    trachnhiem = fields.Float('Phụ cấp trách nhiệm', digits='Product Price')
    dixa = fields.Float('Phụ cấp đi xa', digits='Product Price')
    ngaytructet = fields.Integer('Ngày trực tết')
    thuongtructet = fields.Float('Thưởng trực tết', digits='Product Price')
    tongcong = fields.Float('Tổng cộng', digits='Product Price', compute='_compute_tongcong')
    tienung = fields.Float('Trừ tiền ứng', digits='Product Price')
    tienmuon = fields.Float('Trừ tiền mượn', digits='Product Price')
    banvattu = fields.Float('Bán vật tư', digits='Product Price')
    caotn = fields.Float('Cạo thí nghiệm', digits='Product Price')
    laimc = fields.Float('Lái máy cày', digits='Product Price')
    chiendo = fields.Float('Chiên độ', digits='Product Price')
    nhanthuc = fields.Float('Thực nhận', digits='Product Price', compute='_compute_nhanthuc')
    kyten = fields.Char('Ký tên')
    ghichu = fields.Char('Ghi chú')
    thang = fields.Char('Tháng', default=str(fields.Datetime.now().strftime('%m')), required=True)
    nam = fields.Char('Năm', default=str(fields.Datetime.now().year), required=True)
    diachi = fields.Selection(related='employee_id.diachi', string='Địa chỉ')
    cophep = fields.Integer('Nghỉ có phép')
    kophep = fields.Integer('Nghỉ không phép')
    phucloi = fields.Float('Phúc lợi', digits='Product Price')#, compute='_compute_phucloi')
    phucloitn = fields.Float('Phúc lợi TN', digits='Product Price', compute='_compute_phucloitn')
    phucloitl = fields.Float('PL tích lũy', compute='_compute_phucloitl', digits='Product Price')
    phucloitln = fields.Float('PL TL năm', compute='_compute_phucloitl', digits='Product Price')
    rutbot = fields.Float('Rút bớt', digits='Product Price')
    dongthem = fields.Float('Đóng thêm', digits='Product Price')
    #conlai = fields.Float('Còn lại', digits='Product Price', compute='_compute_conlai')
    salaryofficedepartment_id = fields.Many2one('salary.office.department', string='Bảng lương bảo vệ', ondelete='cascade')

    @api.depends('employee_id')
    def _compute_empname(self):
        for rec in self:
            rec.empname = ""
            if rec.employee_id.id != False:
                rec.empname = rec.employee_id.name.replace('-bv', '')#.split('-')[1]

    @api.depends('mucluong', 'ngaycong')
    def _compute_luongthuc(self):
        for rec in self:
            days = calendar.monthrange(int(rec.nam), int(rec.thang))[1]
            rec.luongthuc = rec.mucluong * rec.ngaycong / days

    @api.depends('trachnhiem', 'dixa', 'luongthuc', 'ngaytructet','thuongtructet','caotn')
    def _compute_tongcong(self):
        for rec in self:
            rec.tongcong = rec.trachnhiem + rec.dixa + rec.luongthuc + rec.ngaytructet + rec.thuongtructet + rec.caotn + rec.laimc + rec.chiendo
    
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
    
    @api.depends('phucloi','dixa')
    def _compute_phucloitn(self):
        for rec in self:
            rec.phucloitn = rec.phucloi - rec.dixa

    @api.onchange('rutbot')
    def _onchange_rutbot(self):
        for rec in self:
            if rec.rutbot > rec.phucloitln:
                raise UserError("Không thể rút quá sô tiền phúc lợi năm.")

    @api.depends('thang', 'nam', 'phucloitn')
    def _compute_phucloitl(self):
        for rec in self:
            """ #raise UserError(_(self.env['reward']._fields['thang1'].string))
            conlai = 0
            rwbs = self.env['salary.office.staff'].search([('nam','=',str(int(rec.nam) - 1)),('employee_id','=',rec.employee_id.id)])
            if len(rwbs) > 0:
                #raise UserError(_(len(rwbs)))
                conlai = rwbs[0].conlai """
            pltl = 0
            pltln = 0
            rwbs = self.env['salary.office.staff'].search([('nam','=',str(int(rec.nam) - 1)),('employee_id','=',rec.employee_id.id)])
            if len(rwbs) > 0:
                pltln = rwbs[len(rwbs) - 1].phucloitln
            rws = self.env['salary.office.staff'].search([('nam','=',rec.nam)])
            for rw in rws:
                if rw.employee_id == rec.employee_id:
                    if int(rw.thang) <= int(rec.thang):
                        pltl += rw.phucloitn
                    pltln += rw.phucloitn - rec.rutbot + rec.dongthem
            rec.phucloitl = pltl
            rec.phucloitln = pltln

    @api.depends('tienung', 'tienmuon')
    def _compute_nhanthuc(self):
        for rec in self:
            rec.nhanthuc = 0
            nt = rec.tongcong - rec.tienung - rec.tienmuon - rec.banvattu
            mod = nt % 10000
            if mod >= 5000:
                rec.nhanthuc = nt - mod + 10000
            else:
                rec.nhanthuc = nt - mod