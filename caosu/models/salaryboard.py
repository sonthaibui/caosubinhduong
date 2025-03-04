from odoo import api, fields, models, _
from odoo.exceptions import UserError

class SalaryBoard(models.Model):
    _name = 'salary.board'
    _description = 'Salary Board Model'

    department_id = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True, readonly=True)
    ref = fields.Char('Reference', compute='_compute_ref')
    company_id = fields.Many2one('res.company', store=True, copy=False,
        string="Company", default=lambda self: self.env.user.company_id.id)
    currency_id = fields.Many2one('res.currency', string="Currency",
        related='company_id.currency_id')
    name = fields.Char('Name', related='department_id.name')
    thang = fields.Selection([
        ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'),
        ('07', '7'), ('08', '8'), ('09', '9'), ('10', '10'), ('11', '11'), ('12', '12'),
    ], string='Tháng', default=str(fields.Datetime.now().strftime('%m')), required=True)
    nam = fields.Selection([
        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
    ], string='Năm', default=str(fields.Datetime.now().year), required=True)
    allowance_line_ids = fields.One2many('allowance', 'salaryboard_id', string='Phụ cấp', domain=[('bymonth', '=', True)])
    tongcong = fields.Char('Tổng Cộng', compute='_compute_tong')
    tongluong = fields.Monetary('tongluong', compute='_compute_tong', digits='Product Price')
    tienung = fields.Monetary('tienung', compute='_compute_tong', digits='Product Price')
    ungtien = fields.Monetary('tienung', compute='_compute_tong', digits='Product Price')
    tamvong = fields.Monetary('tamvong', compute='_compute_tong', digits='Product Price')
    truidao = fields.Monetary('truidao', compute='_compute_tong', digits='Product Price')
    bandao = fields.Monetary('bandao', compute='_compute_tong', digits='Product Price')
    banlinhtinh = fields.Monetary('banlinhtinh', compute='_compute_tong', digits='Product Price')
    tbm = fields.Monetary('tbmang', compute='_compute_tong', digits='Product Price')
    chiendo = fields.Monetary('chiendo', compute='_compute_tong', digits='Product Price')
    tiendao = fields.Monetary('tiendao', compute='_compute_tong', digits='Product Price')
    rutbot = fields.Monetary('rutbot', compute='_compute_tong', digits='Product Price')
    ruttt = fields.Monetary('ruttt', compute='_compute_tong', digits='Product Price')
    dongthem = fields.Monetary('dongthem', compute='_compute_tong', digits='Product Price')
    ttth = fields.Monetary('ttth', compute='_compute_tong', digits='Product Price')
    nctb = fields.Monetary('nctb', compute='_compute_tong', digits='Product Price')
    tienmuon = fields.Monetary('tienmuon', compute='_compute_tong', digits='Product Price')
    tienphan = fields.Monetary('tienphan', compute='_compute_tong', digits='Product Price')
    conlai = fields.Monetary('conlai', compute='_compute_tong', digits='Product Price')

    @api.depends('department_id')
    def _compute_ref(self):
        for rec in self:
            rec.ref = 'To' + rec.department_id.name[3:6]

    @api.onchange('thang', 'nam')
    def _onchange_thangnam(self):
        if self.thang and self.nam:
            als = self.env['allowance'].search([('employee_id.department_id','=',self.department_id.id)])
            for al in als:
                if al.thang == self.thang and al.nam == self.nam:
                    al.bymonth = True #Hien phu cap nao cung to, cung thang va nam
                else:
                    al.bymonth = False

    @api.depends('allowance_line_ids')
    def _compute_tong(self):
        for rec in self:
            tluong = 0
            tung = 0
            utien = 0
            tvong = 0
            tdao = 0
            bdao = 0
            bltinh = 0
            tbmang = 0
            tmuon = 0
            clai = 0
            cdo = 0
            tidao = 0
            rbot = 0
            rtt = 0
            dthem = 0
            ttt = 0
            nctb = 0
            tphan = 0
            rec.tongcong = ''
            for line in self.allowance_line_ids:
                tluong += line.tongluong
                tung += line.tienung
                utien += line.ungtien
                tvong += line.tamvong
                tdao += line.truidao
                bdao += line.bandao
                tbmang += line.tbm
                tmuon += line.tienmuon
                bltinh += line.banlinhtinh
                cdo += line.chiendo
                tidao += line.tiendao
                rbot += line.rutbot
                rtt += line.ruttt
                dthem += line.dongthem
                ttt += line.ttth
                nctb += line.nctb
                tphan += line.tienphan
                clai += line.conlai
            rec.tongcong = 'Tổng Cộng'
            rec.tongluong = tluong
            rec.tienung = tung
            rec.ungtien = utien
            rec.tamvong = tvong
            rec.truidao = tdao
            rec.bandao = bdao
            rec.banlinhtinh = bltinh
            rec.chiendo = cdo
            rec.tiendao = tidao
            rec.rutbot = rbot
            rec.dongthem = dthem
            rec.ruttt = rtt
            rec.ttth = ttt
            rec.nctb = nctb
            rec.tbm = tbmang
            rec.tienphan = tphan
            rec.tienmuon = tmuon
            rec.conlai = clai
