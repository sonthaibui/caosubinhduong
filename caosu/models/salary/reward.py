import calendar
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class Reward(models.Model):
    _name = "reward"
    _description = "Reward Model"

    bymonth = fields.Boolean('By Month', default=True, readonly=False)
    employee_id = fields.Many2one('hr.employee', string='Công nhân', required=True)
    thang = fields.Selection(string='Tháng', related='rewardbymonth_id.thang', store=True)
    nam = fields.Selection(string='Năm', related='rewardbymonth_id.nam', store=True)
    #ngaynghi = fields.Integer('Ngày Nghỉ', default='2', required=True)
    chuyencan = fields.Float('Chuyên cần', digits='Product Price')
    to= fields.Char(string='Tổ', related='rewardbymonth_id.to.name', store=True)
    diemkythuat1 = fields.Selection([
        ('Giỏi', 'Giỏi'), ('Khá', 'Khá'), ('TB', 'TB'), ('Yếu', 'Yếu'), ('Đạt', 'Đạt'), ('Không', 'Không'),
    ], string='Kỹ thuật 1', default='Giỏi')
    diemkythuat2 = fields.Selection([
        ('Giỏi', 'Giỏi'), ('Khá', 'Khá'), ('TB', 'TB'), ('Yếu', 'Yếu'), ('Đạt', 'Đạt'), ('Không', 'Không'),
    ], string='Kỹ thuật 2', default='Giỏi')
    tinhkythuat1 = fields.Float('KT1', digits='Product Price')
    tinhkythuat2 = fields.Float('KT2', digits='Product Price')
    kythuatb = fields.Float('Thưởng KT1', default='0', digits='Product Price')
    kythuatc = fields.Float('Thưởng KT2', default='0', digits='Product Price')
    dunggio = fields.Float('Đúng giờ', default='0', digits='Product Price')
    gomuday = fields.Float('Gỡ mũ dây', default='0', digits='Product Price')
    upday = fields.Float('Úp tô đậy váy', default='0', digits='Product Price')
    vesinh = fields.Float('Vệ sinh thùng', default='0', digits='Product Price')
    tanthumu = fields.Float('Tận thu mũ', default='0', digits='Product Price')
    ttth = fields.Float('TT tăng/giảm', default='0', digits='Product Price')
    ruttt = fields.Float('Rút TT', default='0', digits='Product Price')
    tichcuc = fields.Float('Tích cực', default='0', digits='Product Price')
    motsuat = fields.Float('1 suất', compute='_compute_motsuat', digits='One Decimal')
    sosuatcao = fields.Float('Số suất cạo', default='1.0', digits='One Decimal')
    tongtien = fields.Float('Tiền thưởng', compute='_compute_tongtien', digits='Product Price')
    #tongtien_luyke=fields.Float('Lũy kế',  compute='_compute_tongtien', store=False, readonly=False, digits='Product Price')
    rewardbymonth_id = fields.Many2one('reward.by.month', string='Reward By Month', ondelete='cascade')
    rubbersalary_id = fields.Many2one('rubber.salary', string='Phiếu Lương', ondelete='set null')
    sttcn = fields.Char('STT CN')
    namkt=fields.Char(string='Năm khai thác', compute='_compute_namkt', store=True)
    thangkt = fields.Char('Tháng khai thác', compute='_compute_namkt')
    diachi = fields.Selection(related='employee_id.diachi', string='Địa chỉ')
    cophep = fields.Integer('CP', default=0)
    kophep = fields.Integer('KP', default=0)
    tongtientl = fields.Float('TT tích lũy', digits='Product Price', compute='_compute_thuongphucloi')
    #tongtientln = fields.Float('TT TL năm', digits='Product Price', compute='_compute_tongtientl')
    phucloi = fields.Float('Phúc lợi', digits='Product Price')#, compute='_compute_phucloi')
    pltext = fields.Char('Diễn giải PL')
    phucloitl = fields.Float('PL tích lũy', digits='Product Price', compute='_compute_thuongphucloi') #, compute='_compute_phucloitl'    
    rutbot = fields.Float('Rút PL', digits='Product Price')
    dongthem = fields.Float('Đóng thêm', digits='Product Price')
    chiquy_pl = fields.Float('Chi quỹ PL', digits='Product Price')
    chothem = fields.Float('Cho thêm', digits='Product Price')
    #conlai = fields.Float('Còn lại', digits='Product Price', compute='_compute_conlai')    
    dixa = fields.Float('Đi xa', default=2, digits='One Decimal')
    tongdiem = fields.Float('Tổng điểm', compute='_compute_tongdiem', digits='One Decimal')
    tongdiem_tl = fields.Float('Lũy kế', compute='_compute_tongdiem_tl', digits='One Decimal')
    
    # New fields
    qk_drc_thang = fields.Float('Quy khô', compute='_compute_quykho', digits='Product Price')
    quykho_drc_target = fields.Float('Kế hoạch', compute='_compute_quykho_drc_target', digits='Product Price')
    qk_thang_lk = fields.Float('QK lũy kế', compute='_compute_thuonglk',  digits='Product Price')
    qk_target_lk = fields.Float('QK kế hoạch', compute='_compute_thuonglk',  digits='Product Price')
    tyle_kehoach = fields.Float('(% Đạt)', compute='_compute_thuonglk')
    gia_thuong = fields.Float('Giá thưởng', compute='_computethuonglk', digits='Product Price')

    
    @api.depends('employee_id', 'thang', 'nam', 'to', 'rubbersalary_id','rubbersalary_id.thang')
    def _compute_quykho(self):            
        for rec in self:
            # lũy kế DRC trong cùng tháng
            rec.qk_drc_thang = 0.0            
            if not (rec.thang and rec.nam and rec.to and rec.employee_id):
                continue            
            # tìm tất cả bản ghi cùng tổ, cùng rubbersalary, trong thang
            prior_recs = rec.env['rubber'].search([
                ('to',               '=', rec.to),
                ('rubbersalary_id',  '=', rec.rubbersalary_id.id),
                ('thang',             '=', rec.thang),
                ('nam',             '=', rec.nam),
            ])
            # cộng dồn qk_drc
            rec.qk_drc_thang = sum(r.quykho_drc for r in prior_recs)
    
    @api.depends('thang', 'namkt', 'rewardbymonth_id.to', 'rubbersalary_id.employee_id')
    def _compute_quykho_drc_target(self):
        for rec in self:
            rec.quykho_drc_target = 0.0
            if not (rec.thang and rec.namkt and rec.rewardbymonth_id.to and rec.rubbersalary_id.employee_id):
                continue
                       
            # Convert month: 01->13, 02->14, 03->3, 04->4, etc.
            month_int = int(rec.thang)
            if month_int == 1:
                target_month = 13
            elif month_int == 2:
                target_month = 14
            else:
                target_month = month_int
            
            # Look up YieldTarget model
            # Find all plantations for the employee
            plantations = self.env['plantation'].search([
                ('employee_id', '=', rec.rubbersalary_id.employee_id.id)
            ])
            if not plantations:
                continue

            total_target = 0.0
            month_field = f'quykho_drc_target_t{target_month}'
            for plantation in plantations:
                yield_target = self.env['yield.target'].search([
                    ('department_id', '=', rec.rewardbymonth_id.to.id),
                    ('namkt', '=', rec.namkt),
                    ('plantation_id', '=', plantation.id)
                ], limit=1)
                if yield_target and hasattr(yield_target, month_field):
                    total_target += getattr(yield_target, month_field, 0.0)
            rec.quykho_drc_target = total_target
            
                    
            '''# Raise UserError to debug values
            raise UserError(f"DEBUG VALUES:\n"
                            f"Plantation Name: {plantation.name}\n"
                            f"Yield Target: {yield_target}\n"
                            f"Target Month: {target_month}\n"
                            f"Month Field: {month_field}\n"
                            f"Quykho DRC Target: {rec.quykho_drc_target}")'''
            
    @api.depends('qk_drc_thang', 'quykho_drc_target', 'thang', 'namkt', 'rewardbymonth_id.to', 'employee_id')
    def _compute_thuonglk(self):
        for rec in self:
            rec.qk_thang_lk = 0.0
            rec.qk_target_lk = 0.0
            if not rec.namkt or not rec.thang:
                continue

            # Find all records in the same year (`namkt`) and previous months
            previous_rewards = self.env['reward'].search([
                ('rewardbymonth_id.to','=', rec.rewardbymonth_id.to.id),
                ('employee_id', '=', rec.employee_id.id),
                ('namkt', '=', rec.namkt),
                ('thang', '<=', rec.thang)
            ])

            # Sum up `qk_drc_thang` and `quykho_drc_target` for previous months
            rec.qk_thang_lk = sum(r.qk_drc_thang for r in previous_rewards)
            rec.qk_target_lk = sum(r.quykho_drc_target for r in previous_rewards)

            rec.tyle_kehoach = (rec.qk_drc_thang / rec.quykho_drc_target) if rec.quykho_drc_target > 0 else 0
            if rec.tyle_kehoach >= 1.2:
                rec.gia_thuong = 2000
            elif rec.tyle_kehoach >= 1.1:
                rec.gia_thuong = 1500
            elif rec.tyle_kehoach >= 1:
                rec.gia_thuong = 1000
            elif rec.tyle_kehoach >= 0.9:
                rec.gia_thuong = 700
            elif rec.tyle_kehoach >= 0.8:
                rec.gia_thuong = 500
            elif rec.tyle_kehoach >= 0.7:
                rec.gia_thuong = 200
            else:
                rec.gia_thuong = 0 
                
    @api.depends('chuyencan', 'tinhkythuat1', 'tanthumu', 'tichcuc', 'dixa')
    def _compute_tongdiem(self):
        for rec in self:
            rec.tongdiem = rec.chuyencan + rec.tinhkythuat1 + rec.tanthumu + rec.tichcuc + rec.dixa
            
    @api.depends('tongdiem', 'thang', 'namkt')
    def _compute_tongdiem_tl(self):
        for rec in self:
            rec.tongdiem_tl = 0.0
            if not rec.namkt or not rec.thang:
                continue

            # Define the threshold for computation
            threshold_year = '2025'
            threshold_month = '05'

            # Only include records from `thang = 5` and `namkt = 2025` onward
            previous_rewards = self.env['reward'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('namkt', '=', rec.namkt),
                ('thang', '<=', rec.thang),
                '|',
                ('namkt', '>', threshold_year),
                '&',
                ('namkt', '=', threshold_year),
                ('thang', '>=', threshold_month)
            ])

            # Sum up `tongdiem` for valid records
            rec.tongdiem_tl = sum(r.tongdiem for r in previous_rewards)

    @api.depends('thang','nam')
    def _compute_namkt(self):
        for rec in self:
            if rec.thang =='01':
                rec.thangkt = rec.thang
                rec.namkt = str(int(rec.nam) - 1)
            else:
                rec.thangkt = rec.thang
                rec.namkt = rec.nam

    '''@api.onchange('rutbot')
    def _onchange_rutbot(self):
        for rec in self:
            if rec.rutbot > rec.phucloitln:
                raise UserError("Không thể rút quá sô tiền phúc lợi năm.")'''
            
    @api.model_create_multi
    def create(self, vals):
        res = super(Reward, self).create(vals)
        res.dunggio = 100000
        res.gomuday = 100000
        res.upday = 100000
        res.tanthumu = 2
        res.tichcuc = 2
        res.tinhkythuat1 = 2
        res.chuyencan = 2
        res.dixa = 2
        return res
            
    
    @api.depends('chuyencan','kythuatb','kythuatc','dunggio','gomuday','upday','tanthumu','tichcuc','vesinh') 
    def _compute_motsuat(self):
        for rec in self:
            rec.motsuat = rec.chuyencan + rec.tinhkythuat1 + rec.tinhkythuat2 + rec.dunggio + rec.gomuday + rec.upday + rec.tanthumu + rec.tichcuc+ rec.vesinh

    @api.depends('motsuat','sosuatcao')
    def _compute_tongtien(self):
        for rec in self:
            rec.tongtien = rec.motsuat * rec.sosuatcao            

    @api.depends('thang', 'nam', 'tongtien', 'phucloi', 'rutbot', 'dongthem')
    def _compute_thuongphucloi(self):
        for rec in self:
            tongtientl = 0
            phucloitl = 0
            rws = self.env['reward'].search([('employee_id','=',rec.employee_id.id)])
            for rw in rws:
                if int(rw.nam) < int(rec.nam):                    
                    tongtientl += rw.tongtien - rw.ruttt + rw.ttth
                    phucloitl += rw.phucloi - rw.rutbot + rw.dongthem- rw.chiquy_pl + rw.chothem                    
                elif int(rw.nam) == int(rec.nam):
                    if int(rw.thang) <= int(rec.thang):
                        tongtientl += rw.tongtien - rw.ruttt + rw.ttth
                        phucloitl += rw.phucloi - rw.rutbot + rw.dongthem - rw.chiquy_pl + rw.chothem
            rec.tongtientl = tongtientl
            rec.phucloitl = phucloitl      
            

    