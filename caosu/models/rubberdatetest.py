from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class RubberTestByDate(models.Model):
    _name = "rubber.test.date"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Rubber Test Date Model"
    _rec_name = 'recname'

    active = fields.Boolean('Active', default=True)    
    daoup = fields.Integer('Dao Úp thứ')
    daongua = fields.Integer('Dao ngửa thứ')  
    ghichu = fields.Char('Ghi chú')    
    kt_daoup = fields.Char('Dao kích thích')  
    ctktup = fields.Many2one('ctkt', string='CT úp', default=lambda self: self._default_ctkt())
    lo = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C')], string='Lô', default='a', required=True, tracking=True)
    miengcao = fields.Char('Miệng cạo')
    ngay = fields.Date('Ngày', default=fields.Datetime.now(), required=True, tracking=True)     
    thoitiet = fields.Char('Thời tiết')
    thoigian_cao = fields.Char('Thời gian cạo')
    thoigian_trut = fields.Char('Thời gian trút')
    to = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True)    
    do_tb3 = fields.Float('ĐộTB 3 ngày', default = 0, compute='_compute_dotb3', digits='One Decimal')
    recname = fields.Char('Rec Name', compute='_compute_recname')
    thang = fields.Char('Tháng', compute='_compute_ngay')
    nam = fields.Char('Năm', compute='_compute_ngay')
    rubbertest_line_ids = fields.One2many('rubber.test', 'rubbertestbydate_id', string='Sản lượng thí nghiệm')
    kichthich = fields.Boolean('KT', default =False, store=True, readonly=False) #Son them

    """@api.depends('kt_daoup') # Son them
    def _compute_kichthich(self):
        for rec in self:
            if rec.kt_daoup == "Dao 1":
                rec.kichthich = True
            else:
                rec.kichthich = False"""
    @api.depends('ngay')
    def _compute_ngay(self):
        for rec in self:
            rec.thang = datetime.strptime(str(rec.ngay),'%Y-%m-%d').strftime('%m')
            rec.nam = datetime.strptime(str(rec.ngay),'%Y-%m-%d').strftime('%Y')

    @api.onchange('to')
    def _onchange_to(self):
        if self.to:
            rubbertestbydate_counts = self.search_count([('to','=',self.to.id),('ngay','=',self.ngay),('lo','=',self.lo)])
            if rubbertestbydate_counts > 0:
                raise UserError(_("Rubber Test by date already exists!"))
            else:
                if len(self.rubbertest_line_ids) > 0:
                    dep = self.to
                    for line in self.rubbertest_line_ids:
                        line.unlink()
                    self.to = dep.id
                    #xoa san luong cu
                if len(self.rubbertest_line_ids) == 0:
                    if len(self.env['plantation.test'].search([('to', '=', self.to.id),('lo', '=', self.lo)])) == False:
                        raise UserError(_("Department " + self.to.name.upper() + " lot " + self.lo.upper() + " doesn't have any plantation test."))
                    #bao loi neu to chua co plantation
                    else:
                        plants = self.env['plantation.test'].search([('to', '=', self.to.id),('lo', '=', self.lo),('active', '=', True), ])
                        for plant in plants:
                            self.env['rubber.test'].create({'rubbertestbydate_id': self.id, 'plantationtest_id': plant.id})
                            #Tao san luong va gan plantation_id
    @api.depends('to','ngay')
    def _compute_recname(self):
        for rec in self:
            rec.recname = rec.to.name + ' - ' + datetime.strptime(str(rec.ngay),'%Y-%m-%d').strftime('%d/%m/%Y')

    @api.onchange('ngay')
    def _onchange_ngay(self):
        if self.to:
            rubbertestbydate_counts = self.search_count([('to', '=', self.to.id), ('ngay', '=', self.ngay)])
            if rubbertestbydate_counts > 0:
                raise UserError(_("Rubber Test by date already exists!"))   

    @api.constrains('to','ngay')
    def _check_rubbertestdate_unique(self):
        rubbertestdate_counts = self.search_count([('to','=',self.to.id),('ngay','=',self.ngay),('id','!=',self.id)])
        if rubbertestdate_counts > 0:
            raise ValidationError("Rubber Test By Date already exists!")
    @api.depends('rubbertest_line_ids')
    def _compute_dotb3(self):        
        x = 0
        y = 0  
        
        for line in self.rubbertest_line_ids:
            x += line.mu_up3           
            y += line.mu_up3 * line.do_up3          
       
        if x > 0:
            self['do_tb3'] = y / x
        else:
            self['do_tb3'] = 0
    
    @api.model
    def _default_ctkt(self):
        default_ctkt = self.env['ctkt'].search([('name','=','Chưa bôi')], limit=1)
        if not default_ctkt:
            # Create a default ctkt record if none exist
            default_ctkt = self.env['ctkt'].create({'name': 'Chưa bôi'})
        return default_ctkt.id
        
    
    @api.onchange('ctktup')
    def _onchange_ctktup(self):
        for line in self.rubbertest_line_ids:
            if line.ctktup !="Chưa bôi":
                line.ctktup = self.ctktup