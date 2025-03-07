from odoo import api, fields, models, _

class CTKT(models.Model):
    _name = 'ctkt'
    _description = 'Công thức kích thích'
    _rec_name = "name"

    name = fields.Char(string='Name', required=True, copy=False)
    congthuc = fields.Html(string='Công thức')

    '''def __init__(self, pool, cr):
        # Call the super method
        super(CTKT, self).__init__(pool, cr)
        # Check if the record with name 'Chưa bôi' exists
        cr.execute("SELECT id FROM ctkt WHERE name = 'Chưa bôi'")
        exists = cr.fetchone()
        if not exists:
            # Create the record if it does not exist: lam khac kieu rubbertree
            cr.execute("INSERT INTO ctkt (name, create_uid, create_date, write_uid, write_date) VALUES ('Chưa bôi', 1, NOW(), 1, NOW())")'''
class RubberTest(models.Model):
    _name = "rubber.test"
    _description = "Rubber Test Model"
    _rec_name = 'empname'

    active = fields.Boolean('Active', default=True)   
    do_up = fields.Float('Độ', default='0', digits=(16, 1))
    do_up3 = fields.Float('Độ-3N', digits=(16, 1), compute='_compute_do3')
    do_up6 = fields.Float('Độ-6N', digits=(16, 1), compute='_compute_do6')
    do_ngua = fields.Float('Độ', digits=(16, 1))
    do_bo = fields.Float('Độ', digits=(16, 1)) #test thu    
    
    mu_up = fields.Float('Úp', default='0', digits=(42, 0))
    mu_up3 = fields.Float('Úp-3N', default='0', digits=(42, 1))
    mu_up6 = fields.Float('Úp-6N', default='0', digits=(42, 3))
    mu_ngua = fields.Float('Ngửa', default='0', digits=(16, 0))
    mu_bo = fields.Float('Bợ', default='0', digits=(16, 0))     

    ghichu = fields.Char('Ghi chú')
    kichthich = fields.Boolean('KT-U', store=True, readonly=False, compute='_compute_kichthich') #Son sua
    kichthichngua = fields.Boolean('KT-N', store=True, readonly=False) #Son sua
    congthuc_kt = fields.Char('Công thức', store=True, readonly=False) #Son them
    ctktup = fields.Many2one('ctkt', string='CT úp', default=lambda self: self._default_ctkt())
    ctktngua = fields.Many2one('ctkt', string='CT ngửa')
    occtktup = fields.Boolean('OC CT úp', default = False, store=True)
    rubbertestbydate_id = fields.Many2one('rubber.test.by.date', string='Sản lượng thí nghiệm')
    kt_daoup = fields.Integer('KTU', default='0', digits='Product Unit of Measure', store=True, readonly=False)
    kt_daongua = fields.Integer('KTN', default='0', digits='Product Unit of Measure', store=True, readonly=False)
    daoup = fields.Integer('Dao-U', related='rubbertestbydate_id.daoup', store=True, readonly=False )
    daongua = fields.Integer('Dao-N', related='rubbertestbydate_id.daongua', store=True, readonly=False)
    lo = fields.Char('Lô', compute='_compute_lo', store=True, readonly=False) #Son sua khong lay quan he nua
    ngay = fields.Date('Ngày', compute='_compute_ngay', store=True, readonly=False) #Son sua khong lay quan he nua
    thang = fields.Char('Tháng', related='rubbertestbydate_id.thang')
    nam = fields.Char('Năm', related='rubbertestbydate_id.nam')    
    
    rubbertestbydate_id = fields.Many2one('rubber.test.date', string='Rubber Test By Date', ondelete='cascade')
    plantationtest_id = fields.Many2one('plantation.test', string='Phần cây thí nghiệm', ondelete='cascade')
    empname = fields.Char('Tên Công Nhân', related='plantationtest_id.employee_id.name')    
    plantestcode = fields.Char(related='plantationtest_id.name')
    plantestname = fields.Char(related='plantationtest_id.socay.name', store=True) #Luc dau related='plantationtest_id.socay' bi loi ko vao odoo duoc  
    to = fields.Char('Tổ', compute='_compute_to', store=True, readonly=False) #Son them
    miengcao = fields.Char('Miệng cạo', store=True, readonly=False) #Son them
    thoitiet = fields.Char('Thời tiết', compute='_compute_thoitiet', store=True, readonly=False) #Son them
    lan_kt_up = fields.Integer('Lần KTU', default='0',store=True)#son them 23.6.24
    dao_kt_up = fields.Integer('Dao KTU', default='0',store=True)
    lan_kt_ngua = fields.Integer('Lần KTN', default='0',store=True)#son them 23.6.24
    dao_kt_ngua = fields.Integer('Dao KTN', default='0',store=True)
    mulantruoc_up = fields.Float('Lần trước U', default='0',store=True, digits=(16, 0))
    mulantruoc_ngua = fields.Float('Lần trước N', default='0',store=True, digits=(16, 0))    
    mudaotruoc_up = fields.Float('Dao trước U', default='0',store=True, digits=(16, 0))
    mudaotruoc_ngua = fields.Float('Dao trước N', default='0',store=True, digits=(16, 0))
    chenhlechkho_up = fields.Float('Khô U +/-', default='0',store=True, digits=(16, 1))
    chenhlechkho_up_state = fields.Boolean('CLKU', default=True,store=True)
    chenhlechkho_ngua = fields.Float('Khô N +/-', default='0',store=True, digits=(16, 1))
    chenhlechkho_ngua_state = fields.Boolean('CLKN', default=True,store=True)
    quykho_up = fields.Float('Quy Khô U', default='0',store=True, digits=(16, 1))#son them 23.6.24
    quykho_ngua = fields.Float('Quy Khô N', default='0',store=True, digits=(16, 1))
    #color = fields.Char(related='plantationtest_id.color')
    vanhcay = fields.Integer(related='plantationtest_id.vanhcay')
    matcao = fields.Char(related='plantationtest_id.matcao.name')        

    @api.depends('ctktup') # Add the appropriate dependencies
    def _compute_kichthich(self):
        for rec in self:
            if rec.ctktup and rec.ctktup.name != "Chưa bôi":
                rec.kichthich = True
            else: rec.kichthich = False            

    @api.depends('rubbertestbydate_id.ngay')
    def _compute_ngay(self):
        for rec in self:            
            rec.ngay = rec.rubbertestbydate_id.ngay
    @api.depends('rubbertestbydate_id.lo')
    def _compute_lo(self):
        for rec in self:            
            rec.lo = rec.rubbertestbydate_id.lo
    @api.depends('rubbertestbydate_id.to.display_name')
    def _compute_to(self):
        for rec in self:            
            rec.to = rec.rubbertestbydate_id.to.display_name    
    @api.depends('rubbertestbydate_id.thoitiet') # Son them
    def _compute_thoitiet(self):
        for rec in self:            
            if rec.rubbertestbydate_id.thoitiet:
                rec.thoitiet = rec.rubbertestbydate_id.thoitiet       
    @api.depends('mu_up','do_up','mu_up3') # Son them
    def _compute_do3(self):
        for rec in self:
            rec.do_up3 = 0            
            if rec.mu_up3 > 0:
                rec.do_up3 = rec.mu_up * rec.do_up / rec.mu_up3                
    @api.depends('mu_up','do_up','mu_up6') # Son them
    def _compute_do6(self):
        for rec in self:            
            rec.do_up6 = 0
            if rec.mu_up6 > 0:
                rec.do_up6 = rec.mu_up * rec.do_up / rec.mu_up6
    @api.model
    def _default_ctkt(self):
        for rec in self:        
            if rec.rubbertestbydate_id.ctktup : 
            # phai lay gia tri cuar rubberbydate chu khong cho on change, neu ko thi bi gan Chua boi va phai sua ctktup cua rubberbydate moi tinh lai
                default_ctkt = rec.rubbertestbydate_id.ctktup
            else:            
                default_ctkt = self.env['ctkt'].search([('name', '=', 'Chưa bôi')], limit=1)
                if not default_ctkt:
                # Create a default ctkt record if none exist
                    default_ctkt = self.env['ctkt'].create({'name': 'Chưa bôi'})        
            return default_ctkt.id if default_ctkt else None
    @api.onchange('ctktup')
    def _onchange_ctktup(self):
        self.occtktup = True            
        return {
            'value': {
                'occtktup': True
            }
        }
    '''@api.depends('ctktup')
    def _compute_occtktup(self):
        for record in self:
            record.occtktup = bool(record.ctktup)  # True if ctktup is set'''   
