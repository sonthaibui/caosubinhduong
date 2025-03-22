from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

#Phai de o tren plantiontest thi moi ko bi ko nhan ra model rubber.tree trong field socay
#co the tao file python khac thi ko bi loi
class RubberTree(models.Model):
    _name = 'rubber.tree'
    _description = 'Cây Cao Su'
    _rec_name = "name"

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Name', required=True, copy=False, default='New')

    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            last_record = self.search([], order='id desc', limit=1)
            if last_record:
                last_name = last_record.name
                new_name = str(int(last_name) + 1).zfill(2)
            else:
                new_name = '01'
            vals['name'] = new_name
        return super(RubberTree, self).create(vals)
class Matcao(models.Model):
    _name = 'matcao'
    _description = 'Mặt Cao'
    _rec_name = "name"

    active = fields.Boolean('Active', default=True)
    name = fields.Char(string='Name', required=True, copy=False, default='Binh thuong')

class RubberTestNhom(models.Model):
    _name = 'rubber.test.nhom'
    _description = 'Nhóm for Rubber Test Report'

    name = fields.Char(string="Name", required=True)
    plantationtest_ids = fields.Many2many(
        'plantation.test',
        'plantation_test_nhom_rel',
        'rubber_test_nhom_id',   # this model's id field
        'plantationtest_id',     # target model's id field
        string='Plantation Tests',
        store=True
    )
class PlantationTest(models.Model):
    _name = 'plantation.test'
    _description = 'Plantation Test Model'
    _rec_name = "name"

    active = fields.Boolean('Active', default=True)
    name = fields.Char('Mã')#, compute='_compute_ma_to')
    nongtruong = fields.Selection([('DHR', 'Đăk Hring'), ('DRE', 'Đăk Tờ Re'),('THTR', 'Thanh Trung'),('DTH', 'Triệu Hải'),('SS', 'Sa Sơn'),('IL', 'Ia Le')], string='Nông Trường', default='DHR', required=True)
    loso = fields.Char('Lô Số', default='1')
    sophan = fields.Char('Số Hàng', default='1')
    to = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True,
        default=lambda self: self.env['hr.department'].search([('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], limit=1))
    to_name = fields.Char('Tổ', related='to.name')
    toname = fields.Char('Tổ Name', compute='_compute_ma_to')
    lo = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C')], string='Lô', default='a', required=True)
    sttcn = fields.Selection([
        ('01', '1'), ('02', '2'), ('03', '3'), ('04', '4'), ('05', '5'), ('06', '6'), ('07', '7'), ('08', '8'), ('09', '9'), ('10', '10'),
        ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), ('21', '21'),
        ('22', '22'), ('23', '23'), ('24', '24'), ('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), ('29', '29'), ('30', '30'),
    ], string='STT CN', default='01', required=True)
    socay = fields.Many2one('rubber.tree', string='Số Cây', required=True, default=lambda self: self._default_socay()) # ko set defaut thi bi loi bool khi tinh ten phan cay
    employee_id = fields.Many2one('hr.employee', string='Công nhân', required=True)
    hangso = fields.Char('Hàng số')    
    giong = fields.Char('Giống', default='GT1')
    tyle = fields.Char('% Giống', default='80%')    
    namtrong = fields.Char('Năm Trồng', default='1994')
    nammomieng = fields.Char('Năm Mở Miệng', default='2000')
    namcaoup = fields.Char('Năm Cạo Úp', default='2015')
    rubbertest_line_ids = fields.One2many('rubber.test', 'plantationtest_id', string='Sản lượng mũ cạo thí nghiệm')
    vanhcay = fields.Integer('Vành Cây', default=0)
    matcao = fields.Many2one('matcao', string='Mặt cạo', required=True, store=True)
    # New model for Nhóm
    nhom_ids = fields.Many2many(
        'rubber.test.nhom',
        'plantation_test_nhom_rel',
        'plantationtest_id',       # this model's id field
        'rubber_test_nhom_id',     # target model's id field
        string='Nhóm',
        store=True
    )
    '''color = fields.Selection([
        ('red', 'Red'), 
        ('blue', 'Blue'), 
        ('green', 'Green'), 
        ('black', 'Black'), 
        ('brown', 'Brown'), 
        ('pink', 'Pink'), 
        ('purple', 'Purple'), 
        ('orange', 'Orange'), 
        ('grey', 'Grey'), 
        ('yellow', 'Yellow')
    ], string='Color', default='black')'''    

    @api.model
    def _default_socay(self):
        # Ensure at least one RubberTree record exists
        default_tree = self.env['rubber.tree'].search([], limit=1)
        if not default_tree:
            # Create a default RubberTree record if none exist
            default_tree = self.env['rubber.tree'].create({'name': '01'})
        return default_tree.id
    
    @api.constrains('nongtruong','lo','to','sttcn')
    def _check_plantationtest_unique(self):
        plantationtest_counts = self.search_count([('nongtruong','=', self.nongtruong),('id','!=',self.id),
            ('lo','=',self.lo),('to','=',self.to.id),('socay','=',self.socay.id)])
        if plantationtest_counts > 0:
            raise ValidationError("Plantation Test already exists!")       
    
    
    @api.depends('nongtruong','to','lo','socay.name')
    def _compute_ma_to(self):
        for rec in self:
            ref = 'To' + rec.to.name[3:]
            rec.name = rec.nongtruong + '-' + ref + '-' + rec.lo.upper() + rec.socay.name
            rec.toname = '-' + rec.to.name[3:]
    @api.onchange('nongtruong', 'to', 'lo', 'socay')
    def _onchange_fields(self):
        self._compute_ma_to()