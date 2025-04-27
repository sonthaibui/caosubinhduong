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
    
    mu = fields.Many2one('product.template', string='Mũ', 
        domain=['|', '|', '|', '|',
            ('name', 'ilike', 'mũ nước'),
            ('name', 'ilike', 'mũ chén'),
            ('name', 'ilike', 'mũ dây'),
            ('name', 'ilike', 'mũ đông'),
            ('name', 'ilike', 'mũ tạp')
        ], 
        required=True, ondelete='restrict')
    
    gia = fields.Float('Giá', digits='Product Price', required=True)
    ngay_hieuluc = fields.Date('Ngày hiệu lực', default=fields.Date.today, required=True)
    macdinh = fields.Boolean('Mặc định', default=False, help="Đặt đại lý này làm mặc định cho loại mũ này")
    ghi_chu = fields.Text('Ghi chú')
    name = fields.Char(compute='_compute_name', string='name', store=True)
    
    @api.depends('to', 'daily', 'mu', 'ngay_hieuluc', 'gia')
    def _compute_name(self):
        for rec in self:
            to_names = ", ".join(rec.to.mapped('name')) if rec.to else "All"
            mu_name = rec.mu.name if rec.mu else ""
            daily_name = rec.daily.name if rec.daily else ""
            date_str = rec.ngay_hieuluc.strftime('%d/%m/%Y') if rec.ngay_hieuluc else ""
            rec.name = f"{daily_name}_{mu_name}_{to_names}_{date_str}_{rec.gia:,.0f}"

    @api.constrains('to', 'daily', 'mu', 'ngay_hieuluc')
    def _check_rubberdate_unique(self):
        for record in self:
            if not (record.to and record.daily and record.mu and record.ngay_hieuluc):
                continue  # Skip validation if any required field is missing
                
            dublicate_price = self.search([
                ('to', 'in', record.to.ids),
                ('daily', '=', record.daily.id),
                ('mu', '=', record.mu.id),  # Changed from record.mu to record.mu.id for Many2one
                ('ngay_hieuluc', '=', record.ngay_hieuluc),
                ('id', '!=', record.id)
            ])
            if dublicate_price:
                raise ValidationError(f"Giá cho {', '.join(record.to.mapped('name'))} đại lý {record.daily.name} loại {record.mu.name} đã tồn tại cho ngày {record.ngay_hieuluc.strftime('%d/%m/%Y')}!")
    
    @api.constrains('macdinh', 'mu', 'to')
    def _check_default(self):
        # Ensure only one default per rubber type per team
        for rec in self:
            if rec.macdinh:
                other_defaults = self.search([
                    ('id', '!=', rec.id),
                    ('to', 'in', rec.to.ids),
                    ('mu', '=', rec.mu),
                    ('macdinh', '=', True)
                ])
                if other_defaults:
                    # Unmark other defaults
                    other_defaults.write({'macdinh': False})
    
    @api.model
    def get_price(self, mu, to_ids, daily_id=False, ngay=False):
        """Lấy giá áp dụng cho đại lý vào một ngày cụ thể"""
        if not ngay:
            ngay = fields.Date.today()
            
        domain = [
            ('mu', '=', mu),
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
            
        # No price found
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
                ('to', 'in', price.to.ids)
            ]
            
            # Determine which field needs updating based on the product
            product = price.mu
            if not product or not product.name:
                continue
                
            product_name = product.name.lower()
            RubberDate = self.env['rubber.date']
            affected_records = False
            
            # MŨ DÂY
            if 'mũ dây' in product_name:
                domain_day = domain.copy()
                domain_day.extend(['|', ('daily_day', '=', price.daily.id), ('daily_day', '=', False)])
                affected_records = RubberDate.search(domain_day)
                for record in affected_records:
                    record._compute_rubber_prices()
                    record.write({'giaday': record.giaday})
                    
            # MŨ NƯỚC
            elif 'mũ nước' in product_name:
                domain_nuoc = domain.copy()
                domain_nuoc.extend(['|', ('daily_nuoc', '=', price.daily.id), ('daily_nuoc', '=', False)])
                affected_records = RubberDate.search(domain_nuoc)
                for record in affected_records:
                    record._compute_rubber_prices()
                    record.write({'gianuoc': record.gianuoc})
                    
            # MŨ TẠP
            elif 'mũ tạp' in product_name:
                domain_tap = domain.copy()
                domain_tap.extend(['|', ('daily_tap', '=', price.daily.id), ('daily_tap', '=', False)])
                affected_records = RubberDate.search(domain_tap)
                for record in affected_records:
                    record._compute_rubber_prices()
                    record.write({'giatap': record.giatap})
                    
            # MŨ ĐÔNG
            elif 'mũ đông' in product_name:
                domain_dong = domain.copy()
                domain_dong.extend(['|', ('daily_dong', '=', price.daily.id), ('daily_dong', '=', False)])
                affected_records = RubberDate.search(domain_dong)
                for record in affected_records:
                    record._compute_rubber_prices()
                    record.write({'giadong': record.giadong})
                    
            # MŨ CHÉN (typically uses the same dealer as mũ nước)
            elif 'mũ chén' in product_name:
                domain_chen = domain.copy()
                domain_chen.extend(['|', ('daily_nuoc', '=', price.daily.id), ('daily_nuoc', '=', False)])
                affected_records = RubberDate.search(domain_chen)
                for record in affected_records:
                    record._compute_rubber_prices()
                    record.write({'giachen': record.giachen})
                    
            # Update money calculation after price changes
            if affected_records:
                for record in affected_records:
                    if hasattr(record, '_compute_tien'):
                        record._compute_tien()
                        record.write({'tien': record.tien})

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