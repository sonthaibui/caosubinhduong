from odoo import models, fields, api
from datetime import date

class Hangmi(models.Model):
    _name = 'hangmi'
    _description = 'Hàng mì'
    
    
    tenlo = fields.Char(string="Lô", related='lomi_id.tenlo', store=True)
    tenhang = fields.Char(string="Tên hàng", compute='_compute_tenhang')
    sohang = fields.Integer(string="Số hàng")
    soluongmi = fields.Integer(string="Số luồng")
    ngaytrong = fields.Date(string="Ngày trồng")
    ngaytuoi = fields.Integer(string="Ngày tuổi", compute='_compute_ngaytuoi')
    kc_hom = fields.Float(string="KC cây", default=0.7)    
    cd_hang = fields.Float(string="Hàng dài", default=100)
    cr_ro = fields.Float(string="Rò rộng", default=1)
    giong_id = fields.Many2one('giongmi', string="Giống")
    kieuhang_id = fields.Many2one('kieuhang', string="Kiểu hàng")
    kieutrong_id = fields.Many2one('kieutrong', string="Kiểu trồng")
    kieuro_id = fields.Many2one('kieuro', string="Kiểu rò")    
    sohom = fields.Integer(string="SLG hom", compute='_compute_sohom')
    
    bonphan_line_ids = fields.Many2many('bonphan.line', 'bonphan_line_hangmi_rel', 'hangmi_id', 'bonphan_line_id', string="Bón phân Lines")
    bonphan_ids = fields.Many2many('bonphan', 'bonphan_hangmi_rel', 'hangmi_id', 'bonphan_id', string="Bón phân")
    lomi_id = fields.Many2one('lomi', string="Lô mì", required=True, ondelete='cascade')

    def name_get(self):
        result = []
        for record in self:
            name = record.tenhang
            result.append((record.id, name))
        return result
    
    @api.depends('tenlo', 'kieuhang_id')
    def _compute_tenhang(self):
        for record in self:
            record.tenhang = f"{record.tenlo}-{record.kieuhang_id.name}" if record.tenlo and record.kieuhang_id else ''

    @api.depends('ngaytrong')
    def _compute_ngaytuoi(self):
        for record in self:
            if record.ngaytrong:
                record.ngaytuoi = (date.today() - record.ngaytrong).days
            else:
                record.ngaytuoi = 0

    @api.depends('cd_hang', 'kc_hom', 'sohang')
    def _compute_sohom(self):
        for record in self:
            if record.kc_hom != 0:
                record.sohom = record.cd_hang / record.kc_hom * record.sohang
            else:
                record.sohom = 0

class Kieuhang(models.Model):
    _name = 'kieuhang'
    _description = 'Kiểu hàng'

    name = fields.Char(string="Tên kiểu hàng")

class Kieutrong(models.Model):
    _name = 'kieutrong'
    _description = 'Kiểu trồng'

    name = fields.Char(string="Tên kiểu trồng")

class Kieuro(models.Model):
    _name = 'kieuro'
    _description = 'Kiểu rò'

    name = fields.Char(string="Tên kiểu rò")

class Giongmi(models.Model):
    _name = 'giongmi'
    _description = 'Giống mì'

    name = fields.Char(string="Tên giống mì")

class Kieuhang(models.Model):
    _name = 'kieuhang'
    _description = 'Kiểu hàng'

    name = fields.Char(string="Tên kiểu hàng")