import calendar
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class RewardByMonth(models.Model):
    _name = "reward.by.month"
    _description = "Reward By Month Model"

    to = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True)
    recorded = fields.Boolean('recorded', default=False, compute='_compute_recorded')
    thang = fields.Selection([
        ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'),
        ('07', '7'), ('08', '8'), ('09', '9'), ('10', '10'), ('11', '11'), ('12', '12'),
    ], string='Tháng', default=str(fields.Datetime.now().strftime('%m')), required=True)
    nam = fields.Selection([
        ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2024', '2024'),
        ('2025', '2025'), ('2026', '2026'), ('2027', '2027'), ('2028', '2028'), ('2029', '2029'),
    ], string='Năm', default=str(fields.Datetime.now().year), required=True)    
    name = fields.Char('Tên tổ', related='to.name')
    ghichu = fields.Html('Ghi chú')
    reward_line_ids = fields.One2many('reward', 'rewardbymonth_id', string='Xét Thưởng CN', copy=True)
    #ttth = fields.Float(compute='_compute_ttth', string='ttth')
    #ruttt = fields.Float(compute='_compute_ttth', string='ruttt')
    #pltl = fields.Float(compute='_compute_ttth', string='pltl')
    #pltln = fields.Float(compute='_compute_ttth', string='pltln')
    thongbao = fields.Char(compute='_compute_thongbao', string='Thông báo')
    namkt=fields.Char(string='Năm khai thác', compute='_compute_namkt', store=True)
    chiquy_pl = fields.Float(string='Chi Quỹ PL', compute='_compute_chiquy_pl', store=True)

    @api.depends('reward_line_ids')
    def _compute_chiquy_pl(self):
        for rec in self:
            total_chiquy_pl = 0
            for line in rec.reward_line_ids:                
                total_chiquy_pl += line.chiquy_pl
        rec.chiquy_pl = total_chiquy_pl
    
    @api.depends('thang','nam')
    def _compute_namkt(self):
        for rec in self:
            if rec.thang =='01':                
                rec.namkt = str(int(rec.nam) - 1)
            else:                
                rec.namkt = rec.nam
                
    @api.depends('thang','nam','to')
    def _compute_thongbao(self):
        for rec in self:
            rec.thongbao = ""
            if rec.recorded == True:
                rws = rec.env['allowance.by.month'].search([('thang','=',rec.thang),('nam','=',rec.nam),('department_id','=',rec.to.id)])
                if len(rws) != 1:
                    rec.thongbao = "BẢNG PHỤ CẤP THÁNG " + rec.thang + "/" + rec.nam + " " + rec.to.name + " CHƯA TẠO. HÃY TẠO ĐỂ CẬP NHẬT NGÀY PHÉP CÔNG NHÂN."
    
    '''@api.depends('reward_line_ids')
    def _compute_ttth(self):
        for rec in self:
            rec.ttth = 0
            rec.ruttt = 0
            rec.pltl = 0
            rec.pltln = 0
            ttth = 0
            ruttt = 0
            pltl = 0
            pltln = 0
            for line in rec.reward_line_ids:
                ttth += line.ttth
                ruttt += line.ruttt
                pltl += line.phucloitl
                pltln += line.phucloitln
            rec.ttth = ttth
            rec.ruttt = ruttt
            rec.pltl = pltl
            rec.pltln = pltln'''

    def _compute_recorded(self):
        for rec in self:
            if len(rec.reward_line_ids) > 0:
                rec.recorded == True
            elif str(rec.id).replace('NewId_', '')[0:2] != "0x":
                rec.recorded = True
                rws = self.env['reward'].search([('rewardbymonth_id.id','=',rec.id)])
                if len(rws) == 0:
                    plants = self.env['plantation'].search([('to', '=', rec.to.id),('lo', '=', 'a')])
                    for plant in plants:
                        rs = self.env['rubber.salary'].search([('employee_id','=',plant.employee_id.id)])
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
                                chuyencan = 200000
                            elif cophep == 1:
                                chuyencan = 100000
                            elif cophep >= 2:
                                chuyencan = 0
                        phucloi = 0
                        pltext = ''
                        days = calendar.monthrange(int(rec.nam), int(rec.thang))[1]
                        ngaylam = days - cophep - kophep
                        tien = float(plant.employee_id.diachi)
                        if cophep <=1 and kophep == 0:
                            phucloi = tien / days * ngaylam
                            pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày' 
                        elif cophep == 2 and kophep == 0:
                            phucloi = tien / days * ngaylam * 0.7
                            pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 70%'
                        elif cophep == 3 and kophep == 0:
                            phucloi = tien / days * ngaylam * 0.5
                            pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 50%'
                        elif cophep == 4 and kophep == 0:
                            phucloi = tien / days * ngaylam * 0.3
                            pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 30%'
                        elif cophep > 4 or kophep > 1:
                            phucloi = 0
                        elif cophep == 0 and kophep == 1:
                            phucloi = tien / days * ngaylam * 0.5
                            pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 50%'
                        elif  cophep == 1 and kophep == 1:
                            phucloi = tien / days * ngaylam * 0.4
                            pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 40%'
                        elif cophep == 2 and kophep == 1:
                            phucloi = tien / days * ngaylam * 0.3
                            pltext = '= (' + str(int(tien)) + ' / ' + str(days) + ' ngày) x ' + str(ngaylam) + ' ngày x 30%'
                        namkt = ''
                        thangkt = ''
                        if int(rec.thang) >= 2:
                            namkt = rec.nam
                            thangkt = rec.thang
                        else:
                            namkt = str(int(rec.nam) - 1)
                            if int(rec.thang) == 1:
                                thangkt = '13'
                            '''elif int(rec.thang) == 2:
                                thangkt = '14'
                        pltl = phucloi
                        pltln = phucloi
                        phucloitl = 0
                        phucloitln = 0
                        rwbs = self.env['reward'].search([('namkt','=',str(int(namkt) - 1)),('employee_id','=',plant.employee_id.id)])
                        if len(rwbs) > 0:
                            pltln += rwbs[len(rwbs) - 1].phucloitln
                        rws = self.env['reward'].search([('namkt','=',namkt)])
                        for rw in rws:
                            if rw.employee_id == plant.employee_id:
                                if int(rw.thangkt) <= int(thangkt):
                                    pltl += rw.phucloi
                                    pltln += rw.phucloi - rw.rutbot + rw.dongthem
                        phucloitl = pltl
                        phucloitln = pltln'''

                        self.env['reward'].create({'cophep': cophep, 'kophep': kophep, 'rubbersalary_id': rs.id, 'employee_id': plant.employee_id.id, 'rewardbymonth_id': rec.id, 
                            'thang': rec.thang, 'nam': rec.nam, 'namkt': namkt, 'thangkt': thangkt, 'sttcn': plant.sttcn, 'chuyencan': chuyencan, 'pltext': pltext}) #'phucloi': phucloi,, 'phucloitl': phucloitl

    @api.constrains('to', 'thang', 'nam')
    def _constrains_unique(self):
        rewardbymonth_counts = self.search_count([('to','=',self.to.id),('thang','=',self.thang),('nam','=',self.nam),('id','!=',self.id)])
        if rewardbymonth_counts > 0:
                raise UserError(_("Xét thưởng " + self.to.name + " tháng " + self.thang + "/" + self.nam + " đã có rồi."))
