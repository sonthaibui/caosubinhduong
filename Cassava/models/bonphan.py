from odoo import api, models, fields

class Giaidoan(models.Model):
    _name = 'giaidoan'
    _description = 'Giai đoạn'

    name = fields.Char(string="Name", required=True)

    @api.model
    def create(self, vals):
        if not vals.get('name'):
            vals['name'] = 'Bón lót'
        return super(Giaidoan, self).create(vals)

class Loaiphan(models.Model):
    _name = 'loaiphan'
    _description = 'Loại Phân'

    ngaybon = fields.Date(string="Ngày bón", required=True)
    phan_id = fields.Many2one('product.template', string="Phân", domain="[('categ_id.name', '=', 'VẬT TƯ PHÂN BÓN')]")
    abbre = fields.Char(string="Phân", related='phan_id.abbre')
    soluong = fields.Float(string="Số lượng", digits=(16, 0))
    donvi = fields.Many2one('uom.uom', string="Đơn vị", related='phan_id.uom_id', store=True)
    bonphan_id = fields.Many2one('bonphan', string="Bón phân", required=True, ondelete='cascade')
    kieubon_id = fields.Many2one('kieubon', string="Kiểu bón")
class BonPhan(models.Model):
    _name = 'bonphan'
    _description = 'Bon Phan'

    lomi_ids = fields.Many2many('lomi', 'bonphan_lomi_rel', 'bonphan_id', 'lomi_id', string="Lomi", required=True)    
    giaidoan_id = fields.Many2one('giaidoan', string="Giai đoạn", required=True, store=True)
    loaiphan_line_ids = fields.One2many('loaiphan', 'bonphan_id', string="Loại phân")
    bonphan_line_ids = fields.One2many('bonphan.line', 'bonphan_id', string="Bonphan Line")    
    ngay = fields.Datetime(string="Ngày")
    hang_avg = fields.Float(string="Số hàng TB", compute='_compute_hang_avg', store=True)
    hang_actual = fields.Float(string="Số hàng TT", store=True, default=lambda self: self.hang_avg)
    sohom_avg = fields.Float(string="Số hom TB", compute='_compute_sohom_avg', store=True)
    sohom_actual = fields.Float(string="Số hom TT", store=True, default=lambda self: self.sohom_avg)

    @api.depends('lomi_ids')
    def _compute_sohom_avg(self):
        for record in self:
            total_sohom = sum(lomi.sohom for lomi in record.lomi_ids)
            count = len(record.lomi_ids)
            record.sohom_avg = total_sohom / count if count > 0 else 0

    @api.depends('lomi_ids')
    def _compute_hang_avg(self):
        for record in self:
            total_soluong = sum(lomi.sohang for lomi in record.lomi_ids)
            count = len(record.lomi_ids)
            record.hang_avg = total_soluong / count if count > 0 else 0

    @api.model
    def create(self, vals):
        record = super(BonPhan, self).create(vals)
        record._create_bonphan_lines()
        return record

    def write(self, vals):
        res = super(BonPhan, self).write(vals)
        if 'loaiphan_line_ids' in vals or 'lomi_ids' in vals:
            self._create_bonphan_lines()
        return res

    def _create_bonphan_lines(self):
        self.ensure_one()
        bonphan_line_obj = self.env['bonphan.line']
        existing_lines = self.bonphan_line_ids
        kieuhang_records = self.env['kieuhang'].search([])
        if not kieuhang_records:
            return

        # Remove bonphan.line records that are no longer related to any loaiphan.line
        existing_phan_ids = self.loaiphan_line_ids.mapped('phan_id.id')
        lines_to_remove = existing_lines.filtered(lambda l: l.phan_id.id not in existing_phan_ids)
        lines_to_remove.unlink()

        for kieuhang in kieuhang_records:
            for line in self.loaiphan_line_ids:
                hangmi_ids = self.env['hangmi'].search([
                    ('lomi_id', 'in', self.lomi_ids.ids),
                    ('kieuhang_id', '=', kieuhang.id)
                ]).ids
                existing_line = existing_lines.filtered(lambda l: l.phan_id.id == line.phan_id.id and l.giaidoan_id.id == self.giaidoan_id.id and l.kieuhang_id.id == kieuhang.id)
                if existing_line:
                    existing_line.write({
                        'lomi_ids': [(6, 0, self.lomi_ids.ids)],
                        'hangmi_ids': [(6, 0, hangmi_ids)],
                        'soluong_lo': line.soluong,  # Ensure this field is updated correctly
                        'kieubon_id': line.kieubon_id.id,
                        'ngaybon': line.ngaybon
                    })
                else:
                    bonphan_line_obj.create({
                        'bonphan_id': self.id,
                        'phan_id': line.phan_id.id,
                        'giaidoan_id': self.giaidoan_id.id,                        
                        'lomi_ids': [(6, 0, self.lomi_ids.ids)],
                        'hangmi_ids': [(6, 0, hangmi_ids)],
                        'kieuhang_id': kieuhang.id,
                        'soluong_lo': line.soluong,  # Ensure this field is set correctly
                        'kieubon_id': line.kieubon_id.id,
                        'ngaybon': line.ngaybon
                        # Add other fields and formulas here
                    })




