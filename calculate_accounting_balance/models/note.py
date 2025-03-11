from odoo import api, models, fields

class Note(models.Model):
    _inherit = "note.note"

    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:', default="0")
    taonguoi = fields.Char(compute='_compute_taonguoi', string='Tạo Người:', default="0")
    xac_nhan = fields.Boolean(compute='_compute_xac_nhan', string='Xac Nhan', default=True)
    lomi_ids = fields.Many2many(
        comodel_name='lomi',
        relation='lomi_note_rel',
        column1='note_id',
        column2='lomi_id',
        string="Lô mì"
    )
    
    @api.depends('nguoitao','taonguoi')
    def _compute_xac_nhan(self):
        if self.nguoitao == self.taonguoi:
            self.xac_nhan = True
        else:
            self.xac_nhan = False
    
    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)

    @api.model
    def _compute_taonguoi(self):
        self.taonguoi = str(self.user_id.id)