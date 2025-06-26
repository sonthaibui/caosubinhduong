from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class RubberPrice(models.Model):
    _name = 'rubber.price'
    _description = 'Rubber Price Model'
    _rec_name = 'name'
    _order = "ngay_hieuluc desc, create_date desc"
    
    to_id = fields.Many2one('hr.department', string='Tổ', 
        domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22'), ('name', 'not ilike', 'Tổ mì')], 
        required=True, ondelete='restrict')
    
    daily_id = fields.Many2one('res.partner', string='Đại lý', 
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
         'UNIQUE(price_type_id, to_id, daily_id, ngay_hieuluc)',
         'A price record for this type, department, dealer and date already exists!')
    ]
    
    @api.depends('to_id', 'daily_id', 'price_type_id', 'ngay_hieuluc', 'gia')
    def _compute_name(self):
        for rec in self:
            to_name = rec.to_id.name if rec.to_id else "All"
            price_type_name = rec.price_type_id.name if rec.price_type_id else ""
            daily_name = rec.daily_id.name if rec.daily_id else ""
            date_str = rec.ngay_hieuluc.strftime('%d/%m/%Y') if rec.ngay_hieuluc else ""
            rec.name = f"{daily_name}_{price_type_name}_{to_name}_{date_str}_{rec.gia:,.0f}"

    @api.constrains('to', 'daily', 'price_type_id', 'ngay_hieuluc')
    def _check_rubberdate_unique(self):
        for record in self:
            if not (record.to_id and record.daily_id and record.price_type_id and record.ngay_hieuluc):
                continue
            duplicate_price = self.search([
                ('to_id', '=', record.to_id.id),
                ('daily_id', '=', record.daily_id.id),
                ('price_type_id', '=', record.price_type_id.id),
                ('ngay_hieuluc', '=', record.ngay_hieuluc),
                ('id', '!=', record.id)
            ])
            if duplicate_price:
                raise ValidationError(
                    f"Giá cho {', '.join(record.to.mapped('name'))} đại lý {record.daily.name} loại {record.price_type_id.name} đã tồn tại cho ngày {record.ngay_hieuluc.strftime('%d/%m/%Y')}!"
                )
    
    @api.constrains('macdinh', 'price_type_id', 'to_id', 'ngay_hieuluc')
    def _check_unique_macdinh(self):
        for rec in self:
            if rec.macdinh:
                domain = [
                    ('macdinh', '=', True),
                    ('price_type_id', '=', rec.price_type_id.id),
                    ('to_id', '=', rec.to_id.id),
                    ('ngay_hieuluc', '=', rec.ngay_hieuluc),
                    ('id', '!=', rec.id),
                ]
                if self.search_count(domain):
                    raise ValidationError(
                        "Chỉ được phép có một dòng mặc định cho mỗi loại giá, tổ và ngày hiệu lực."
                    )
   
    @api.model
    def create(self, vals):
        res = super(RubberPrice, self).create(vals)
        # Trigger price recalculation for affected records
        res._update_affected_rubberdate_records()
        return res

    def write(self, vals):
        res = super(RubberPrice, self).write(vals)
        # Trigger price recalculation if price-related fields changed
        if any(field in vals for field in ['price_type_id', 'gia', 'to_id', 'daily_id', 'ngay_hieuluc', 'macdinh']):
            self._update_affected_rubberdate_records()
        return res

    def _update_affected_rubberdate_records(self):
        """Update rubberdate records affected by this price change"""
        for price in self:
            # Find all records from the effective date onward with matching team and product type
            domain = [
                ('ngay', '>=', price.ngay_hieuluc),
                ('to', '=', price.to_id.id),                
            ]
            affected_records = self.env['rubber.date'].search(domain)
            for record in affected_records:
                if hasattr(record, '_compute_rubber_price'):
                    record._compute_rubber_price()
                if hasattr(record, '_compute_tien'):
                    record._compute_tien()

    def unlink(self):
        # Collect affected rubber.date records before deleting prices
        RubberDate = self.env['rubber.date']
        affected_dates = RubberDate.browse()
        for price in self:
            # Find rubber.date records related to this price
            dates = RubberDate.search([
                ('to', '=', price.to_id.id),                
                ('ngay', '>=', price.ngay_hieuluc),
            ])
            affected_dates |= dates
        # Unlink the prices
        res = super(RubberPrice, self).unlink()
        # Recompute fields on affected rubber.date records
        if affected_dates:
            affected_dates._compute_rubber_price()
            affected_dates._compute_tien()
        return res    

class RubberPriceType(models.Model):
    _name = 'rubber.price.type'
    _description = 'Rubber Price Type'

    code = fields.Char(string='Code', required=True, unique=True)
    name = fields.Char(string='Name', required=True)

    @api.model
    def create_default_type(self):
        """Create the default price type if none exists."""
        if not self.search([], limit=1):
            self.create({
                'code': 'giamunuoc',
                'name': 'Giá mũ nước',
            })

    @api.model
    def init(self):
        """Ensure default record exists at module install/upgrade."""
        self.create_default_type()