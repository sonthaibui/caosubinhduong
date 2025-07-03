from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)
# Wizard to set multiple rubber prices at once
class RubberPriceWizard(models.TransientModel):
    _name = 'rubber.price.wizard'
    _description = 'Set Multiple Rubber Prices'

    daily_ids = fields.Many2many('res.partner', string='Đại lý',
        domain=[('is_customer', '=', True)])    
    to_ids = fields.Many2many('hr.department', string='Tổ', 
        domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22'), ('name', 'not ilike', 'Tổ mì')])
    price_type_ids = fields.Many2many('rubber.price.type', string='Loại giá')    
    
    ngay_hieuluc = fields.Date('Ngày hiệu lực', default=fields.Date.today)
    ngay_hieuluc_old = fields.Many2one('rubber.price.wizard.line', string='Ngày hiệu lực cũ')

    price_line_ids = fields.One2many('rubber.price.wizard.line', 'wizard_id', string='Giá mủ')
         
    #filter rubber.price.wizard.line in the range of rubber.price.wizard
    @api.onchange('daily_ids', 'to_ids', 'price_type_ids', 'ngay_hieuluc')
    def onchange_params(self):
        # Clear current wizard lines
        self.price_line_ids = [(5, 0, 0)]
        # Build domain for rubber.price
        price_domain = []
        if self.daily_ids:
            price_domain.append(('daily_id', 'in', self.daily_ids.ids))
        if self.to_ids:
            price_domain.append(('to_id', 'in', self.to_ids.ids))
        if self.price_type_ids:
            price_domain.append(('price_type_id', 'in', self.price_type_ids.ids))
        if self.ngay_hieuluc:
            price_domain.append(('ngay_hieuluc', '=', self.ngay_hieuluc))
        # Fetch matching rubber.price records
        price_lines = self.env['rubber.price'].search(price_domain)
        # Prepare wizard lines
        wizard_lines = []
        seen = set()
        for price in price_lines:
            key = (price.ngay_hieuluc, price.price_type_id.id, price.to_id.id, price.daily_id.id)
            if key in seen:
                continue
            seen.add(key)
            wizard_lines.append((0, 0, {
                'price_id': price.id,
                'price_type_id': price.price_type_id.id,
                'old_price': price.gia,
                'new_price': price.gia,
                'daily_id': price.daily_id.id,
                'to_id': price.to_id.id,
                'ngay_hieuluc': price.ngay_hieuluc,
                'macdinh': price.macdinh,
            }))
        self.price_line_ids = wizard_lines

        # --- For ngay_hieuluc_old ---
        old_date_domain = []
        if self.daily_ids:
            old_date_domain.append(('daily_id', 'in', self.daily_ids.ids))
        if self.to_ids:
            old_date_domain.append(('to_id', 'in', self.to_ids.ids))
        if self.price_type_ids:
            old_date_domain.append(('price_type_id', 'in', self.price_type_ids.ids))
        # Do NOT include ('ngay_hieuluc', '=', self.ngay_hieuluc) here

        # Find unique ngay_hieuluc from rubber.price matching the domain
        ngay_hieuluc_list = self.env['rubber.price'].search(old_date_domain).mapped('ngay_hieuluc')
        unique_dates = list(set(ngay_hieuluc_list))
        # Find any wizard.line with those dates (one per date)
        wizard_line_domain = [('ngay_hieuluc', 'in', unique_dates)]
        return {
            'domain': {'ngay_hieuluc_old': wizard_line_domain}
        }

    #Thay đổi ngày hiệu lực cũ sẽ cập nhật ngày hiệu lực mới
    @api.onchange('ngay_hieuluc_old')
    def _onchange_set_ngay_hieuluc(self):
        if self.ngay_hieuluc_old:
            self.ngay_hieuluc = self.ngay_hieuluc_old.ngay_hieuluc
    
    
    #Khi bấm nút "Lưu giá", sẽ lưu tất cả các giá đã thay đổi
    def save_prices(self):
        for line in self.price_line_ids:
            vals = {
                'ngay_hieuluc': line.ngay_hieuluc,
                'to_id': line.to_id.id,
                'daily_id': line.daily_id.id,
                'price_type_id': line.price_type_id.id,
                'gia': line.new_price,
                'macdinh': line.macdinh,
            }
            # Check for existing record
            existing = self.env['rubber.price'].search([
                ('ngay_hieuluc', '=', line.ngay_hieuluc),
                ('to_id', '=', line.to_id.id),
                ('daily_id', '=', line.daily_id.id),
                ('price_type_id', '=', line.price_type_id.id),
            ], limit=1)
            if existing:
                existing.write(vals)
            else:
                self.env['rubber.price'].create(vals)

    def delete_selected_prices(self):
        lines_to_delete = self.price_line_ids.filtered('select')
        count = 0
        for line in lines_to_delete:
            if line.price_id:
                line.price_id.unlink()
                count += 1
            line.unlink()  # Remove the wizard line as well
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Xóa giá',
                'message': f'Đã xóa {count} giá mủ.',
                'type': 'success',
                'sticky': False,
            }
        }   
    
class RubberPriceWizardLine(models.TransientModel):
    _name = 'rubber.price.wizard.line'
    _description = 'Rubber Price Wizard Line'
    
    wizard_id = fields.Many2one('rubber.price.wizard', string='Wizard')
    price_id = fields.Many2one('rubber.price', string='Giá gốc')
    price_type_id = fields.Many2one('rubber.price.type', string='Loại giá')
    old_price = fields.Float('Giá hiện tại', digits='Product Price', readonly=True)
    new_price = fields.Float('Giá mới', digits='Product Price')
    #changed = fields.Boolean(compute='_compute_changed', store=True)
    
    # Added fields for per-line customization
    daily_id = fields.Many2one('res.partner', string='Đại lý')    
    to_id = fields.Many2one('hr.department', string='Tổ')
    ngay_hieuluc = fields.Date('Áp dụng từ', required=True)
    macdinh = fields.Boolean('Mặc định')    
    select = fields.Boolean('Chọn xóa')  # Add this field

    def name_get(self):
        result = []
        for rec in self:
            name = rec.ngay_hieuluc and rec.ngay_hieuluc.strftime('%d.%m.%y') or 'No Date'
            result.append((rec.id, name))
        return result

    
    def unlink(self):
        for line in self:
            _logger.info(f"Wizard line {line.id} price_id: {line.price_id.id}")
            if line.price_id:
                _logger.info(f"Deleting rubber.price {line.price_id.id}")
                line.price_id.unlink()
        return super().unlink()
    
    @api.constrains('ngay_hieuluc', 'price_type_id', 'to_id', 'daily_id')
    def _check_unique_line(self):
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('wizard_id', '=', rec.wizard_id.id),  # Only check within the current wizard
                ('ngay_hieuluc', '=', rec.ngay_hieuluc),
                ('price_type_id', '=', rec.price_type_id.id),
                ('to_id', '=', rec.to_id.id),
                ('daily_id', '=', rec.daily_id.id),
            ]
            duplicate = self.search(domain, limit=1)
            if duplicate:
                raise ValidationError(
                    "A wizard line with the same 'ngay_hieuluc', 'price_type_id', 'to_ids', and 'daily_ids' already exists."
                )

    @api.constrains('macdinh', 'price_type_id', 'to_ids', 'ngay_hieuluc', 'wizard_id')
    def _check_unique_macdinh_line(self):
        for line in self:
            if line.macdinh:                
                # Find other lines in the same wizard with the same price_type_id, ngay_hieuluc, and this to_id
                domain = [
                    ('macdinh', '=', True),
                    ('price_type_id', '=', line.price_type_id.id),
                    ('to_id', '=', line.to_id.id),
                    ('ngay_hieuluc', '=', line.ngay_hieuluc),
                    ('wizard_id', '=', line.wizard_id.id),
                    ('id', '!=', line.id),
                ]
                if self.search_count(domain):
                    raise ValidationError(
                        "Chỉ được phép lấy giá một đại lý làm mặc định cho mỗi loại giá, trong cùng tổ và ngày hiệu lực trong wizard. "
                        f"Tổ bị trùng: {line.to_id.name}"
                    )
    