from odoo import models, fields, api
from datetime import date

class Hangmi(models.Model):
    _name = 'hangmi'
    _description = 'Hàng mì'    
    
    tenlo = fields.Char(string="Lô", related='lomi_id.tenlo', store=True)
    tenhang = fields.Char(string="Tên hàng", compute='_compute_tenhang')
    STT = fields.Char(string="STT")
    hide = fields.Boolean(string="Ẩn", default=False)
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
    N = fields.Float(string="N", compute='_compute_phan', digits=(16, 0))
    P = fields.Float(string="P", compute='_compute_phan', digits=(16, 0))
    K = fields.Float(string="K", compute='_compute_phan', digits=(16, 0))
    N_add = fields.Float(string="N+", compute='_compute_phan', digits=(16, 0))
    P_add = fields.Float(string="P+", compute='_compute_phan', digits=(16, 0))
    K_add = fields.Float(string="K+", compute='_compute_phan', digits=(16, 0))
    phanlot = fields.Html(string="Phân lót", compute="_compute_phanlot")
    phanthuc1 = fields.Html(string="Phân Thúc 1", compute="_compute_phanthuc1")
    money_lot = fields.Float(string="$ phân lót", compute='_compute_money_lot', digits=(16, 0))    
    money_thuc1 = fields.Float(string="$ phân thúc1", compute='_compute_money_thuc1', digits=(16, 0))
    phanthuc2 = fields.Html(string="Phân Thúc 2", compute="_compute_phanthuc2")
    money_thuc2 = fields.Float(string="$ phân thúc2", compute='_compute_money_thuc2', digits=(16, 0))
    phanthuc3 = fields.Html(string="Phân Thúc 3", compute="_compute_phanthuc3")
    money_thuc3 = fields.Float(string="$ phân thúc3", compute='_compute_money_thuc3', digits=(16, 0))
    bonla1 = fields.Html(string="Bón lá 1", compute="_compute_bonla1")
    money_bonla1 = fields.Float(string="$ bón lá 1", compute='_compute_money_bonla1', digits=(16, 0))
    bonla2 = fields.Html(string="Bón lá 2", compute="_compute_bonla2")
    money_bonla2 = fields.Float(string="$ bón lá 2", compute='_compute_money_bonla2', digits=(16, 0))
    bonla3 = fields.Html(string="Bón lá 3", compute="_compute_bonla3")
    money_bonla3 = fields.Float(string="$ bón lá 3", compute='_compute_money_bonla3', digits=(16, 0))
    bonphan_line_ids = fields.Many2many('bonphan.line', 'bonphan_line_hangmi_rel', 'hangmi_id', 'bonphan_line_id', string="Bón phân Lines")
    bonphan_ids = fields.Many2many('bonphan', 'bonphan_hangmi_rel', 'hangmi_id', 'bonphan_id', string="Bón phân")
    lomi_id = fields.Many2one('lomi', string="Lô mì", required=True, ondelete='cascade')
    quycach = fields.Html(string="Quy cách")
    theodoi = fields.Html(string="Theo dõi")

    def name_get(self):
        result = []
        for record in self:
            name = record.tenhang
            result.append((record.id, name))
        return result
    
    @api.depends("bonphan_line_ids")
    def _compute_phanlot(self):
        for record in self:
            seen = set()
            parts = []
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón lót":
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        # Get the color from product.template; fallback to a default color if not set
                        color = line.phan_id.color or "#000000"
                        parts.append(f"<span style='color: {color};'><strong>{line.phan_id.abbre}</strong></span> {line.soluong:,.0f}kg")
            record.phanlot = " & ".join(parts)
    
    @api.depends("bonphan_line_ids")
    def _compute_phanthuc1(self):
        for record in self:
            seen = set()
            parts = []
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón thúc 1":
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        # Get the color from product.template; fallback to a default color if not set
                        color = line.phan_id.color or "#000000"
                        parts.append(f"<span style='color: {color};'><strong>{line.phan_id.abbre}</strong></span> {line.soluong:,.0f}kg")
            record.phanthuc1 = " & ".join(parts)

    @api.depends('bonphan_line_ids')
    def _compute_money_lot(self):
        for record in self:
            seen = set()
            total = 0
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón lót" and line.phan_id:
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        total += (line.soluong or 0) * (line.phan_id.standard_price or 0)
            record.money_lot = total

    @api.depends('bonphan_line_ids')
    def _compute_money_thuc1(self):
        for record in self:
            seen = set()
            total = 0
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón thúc 1" and line.phan_id:
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        total += (line.soluong or 0) * (line.phan_id.standard_price or 0)
            record.money_thuc1 = total

    @api.depends('bonphan_line_ids')
    def _compute_phanthuc2(self):
        for record in self:
            seen = set()
            parts = []
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón thúc 2":
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        # Get the color from product.template; fallback to a default color if not set
                        color = line.phan_id.color or "#000000"
                        parts.append(f"<span style='color: {color};'><strong>{line.phan_id.abbre}</strong></span> {line.soluong:,.0f}kg")
            record.phanthuc2 = " & ".join(parts)

    @api.depends('bonphan_line_ids')
    def _compute_money_thuc2(self):
        for record in self:
            seen = set()
            total = 0
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón thúc 2" and line.phan_id:
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        total += (line.soluong or 0) * (line.phan_id.standard_price or 0)
            record.money_thuc2 = total

    @api.depends("bonphan_line_ids")
    def _compute_phanthuc3(self):
        for record in self:
            seen = set()
            parts = []
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón thúc 3":
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        # Get the color from product.template; fallback to a default color if not set
                        color = line.phan_id.color or "#000000"
                        parts.append(f"<span style='color: {color};'><strong>{line.phan_id.abbre}</strong></span> {line.soluong_lo:,.0f}kg")
            record.phanthuc3 = " & ".join(parts)

    @api.depends('bonphan_line_ids')
    def _compute_money_thuc3(self):
        for record in self:
            total = 0
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón thúc 3" and line.phan_id:
                    total += (line.soluong_lo or 0) * (line.phan_id.standard_price or 0)
            record.money_thuc3 = total

    @api.depends("bonphan_line_ids")
    def _compute_bonla1(self):
        for record in self:
            seen = set()
            parts = []
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón lá 1":
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        color = line.phan_id.color or "#000000"
                        parts.append(f"<span style='color: {color};'><strong>{line.phan_id.abbre}</strong></span> {line.soluong_lo:,.0f}kg")
            record.bonla1 = " & ".join(parts)

    @api.depends('bonphan_line_ids')
    def _compute_money_bonla1(self):
        for record in self:
            total = 0
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón lá 1" and line.phan_id:
                    total += (line.soluong_lo or 0) * (line.phan_id.standard_price or 0)
            record.money_bonla1 = total

    @api.depends("bonphan_line_ids")
    def _compute_bonla2(self):
        for record in self:
            seen = set()
            parts = []
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón lá 2":
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        color = line.phan_id.color or "#000000"
                        parts.append(f"<span style='color: {color};'><strong>{line.phan_id.abbre}</strong></span> {line.soluong_lo:,.0f}kg")
            record.bonla2 = " & ".join(parts)

    @api.depends('bonphan_line_ids')
    def _compute_money_bonla2(self):
        for record in self:
            total = 0
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón lá 2" and line.phan_id:
                    total += (line.soluong_lo or 0) * (line.phan_id.standard_price or 0)
            record.money_bonla2 = total

    @api.depends("bonphan_line_ids")
    def _compute_bonla3(self):
        for record in self:
            seen = set()
            parts = []
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón lá 3":
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        color = line.phan_id.color or "#000000"
                        parts.append(f"<span style='color: {color};'><strong>{line.phan_id.abbre}</strong></span> {line.soluong_lo:,.0f}kg")
            record.bonla3 = " & ".join(parts)

    @api.depends('bonphan_line_ids')
    def _compute_money_bonla3(self):
        for record in self:
            total = 0
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón lá 3" and line.phan_id:
                    total += (line.soluong_lo or 0) * (line.phan_id.standard_price or 0)
            record.money_bonla3 = total

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
    @api.depends('lomi_id.N_need', 'lomi_id.P_need','lomi_id.K_need','bonphan_line_ids')
    def _compute_phan(self):
        for record in self:
            N_need=record.lomi_id.N_need if record.lomi_id else 0
            P_need=record.lomi_id.P_need if record.lomi_id else 0   
            K_need=record.lomi_id.K_need if record.lomi_id else 0
            record.N=sum(line.P for line in record.bonphan_line_ids)
            record.N_add = N_need - record.N
            record.P=sum(line.P for line in record.bonphan_line_ids)
            record.P_add = P_need - record.P
            record.K=sum(line.K for line in record.bonphan_line_ids)
            record.K_add = K_need - record.K
                
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
    color = fields.Integer(string='Color')

class Kieuhang(models.Model):
    _name = 'kieuhang'
    _description = 'Kiểu hàng'

    name = fields.Char(string="Tên kiểu hàng")