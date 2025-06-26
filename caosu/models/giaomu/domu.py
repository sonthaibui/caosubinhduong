from odoo import api, fields, models, _

class DoMu(models.Model):
    _name = 'do.mu'
    _description = 'Độ mủ theo thời gian'
    _order = "ngay_hieuluc desc, create_date desc"

    to = fields.Many2many('hr.department', string='Tổ',
        relation='do_mu_hr_department_rel',
        column1='do_mu_id',
        column2='department_id',
        domain=[('name', 'like', 'TỔ ')],
        required=True)
    ngay_hieuluc = fields.Date('Ngày hiệu lực', default=fields.Date.today, required=True)
    do_mutap = fields.Float('Độ mủ tạp', digits='Product Price')
    do_muday = fields.Float('Độ mủ dây', digits='Product Price')
    do_mudong = fields.Float('Độ mủ đông', digits='Product Price')
    do_muchen = fields.Float('Độ mủ chén', digits='Product Price')
    ghi_chu = fields.Text('Ghi chú')
    name = fields.Char(compute='_compute_name', string='Tên', store=True)

    @api.depends('to', 'ngay_hieuluc')
    def _compute_name(self):
        for rec in self:
            to_names = ", ".join(rec.to.mapped('name')) if rec.to else "All"
            date_str = rec.ngay_hieuluc.strftime('%d/%m/%Y') if rec.ngay_hieuluc else ""
            rec.name = f"{to_names}_{date_str}"

    @api.model
    def get_do(self, to_ids, ngay=False):
        """Lấy độ mủ áp dụng cho tổ vào một ngày cụ thể"""
        if not ngay:
            ngay = fields.Date.today()
        domain = [
            ('to', 'in', to_ids),
            ('ngay_hieuluc', '<=', ngay)
        ]
        record = self.search(domain, order='ngay_hieuluc desc', limit=1)
        if record:
            return {
                'do_mutap': record.do_mutap,
                'do_muday': record.do_muday,
                'do_mudong': record.do_mudong,
                'do_muchen': record.do_muchen,
            }
        return {}
