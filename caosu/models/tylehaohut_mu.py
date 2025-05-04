from odoo import models, fields

class TyleHaoHutMu(models.Model):
    _name = 'tylehaohut.mu'
    _description = 'Tỷ lệ hao hụt mủ theo thời gian'

    date = fields.Date('Ngày áp dụng', required=True)
    field_code = fields.Selection([
        ('nuoc_haohut', 'Mũ nước hao hụt'),
        ('tap_haohut', 'Mũ tạp hao hụt'),
        ('day_haohut', 'Mũ dây hao hụt'),
        ('dong_haohut', 'Mũ đông hao hụt'),
        ('chen_haohut', 'Mũ chén hao hụt'),
        ('do_haohut', 'Độ hao hụt'),
    ], string='Loại hao hụt', required=True)
    tylehaohut1 = fields.Float('Tỷ lệ hao hụt 1 (%)', required=True)
    tylehaohut2 = fields.Float('Tỷ lệ hao hụt 2 (%)', required=True)
    color1 = fields.Char('Màu dưới ngưỡng 1', default='#008000')  # green
    color2 = fields.Char('Màu giữa ngưỡng 1 và 2', default='#A0522D')  # brown
    color3 = fields.Char('Màu trên ngưỡng 2', default='#FF0000')  # red