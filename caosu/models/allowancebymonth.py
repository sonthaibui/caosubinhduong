import calendar
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AllowanceByMonth(models.Model):
    _name = "allowance.by.month"
    _description = "Allowance By Month Model"

    department_id = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True)
    recorded = fields.Boolean('recorded', default=False, compute='_compute_recorded')
    name = fields.Char('name', related='department_id.name')
    thang = fields.Selection([
        ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'),
        ('07', '7'), ('08', '8'), ('09', '9'), ('10', '10'), ('11', '11'), ('12', '12'),
    ], string='Tháng', default=str(fields.Datetime.now().strftime('%m')), required=True)
    nam = fields.Selection([
        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
    ], string='Năm', default=str(fields.Datetime.now().year), required=True)
    dg_nuoc = fields.Float('Đơn giá nước', digits='Product Price')
    dg_tang = fields.Float('Đơn giá tăng', digits='Product Price')
    dg_day = fields.Float('Đơn giá dây', digits='Product Price')
    dg_dong = fields.Float('Đơn giá đông', digits='Product Price')
    dg_chen = fields.Float('Đơn giá chén', digits='Product Price')
    allowance_line_ids = fields.One2many('allowance', 'allowancebymonth_id', string='Phụ cấp')
    thongbao = fields.Char(compute='_compute_thongbao', string='Thông báo')
    
    @api.depends('thang','nam','department_id')
    def _compute_thongbao(self):
        for rec in self:
            rec.thongbao = ""
            if rec.recorded == True:
                rws = rec.env['reward.by.month'].search([('thang','=',rec.thang),('nam','=',rec.nam),('to','=',rec.department_id.id)])
                if len(rws) != 1:
                    rec.thongbao = "BẢNG XÉT THƯỞNG THÁNG " + rec.thang + "/" + rec.nam + " " + rec.department_id.name + " CHƯA TẠO. HÃY TẠO ĐỂ CẬP NHẬT NGÀY PHÉP CÔNG NHÂN."

    @api.model
    def create(self, vals):
        res =  super(AllowanceByMonth, self).create(vals)
        als = self.env['allowance.by.month'].search([('department_id','=',res.department_id.id)])
        als = als.sorted(key=lambda r: r.id)
        res.dg_nuoc = als[len(als) - 2].dg_nuoc
        res.dg_tang = als[len(als) - 2].dg_tang
        res.dg_day = als[len(als) - 2].dg_day
        res.dg_dong = als[len(als) - 2].dg_dong
        res.dg_chen = als[len(als) - 2].dg_chen
        return res

    def _compute_recorded(self):
        for rec in self:
            if len(rec.allowance_line_ids) > 0:
                rec.recorded = True
            elif str(rec.id).replace('NewId_', '')[0:2] != "0x":
                rec.recorded = True
                als = self.env['allowance'].search([('allowancebymonth_id.id','=',rec.id)])
                if len(als) == 0:
                    plants = self.env['plantation'].search([('to', '=', rec.department_id.id),('lo', '=', 'a')])
                    for plant in plants:
                        if self.env['employee.benefit'].search([('department_id','=',rec.department_id.id)]).id == False:
                            self.env['employee.benefit'].create({'department_id': rec.department_id.id})
                        if self.env['salary.board'].search([('department_id','=',rec.department_id.id)]).id == False:
                            self.env['salary.board'].create({'department_id': rec.department_id.id})
                        if self.env['salary.board'].search([('department_id','=',rec.department_id.id)]).id and self.env['employee.benefit'].search([('department_id','=',rec.department_id.id)]).id:
                            sb = self.env['salary.board'].search([('department_id','=',rec.department_id.id)])
                            eb = self.env['employee.benefit'].search([('department_id','=',rec.department_id.id)])
                            cophep = 0
                            kophep = 0
                            rbs = self.env['rubber'].search([('empname','=',plant.employee_id.name)])
                            for rb in rbs:
                                if rb.thang == rec.thang and rb.nam == rec.nam:
                                    if rb.phep == 'cp':
                                        cophep += 1
                                    if rb.phep == 'kp':
                                        kophep += 1
                            chuyencan = 0
                            if kophep > 0:
                                chuyencan = 0
                            elif kophep == 0:
                                if cophep == 0:
                                    chuyencan = 300000
                                elif cophep == 1:
                                    chuyencan = 150000
                                elif cophep >= 2:
                                    chuyencan = 0
                            self.env['allowance'].create({'salaryboard_id': sb.id, 'employeebenefit_id': eb.id, 'employee_id': plant.employee_id.id, 'allowancebymonth_id': rec.id, 
                                'thang': rec.thang, 'nam': rec.nam, 'cophep': cophep, 'kophep': kophep, 'sttcn': plant.sttcn, 'chuyencan': chuyencan})
                    qk = []
                    for line in rec.allowance_line_ids:
                        qk.append(line.quykho)
                    qk.sort(reverse=True)
                    for line in rec.allowance_line_ids:
                        if line.quykho == qk[0]:
                            line.thuong_sl = 1000000
                        elif line.quykho == qk[1]:
                            line.thuong_sl = 800000
                        elif line.quykho == qk[2]:
                            line.thuong_sl = 500000
                        elif line.quykho == qk[3]:
                            line.thuong_sl = 300000
                        elif line.quykho == qk[4]:
                            line.thuong_sl = 200000

    @api.onchange('dg_nuoc','dg_day','dg_tang','dg_dong','dg_chen')
    def _onchange_dg(self):
        for rec in self:
            if len(rec.allowance_line_ids) > 0:
                for line in rec.allowance_line_ids:
                    line.dgta = rec.dg_tang
                    line.dgtb = rec.dg_tang
                    line.dgtc = rec.dg_tang
                    if self.env['rubber'].search([('empname', '=', line.employee_id.name),('thang', '=', line.thang),('nam', '=', line.nam)]):
                        rbs = self.env['rubber'].search([('empname', '=', line.employee_id.name)])
                        for rb in rbs:
                            if rb.thang == line.thang and rb.nam == line.nam:
                                if rb.lo == 'a':
                                    rb.dongia_tang = line.dgta
                                elif rb.lo == 'b':
                                    rb.dongia_tang = line.dgtb
                                elif rb.lo == 'c':
                                    rb.dongia_tang = line.dgtc
            if self.env['rubber'].search([('to', '=', rec.department_id.name),('thang', '=', rec.thang),('nam', '=', rec.nam)]):
                rbs = self.env['rubber'].search([('to', '=', rec.department_id.name)])
                for line in rbs:
                    if line.thang == rec.thang and line.nam == rec.nam:
                        line.dongia_nuoc = rec.dg_nuoc
                        line.dongia_day = rec.dg_day
                        line.dongia_dong = rec.dg_dong
                        line.dongia_chen = rec.dg_chen

    @api.constrains('department_id','thang','nam')
    def _check_allowancebymonth_unique(self):
        allowancebymonth_counts = self.search_count([('department_id','=',self.department_id.id),('thang','=',self.thang),('nam','=',self.nam),('id','!=',self.id)])
        if allowancebymonth_counts > 0:
            raise UserError(_("Phụ cấp " + self.department_id.name.lower() + " tháng " + self.thang + "/" + self.nam + " đã tồn tại."))
