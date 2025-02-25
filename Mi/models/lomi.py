from odoo import models, fields, api
from datetime import date

class Lomi(models.Model):
    _name = 'lomi'
    _description = 'Lô mì'

    # Fields
    tenlo = fields.Char(string="Lô")
    tenhang = fields.Char(string="Hàng")
    hang = fields.Integer(string="Số hàng", default=1)
    luong = fields.Integer(string="Số luồng", default=1)
    giong = fields.Many2one('giongmi', string="Giống")
    ngaytrong = fields.Date(string="Ngày trồng")
    kc_hom = fields.Float(string="KC cây", default=0.7)
    kc_hang = fields.Float(string="KC hàng", default=1.1)
    cd_hang = fields.Float(string="Hàng dài", default=100)
    kieutrong = fields.Many2one('kieutrong', string="Kiểu trồng")
    kieuro = fields.Many2one('kieuro', string="Kiểu rò")
    cr_ro = fields.Float(string="Rò rộng", default=1)
    ngaytuoi = fields.Integer(string="Ngày tuổi", compute='_compute_ngaytuoi')
    sohom = fields.Integer(string="SLG hom", compute='_compute_sohom', store=True)
    bonphan_line_ids = fields.One2many('bonphan.line', 'lomi_id', string="Bón phân Lines")

    @api.depends('ngaytrong')
    def _compute_ngaytuoi(self):
        for record in self:
            if record.ngaytrong:
                record.ngaytuoi = (date.today() - record.ngaytrong).days
            else:
                record.ngaytuoi = 0

    @api.depends('cd_hang', 'kc_hom', 'hang')
    def _compute_sohom(self):
        for record in self:
            if record.kc_hom != 0:
                record.sohom = record.cd_hang / record.kc_hom * record.hang
            else:
                record.sohom = 0

class BonphanLine(models.Model):
    _name = 'bonphan.line'
    _description = 'Bón phân Line'

    lomi_id = fields.Many2one('lomi', string="Lô mì", required=True, ondelete='cascade')
    giaidoan = fields.Selection([
        ('bon', 'Bón lót'),
        ('bon_thuc_1', 'Bón thúc 1'),
        ('bon_thuc_2', 'Bón thúc 2'),
        ('bon_thuc_3', 'Bón thúc 3'),
        ('bon_la_1', 'Bón lá 1'),
        ('bon_la_2', 'Bón lá 2'),
        ('bon_la_3', 'Bón lá 3')
    ], string="Giai đoạn", required=True)
    phan = fields.Many2one('product.template', string="Phân", domain="[('categ_id.name', '=', 'VẬT TƯ PHÂN BÓN')]")
    slg = fields.Float(string="SLG", digits=(16, 0))
    tyle_ro = fields.Float(string="Tỷ lệ-rò", digits=(16, 2))
    tyle_ho = fields.Float(string="Tỷ lệ-hố", digits=(16, 2))
    hang = fields.Float(string="Phân-hàng", compute='_compute_hang', digits=(16, 0))
    ro = fields.Float(string="Phân-rò", compute='_compute_ro', digits=(16, 0))
    ho = fields.Float(string="Phân-hố", compute='_compute_ho', digits=(16, 0))
    hom = fields.Float(string="Phân-1hom", compute='_compute_hom', digits=(16, 0))
    N = fields.Float(string="N", compute='_compute_N', digits=(16, 0), store=True)
    P = fields.Float(string="P", compute='_compute_P', digits=(16, 0), store=True)
    K = fields.Float(string="K", compute='_compute_K', digits=(16, 0), store=True)
    Ca = fields.Float(string="Ca", compute='_compute_Ca', digits=(16, 0), store=True)
    Mg = fields.Float(string="Mg", compute='_compute_Mg', digits=(16, 0), store=True)
    Si = fields.Float(string="Si", compute='_compute_Si', digits=(16, 0), store=True)
    OM = fields.Float(string="OM", compute='_compute_OM', digits=(16, 0), store=True)
    Humic = fields.Float(string="Humic", compute='_compute_Humic', digits=(16, 0), store=True)

    @api.depends('slg', 'phan.N')
    def _compute_N(self):
        for record in self:
            record.N = record.slg * record.phan.N if record.phan else 0

    @api.depends('slg', 'phan.P')
    def _compute_P(self):
        for record in self:
            record.P = record.slg * record.phan.P if record.phan else 0

    @api.depends('slg', 'phan.K')
    def _compute_K(self):
        for record in self:
            record.K = record.slg * record.phan.K if record.phan else 0

    @api.depends('slg', 'phan.Ca')
    def _compute_Ca(self):
        for record in self:
            record.Ca = record.slg * record.phan.Ca if record.phan else 0

    @api.depends('slg', 'phan.Mg')
    def _compute_Mg(self):
        for record in self:
            record.Mg = record.slg * record.phan.Mg if record.phan else 0

    @api.depends('slg', 'phan.Si')
    def _compute_Si(self):
        for record in self:
            record.Si = record.slg * record.phan.Si if record.phan else 0

    @api.depends('slg', 'phan.OM')
    def _compute_OM(self):
        for record in self:
            record.OM = record.slg * record.phan.OM if record.phan else 0

    @api.depends('slg', 'phan.Humic')
    def _compute_Humic(self):
        for record in self:
            record.Humic = record.slg * record.phan.Humic if record.phan else 0

    @api.depends('slg', 'lomi_id.hang')
    def _compute_hang(self):
        for record in self:
            record.hang = record.slg / record.lomi_id.hang if record.lomi_id.hang else 0

    @api.depends('hang', 'tyle_ro')
    def _compute_ro(self):
        for record in self:
            record.ro = record.hang * record.tyle_ro if record.tyle_ro else 0

    @api.depends('hang', 'tyle_ho')
    def _compute_ho(self):
        for record in self:
            record.ho = record.hang * record.tyle_ho if record.tyle_ho else 0

    @api.depends('ho', 'lomi_id.cd_hang', 'lomi_id.kc_hom')
    def _compute_hom(self):
        for record in self:
            record.hom = record.ho / (record.lomi_id.cd_hang / record.lomi_id.kc_hom) if record.lomi_id.kc_hom else 0

class Kieutrong(models.Model):
    _name = 'kieutrong'
    _description = 'Kiểu trồng'

    name = fields.Char(string="Tên kiểu trồng")

class Kieuro(models.Model):
    _name = 'kieuro'
    _description = 'Kiểu đổ rò'

    name = fields.Char(string="Tên kiểu đổ rò")

class Giongmi(models.Model):
    _name = 'giongmi'
    _description = 'Giống mì'

    name = fields.Char(string="Tên giống mì")