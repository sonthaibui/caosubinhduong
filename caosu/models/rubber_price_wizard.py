from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)

class RubberPriceWizard(models.TransientModel):
    _name = 'rubber.price.wizard'
    _description = 'Set Multiple Rubber Prices'

    daily_id = fields.Many2one('res.partner', string='Đại lý', 
        domain=[('is_customer', '=', 'True')], 
        required=True,
        default=lambda self: self.env['res.partner'].search([('is_customer', '=', 'True')], limit=1))
    
    to_ids = fields.Many2many('hr.department', string='Tổ', 
        domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22'), ('name', 'not ilike', 'Tổ mì')], 
        required=True)
        
    ngay_hieuluc = fields.Date('Ngày hiệu lực', default=fields.Date.today, required=True)
    macdinh = fields.Boolean('Mặc định', default=False)
    ghi_chu = fields.Text('Ghi chú')
    
    price_line_ids = fields.One2many('rubber.price.wizard.line', 'wizard_id', string='Giá mũ')
    
    @api.onchange('daily_id', 'to_ids', 'ngay_hieuluc')
    def _onchange_params(self):
        if not self.daily_id or not self.to_ids:
            return
            
        ProductTemplate = self.env['product.template']
        RubberPrice = self.env['rubber.price']
            
        # Define the five standard rubber product names
        product_names = [
            'mũ nước', 
            'mũ chén', 
            'mũ dây', 
            'mũ đông', 
            'mũ tạp'
        ]
        
        # Clear existing lines and recreate
        self.price_line_ids = [(5, 0, 0)]
        line_vals = []
        
        # Process each product type
        for product_name in product_names:
            # Find the product by name
            product = ProductTemplate.search([
                '|', 
                ('name', '=ilike', product_name),
                ('name', '=ilike', product_name.capitalize())
            ], limit=1)
            
            # If product not found, create it
            if not product:
                try:
                    product = ProductTemplate.create({
                        'name': product_name.capitalize(),
                        'type': 'product',
                    })
                except Exception as e:
                    # Log error and continue with next product
                    _logger.error(f"Failed to create product {product_name}: {e}")
                    continue

            # Ensure we have a valid product before continuing
            if not product or not product.id:
                _logger.error(f"No valid product found for {product_name}")
                continue
            
            # Find most recent price for this product
            price = 0
            for team in self.to_ids:
                price_record = RubberPrice.search([
                    ('mu', '=', product.id),
                    ('to', 'in', team.id),
                    ('daily', '=', self.daily_id.id),
                    ('ngay_hieuluc', '<=', self.ngay_hieuluc)
                ], order='ngay_hieuluc desc', limit=1)
                
                if price_record:
                    price = price_record.gia
                    break
                    
            # If no specific price found, try default
            if not price:
                for team in self.to_ids:
                    price_record = RubberPrice.search([
                        ('mu', '=', product.id),
                        ('to', 'in', team.id),
                        ('macdinh', '=', True),
                        ('ngay_hieuluc', '<=', self.ngay_hieuluc)
                    ], order='ngay_hieuluc desc', limit=1)
                    
                    if price_record:
                        price = price_record.gia
                        break
            
            # Create new line with default values from wizard header
            line_vals.append((0, 0, {
                'product_id': product.id,
                'old_price': price,
                'new_price': price,
                # Default values from header
                'ngay_hieuluc': self.ngay_hieuluc,
                'macdinh': self.macdinh,
                'daily_id': self.daily_id.id,
                # Leave to_id empty for individual selection
            }))
            
        # Add new lines
        self.price_line_ids = line_vals
    
    def save_prices(self):
        RubberPrice = self.env['rubber.price']
        created_records = self.env['rubber.price']
        
        # Process each price line
        for line in self.price_line_ids:
            if not line.changed:
                # Skip unchanged prices
                continue
                
            # Determine effective values for this line
            daily = line.daily_id or self.daily_id
            ngay = line.ngay_hieuluc or self.ngay_hieuluc
            is_default = line.macdinh if line.macdinh != self.macdinh else self.macdinh
            
            # If line has specific team, use it, otherwise apply to all selected teams
            teams_to_use = [line.to_id] if line.to_id else self.to_ids
            
            # Create/update a price record for each team
            for team in teams_to_use:
                # Skip if no team (shouldn't happen but as safeguard)
                if not team:
                    continue
                    
                # Check if a record already exists for this date
                existing = RubberPrice.search([
                    ('mu', '=', line.product_id.id),
                    ('to', 'in', team.id),
                    ('daily', '=', daily.id),
                    ('ngay_hieuluc', '=', ngay)
                ])
                
                if existing:
                    # Update existing
                    existing.write({
                        'gia': line.new_price,
                        'macdinh': is_default,
                        'ghi_chu': self.ghi_chu
                    })
                    created_records |= existing
                else:
                    # Create new
                    new_record = RubberPrice.create({
                        'mu': line.product_id.id,
                        'to': [(4, team.id)],
                        'daily': daily.id,
                        'gia': line.new_price,
                        'ngay_hieuluc': ngay,
                        'macdinh': is_default,
                        'ghi_chu': self.ghi_chu
                    })
                    created_records |= new_record
        
        # Show notification and return to the form
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%s price records updated') % len(created_records),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }


class RubberPriceWizardLine(models.TransientModel):
    _name = 'rubber.price.wizard.line'
    _description = 'Rubber Price Wizard Line'
    
    wizard_id = fields.Many2one('rubber.price.wizard', string='Wizard')
    product_id = fields.Many2one('product.template', string='Mũ', required=True, ondelete='cascade')
    old_price = fields.Float('Giá hiện tại', digits='Product Price', readonly=True)
    new_price = fields.Float('Giá mới', digits='Product Price', required=True)
    changed = fields.Boolean(compute='_compute_changed', store=True)
    
    # Added fields for per-line customization
    to_id = fields.Many2one('hr.department', string='Tổ',
        domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22'), ('name', 'not ilike', 'Tổ mì')])
    daily_id = fields.Many2one('res.partner', string='Đại lý',
        domain=[('is_customer', '=', 'True')])
    ngay_hieuluc = fields.Date('Áp dụng từ')
    macdinh = fields.Boolean('Mặc định')
    
    # Expand what "changed" means
    @api.depends('old_price', 'new_price', 'to_id', 'daily_id', 'ngay_hieuluc', 'macdinh')
    def _compute_changed(self):
        for line in self:
            # If any value is set differently from the wizard default, consider it changed
            wizard = line.wizard_id
            line.changed = (line.old_price != line.new_price or 
                          (line.to_id and line.to_id.id) or
                          (line.daily_id and line.daily_id != wizard.daily_id) or
                          (line.ngay_hieuluc and line.ngay_hieuluc != wizard.ngay_hieuluc) or
                          (line.macdinh != wizard.macdinh))