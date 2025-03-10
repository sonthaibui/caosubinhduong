from datetime import date
from odoo import api, models, fields

class Lomi(models.Model):
    _name = 'lomi'
    _description = 'Lô mì'

    #to = fields.Many2one('hr.department', string='Tổ', domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22')], required=True)
    tenlo = fields.Char(string="Lô")
    sohang = fields.Integer(string="Số hàng", compute='_compute_sohang')
    soluongmi = fields.Integer(string="Số luồng", compute='_compute_soluongmi')
    ngaytrong = fields.Date(string="Ngày trồng", compute='_compute_ngaytrong')
    ngaytuoi = fields.Integer(string="Ngày tuổi", compute='_compute_ngaytuoi')
    sohom = fields.Integer(string="Số lượng hom", compute='_compute_sohom')
    N = fields.Float(string="N", compute='_compute_phan', digits=(16, 0))
    P = fields.Float(string="P", compute='_compute_phan', digits=(16, 0))
    K = fields.Float(string="K", compute='_compute_phan', digits=(16, 0))
    N_need = fields.Float(string="N Cần", digits=(16, 0))
    P_need = fields.Float(string="P Cần", digits=(16, 0))
    K_need = fields.Float(string="K Cần", digits=(16, 0))
    N_add = fields.Float(string="N Thiếu", compute='_compute_npk_add', digits=(16, 0))
    P_add = fields.Float(string="P Thiếu", compute='_compute_npk_add', digits=(16, 0))
    K_add = fields.Float(string="K Thiếu", compute='_compute_npk_add', digits=(16, 0))  

    Ca = fields.Float(string="Ca", compute='_compute_phan', digits=(16, 0))
    OM = fields.Float(string="OM", compute='_compute_phan', digits=(16, 0))
    giong = fields.Char(string="Giống", compute='_compute_giong')
    kieutrong = fields.Char(string="Kiểu trồng", compute='_compute_kieutrong')
    hangmi_ids = fields.One2many('hangmi', 'lomi_id', string="Hàng mì")
    bonphan_ids = fields.Many2many('bonphan', 'bonphan_lomi_rel', 'lomi_id', 'bonphan_id', string="Bón phân")
    bonphan_line_ids = fields.Many2many('bonphan.line', 'bonphan_line_lomi_rel', 'lomi_id', 'bonphan_line_id', string="Bón phân Lines")
    phanlot = fields.Html(string="Phân lót", compute="_compute_phanlot")
    money_lot = fields.Float(string="Tiền phân lót", compute='_compute_money_lot', digits=(16, 0))
    phanthuc1 = fields.Html(string="Phân Thúc 1", compute="_compute_phanthuc1")
    money_thuc1 = fields.Float(string="Tiền phân thúc1", compute='_compute_money_thuc1', digits=(16, 0))
    
    @api.depends('bonphan_line_ids')
    def _compute_money_lot(self):
        for record in self:
            seen = set()
            total = 0
            for line in record.bonphan_line_ids:
                if line.giaidoan_id and line.giaidoan_id.name == "Bón lót" and line.phan_id:
                    if line.phan_id.id not in seen:
                        seen.add(line.phan_id.id)
                        total += (line.soluong_lo or 0) * (line.phan_id.standard_price or 0)
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
                        total += (line.soluong_lo or 0) * (line.phan_id.standard_price or 0)
            record.money_thuc1 = total
            
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
                        parts.append(f"<span style='color: {color};'><strong>{line.phan_id.abbre}</strong></span> {line.soluong_lo:,.0f}kg")
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
                        parts.append(f"<span style='color: {color};'><strong>{line.phan_id.abbre}</strong></span> {line.soluong_lo:,.0f}kg")
            record.phanthuc1 = " & ".join(parts)

    def name_get(self):
        result = []
        for record in self:
            name = record.tenlo
            result.append((record.id, name))
        return result
        for record in self:
            name = record.tenlo
            result.append((record.id, name))
        return result
    
    @api.depends('N_need', 'N', 'P_need', 'P', 'K_need', 'K')
    def _compute_npk_add(self):
        for record in self:
            record.N_add = record.N_need - record.N if record.N_need is not None and record.N is not None else 0
            record.P_add = record.P_need - record.P if record.P_need is not None and record.P is not None else 0
            record.K_add = record.K_need - record.K if record.K_need is not None and record.K is not None else 0
    
    @api.depends('hangmi_ids')
    def _compute_sohang(self):
        for record in self:
            record.sohang = sum((line.sohang or 0) for line in record.hangmi_ids)

    @api.depends('hangmi_ids')
    def _compute_soluongmi(self):
        for record in self:
            record.soluongmi = sum((line.soluongmi or 0) for line in record.hangmi_ids)

    @api.depends('hangmi_ids.ngaytrong')
    def _compute_ngaytrong(self):
        for record in self:
            ngaytrong_dates = [line.ngaytrong for line in record.hangmi_ids if line.ngaytrong]
            if ngaytrong_dates:
                record.ngaytrong = min(ngaytrong_dates)
            else:
                record.ngaytrong = False

    @api.depends('ngaytrong')
    def _compute_ngaytuoi(self):
        for record in self:
            if record.ngaytrong:
                record.ngaytuoi = (date.today() - record.ngaytrong).days
            else:
                record.ngaytuoi = 0

    @api.depends('hangmi_ids')
    def _compute_sohom(self):
        for record in self:
            record.sohom = sum(line.sohom for line in record.hangmi_ids)

    @api.depends('hangmi_ids.bonphan_line_ids')
    def _compute_phan(self):
        for record in self:
            if record.bonphan_line_ids:
                record.N = sum(line.N for line in record.bonphan_line_ids)
                record.P = sum(line.P for line in record.bonphan_line_ids)
                record.K = sum(line.K for line in record.bonphan_line_ids)
                record.Ca = sum(line.Ca for line in record.bonphan_line_ids)
                record.OM = sum(line.OM for line in record.bonphan_line_ids)
            else:
                record.N = 0
                record.P = 0
                record.K = 0
                record.Ca = 0
                record.OM = 0

    @api.depends('hangmi_ids.giong_id')
    def _compute_giong(self):
        for record in self:
            if len(record.hangmi_ids) > 1:
                giongs = set(line.giong_id.name for line in record.hangmi_ids if line.giong_id)
                record.giong = " & ".join(giongs) if giongs else 'Chưa xác định'
            elif len(record.hangmi_ids) == 1:
                record.giong = record.hangmi_ids[0].giong_id.name if record.hangmi_ids[0].giong_id else 'Chưa xác định'
            else:
                giong_id = self.env['giongmi'].search([('name', '=', 'Chưa xác định')], limit=1)
                if not giong_id:
                    giong_id = self.env['giongmi'].create({'name': 'Chưa xác định'})
                record.giong = giong_id.name

    @api.depends('hangmi_ids.kieutrong_id')
    def _compute_kieutrong(self):
        for record in self:
            if len(record.hangmi_ids) > 1:
                kieutrong_set = set(hang.kieutrong_id.name for hang in record.hangmi_ids if hang.kieutrong_id)
                record.kieutrong = " & ".join(kieutrong_set) if kieutrong_set else 'Chưa xác định'
            elif len(record.hangmi_ids) == 1:
                record.kieutrong = record.hangmi_ids[0].kieutrong_id.name if record.hangmi_ids[0].kieutrong_id else 'Chưa xác định'
            else:
                kieutrong_id = self.env['kieutrong'].search([('name', '=', 'Chưa xác định')], limit=1)
                if not kieutrong_id:
                    kieutrong = self.env['kieutrong'].create({'name': 'Chưa xác định'})
                record.kieutrong = kieutrong_id.name