from odoo import models, fields, api

class BonphanLine(models.Model):
    _name = 'bonphan.line'
    _description = 'Bón phân Line'
    
    giaidoan_id = fields.Many2one('giaidoan', string="Giai đoạn", store=True)    
    phan_id = fields.Many2one('product.template', string="Phân", domain="[('categ_id.name', '=', 'VẬT TƯ PHÂN BÓN')]")
    abbre = fields.Char(string="Tên phân", related='phan_id.abbre', store=True)
    kieuhang_id = fields.Many2one('kieuhang', string="Kiểu hàng", required=True)  # Add this field
    soluong_lo = fields.Float(string="SLG lô", digits=(16, 0))
    soluong = fields.Float(string="SLG", compute='_compute_kg', digits=(16, 0))
    tyle_day = fields.Float(string="TL đáy", digits=(16, 2), store=True)
    tyle_mat = fields.Float(string="TL mặt", digits=(16, 2), store=True)
    kg_hang = fields.Float(string="Phân-hàng", compute='_compute_kg_hang', digits=(16, 0), store=True)
    kg_hang_display = fields.Char(string="Phân-hàng (kg)", compute='_compute_kg_display')
    kg_mat = fields.Float(string="Phân-mặt", compute='_compute_kg', digits=(16, 0), store=True)
    kg_day = fields.Float(string="Phân-đáy ", compute='_compute_kg', digits=(16, 0), store=True)
    kg_hom = fields.Float(string="Phân-1hom", compute='_compute_kg_hom', digits=(16, 0))
    total_sohom = fields.Float(string="Tổng hom/lô", digits=(16, 0))
    N = fields.Float(string="N", compute='_compute_phan', digits=(16, 0))
    P = fields.Float(string="P", compute='_compute_phan', digits=(16, 0))
    K = fields.Float(string="K", compute='_compute_phan', digits=(16, 0))
    Ca = fields.Float(string="Ca", compute='_compute_phan', digits=(16, 0))
    Mg = fields.Float(string="Mg", compute='_compute_phan', digits=(16, 0))
    Si = fields.Float(string="Si", compute='_compute_phan', digits=(16, 0))
    OM = fields.Float(string="OM", compute='_compute_phan', digits=(16, 0))
    Humic = fields.Float(string="Humic", compute='_compute_phan', digits=(16, 0))
    lomi_ids = fields.Many2many('lomi', 'bonphan_line_lomi_rel', 'bonphan_line_id', 'lomi_id', string="Lô mì", required=True)
    hangmi_ids = fields.Many2many('hangmi', 'bonphan_line_hangmi_rel', 'bonphan_line_id', 'hangmi_id', string="Hàng mì", required=True)
    bonphan_id = fields.Many2one('bonphan', string="Bón phân", required=True, ondelete='cascade')
    
    '''@api.model
    def name_get(self):
        result = []
        for record in self:
            name = record.phan.abbre if record.phan and hasattr(record.phan, 'abbre') else 'No Product'
            result.append((record.id, name))
        return result'''
    @api.depends('kg_hang')
    def _compute_kg_display(self):
        for record in self:
            record.kg_hang_display = f"{record.kg_hang} kg"
    @api.depends('bonphan_id.hang_actual', 'soluong_lo')
    def _compute_kg_hang(self): 
        for record in self:
            record.kg_hang = record.soluong_lo / record.bonphan_id.hang_actual if record.bonphan_id.hang_actual else 0
    @api.depends('bonphan_id.hang_actual', 'soluong_lo')
    def _compute_kg_hom(self): 
        for record in self:
            record.kg_hom = record.soluong_lo * 1000 / record.bonphan_id.sohom_actual if record.bonphan_id.sohom_actual else 0

    @api.depends('soluong', 'phan_id')
    def _compute_phan(self):
        for record in self:
            if record.phan_id:
                record.N = record.soluong * record.phan_id.N
                record.P = record.soluong * record.phan_id.P
                record.K = record.soluong * record.phan_id.K
                record.Ca = record.soluong * record.phan_id.Ca
                record.Mg = record.soluong * record.phan_id.Mg
                record.Si = record.soluong * record.phan_id.Si
                record.OM = record.soluong * record.phan_id.OM
                record.Humic = record.soluong * record.phan_id.Humic
            else:
                record.N = 0
                record.P = 0
                record.K = 0
                record.Ca = 0
                record.Mg = 0
                record.Si = 0
                record.OM = 0
                record.Humic = 0

    @api.depends('hangmi_ids', 'kg_hang', 'tyle_day', 'tyle_mat')
    def _compute_kg(self):
        for record in self:
            record.kg_mat = record.kg_hang * record.tyle_mat if record.tyle_mat else 0
            record.kg_day = record.kg_hang * record.tyle_day if record.tyle_day else 0
            if record.hangmi_ids:
                average_sohang = sum(hangmi.sohang for hangmi in record.hangmi_ids) / len(record.hangmi_ids)
                record.soluong = record.kg_hang * average_sohang
            else:
                record.soluong = 0
                         
            
