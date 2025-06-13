from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class RubberPrice(models.Model):
    _name = 'rubber.price'
    _description = 'Rubber Price Model'
    _rec_name = 'name'
    _order = "ngay_hieuluc desc, create_date desc"
    
    to = fields.Many2many('hr.department', string='Tổ', 
        relation='rubber_price_hr_department_rel',
        column1='price_id',
        column2='department_id',
        domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22'), ('name', 'not ilike', 'Tổ mì')], 
        required=True)
    
    daily = fields.Many2one('res.partner', string='Đại lý', 
        domain=[('is_customer', '=', 'True')], 
        required=True, ondelete='restrict',
        default=lambda self: self.env['res.partner'].search([('is_customer', '=', 'True')], limit=1))
       
    
    gia = fields.Float('Giá', digits='Product Price', required=True)
    ngay_hieuluc = fields.Date('Ngày hiệu lực', default=fields.Date.today, required=True)
    macdinh = fields.Boolean('Mặc định', default=False, help="Đặt đại lý này làm mặc định cho loại mũ này")
    ghi_chu = fields.Text('Ghi chú')
    name = fields.Char(compute='_compute_name', string='name', store=True)
    price_type_id = fields.Many2one('rubber.price.type', string='Loại giá', required=True)
    
    _sql_constraints = [
        ('unique_price_record',
         'UNIQUE(price_type_id, to, daily, ngay_hieuluc)',
         'A price record for this type, department, dealer and date already exists!')
    ]
    
    @api.depends('to', 'daily', 'price_type_id', 'ngay_hieuluc', 'gia')
    def _compute_name(self):
        for rec in self:
            to_names = ", ".join(rec.to.mapped('name')) if rec.to else "All"
            price_type_name = rec.price_type_id.name if rec.price_type_id else ""
            daily_name = rec.daily.name if rec.daily else ""
            date_str = rec.ngay_hieuluc.strftime('%d/%m/%Y') if rec.ngay_hieuluc else ""
            rec.name = f"{daily_name}_{price_type_name}_{to_names}_{date_str}_{rec.gia:,.0f}"

    @api.constrains('to', 'daily', 'price_type_id', 'ngay_hieuluc')
    def _check_rubberdate_unique(self):
        for record in self:
            if not (record.to and record.daily and record.price_type_id and record.ngay_hieuluc):
                continue
            dublicate_price = self.search([
                ('to', 'in', record.to.ids),
                ('daily', '=', record.daily.id),
                ('price_type_id', '=', record.price_type_id.id),
                ('ngay_hieuluc', '=', record.ngay_hieuluc),
                ('id', '!=', record.id)
            ])
            if dublicate_price:
                raise ValidationError(
                    f"Giá cho {', '.join(record.to.mapped('name'))} đại lý {record.daily.name} loại {record.price_type_id.name} đã tồn tại cho ngày {record.ngay_hieuluc.strftime('%d/%m/%Y')}!"
                )
    
    @api.constrains('macdinh', 'price_type_id', 'to')
    def _check_default(self):
        for rec in self:
            if rec.macdinh:
                other_defaults = self.search([
                    ('id', '!=', rec.id),
                    ('to', 'in', rec.to.ids),
                    ('price_type_id', '=', rec.price_type_id.id),
                    ('macdinh', '=', True)
                ])
                if other_defaults:
                    other_defaults.write({'macdinh': False})
    
    @api.model
    def get_price(self, price_type_id, to_ids, daily_id=False, ngay=False):
        """Lấy giá áp dụng cho đại lý vào một ngày cụ thể"""
        if not ngay:
            ngay = fields.Date.today()
        domain = [
            ('price_type_id', '=', price_type_id),
            ('to', 'in', to_ids),
            ('ngay_hieuluc', '<=', ngay)
        ]
        # First try with specific daily
        if daily_id:
            daily_price = self.search([
                ('daily', '=', daily_id),
                *domain
            ], order='ngay_hieuluc desc', limit=1)
            if daily_price:
                return daily_price.gia
        # Fall back to default daily
        default_price = self.search([
            ('macdinh', '=', True),
            *domain
        ], order='ngay_hieuluc desc', limit=1)
        if default_price:
            return default_price.gia
        return 0.0

    @api.model
    def create(self, vals):
        res = super(RubberPrice, self).create(vals)
        # Trigger price recalculation for affected records
        res._update_affected_rubberdate_records()
        return res

    def write(self, vals):
        res = super(RubberPrice, self).write(vals)
        # Trigger price recalculation if price-related fields changed
        if any(field in vals for field in ['mu', 'gia', 'to', 'daily', 'ngay_hieuluc', 'macdinh']):
            self._update_affected_rubberdate_records()
        return res

    def _update_affected_rubberdate_records(self):
        """Update rubberdate records affected by this price change"""
        for price in self:
            # Find all records from the effective date onward with matching team and product type
            domain = [
                ('ngay', '>=', price.ngay_hieuluc),
                ('to', 'in', price.to.ids),
                ('price_type_id', '=', price.price_type_id.id)
            ]
            affected_records = self.env['rubber.date'].search(domain)
            for record in affected_records:
                if hasattr(record, '_compute_gia'):
                    record._compute_gia()
                if hasattr(record, '_compute_tien'):
                    record._compute_tien()

    def action_open_price_wizard(self):
        """Open the rubber price wizard"""
        return {
            'type': 'ir.actions.act_window',
            'name': _('Cập nhật giá mủ'),
            'res_model': 'rubber.price.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_daily_id': self.daily.id if self.daily else False,
                'default_to_ids': self.to.ids if self.to else [],
                'default_ngay_hieuluc': fields.Date.today(),
            },
        }