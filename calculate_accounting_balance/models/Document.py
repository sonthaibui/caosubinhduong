from odoo import api, models, fields

class Document(models.Model):
    _inherit = "document.document"

    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:', default="0")
    taonguoi = fields.Char(compute='_compute_taonguoi', string='Tạo Người:', default="0")
    xac_nhan = fields.Boolean(compute='_compute_xac_nhan', string='Xac Nhan', default=True)
    
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
        self.taonguoi = str(self.create_uid.id)
