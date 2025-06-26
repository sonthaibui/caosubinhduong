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

    price_line_ids = fields.One2many('rubber.price.wizard.line', 'wizard_id', string='Giá mũ')
         
    #filter rubber.price.wizard.line in the range of rubber.price.wizard
    @api.onchange('daily_ids', 'to_ids', 'price_type_ids', 'ngay_hieuluc')
    def onchange_params(self):
        # --- For price_line_ids ---
        price_line_domain = []
        if self.daily_ids:
            price_line_domain.append(('daily_ids', 'in', self.daily_ids.ids))
        if self.to_ids:
            price_line_domain.append(('to_ids', 'in', self.to_ids.ids))
        if self.price_type_ids:
            price_line_domain.append(('price_type_id', 'in', self.price_type_ids.ids))
        if self.ngay_hieuluc:
            price_line_domain.append(('ngay_hieuluc', '=', self.ngay_hieuluc))
        # ...your logic to update price_line_ids...
        if price_line_domain:
            price_lines = self.env['rubber.price.wizard.line'].search(price_line_domain)
            # Set old_price = new_price for each found line
            for line in price_lines:
                line.old_price = line.new_price
            self.price_line_ids = [(6, 0, price_lines.ids)]
        else:
            self.price_line_ids = [(5, 0, 0)]

        # --- For ngay_hieuluc_old ---
        old_date_domain = []
        if self.daily_ids:
            old_date_domain.append(('daily_ids', 'in', self.daily_ids.ids))
        if self.to_ids:
            old_date_domain.append(('to_ids', 'in', self.to_ids.ids))
        if self.price_type_ids:
            old_date_domain.append(('price_type_id', 'in', self.price_type_ids.ids))
        # Do NOT include ('ngay_hieuluc', '=', self.ngay_hieuluc) here

        return {
            'domain': {'ngay_hieuluc_old': old_date_domain}}

    @api.onchange('ngay_hieuluc_old')
    def _onchange_set_ngay_hieuluc(self):
        if self.ngay_hieuluc_old:
            self.ngay_hieuluc = self.ngay_hieuluc_old.ngay_hieuluc
    
    
    #Khi bấm nút "Lưu giá", sẽ lưu tất cả các giá đã thay đổi
    def save_prices(self):       
        self.ensure_one()
        # Gather all selected params from lines
        all_to_ids = set()
        all_daily_ids = set()
        all_price_type_ids = set()
        all_ngay_hieuluc = set()
        valid_params = set()
        for line in self.price_line_ids:
            all_to_ids.update(line.to_ids.ids)
            all_daily_ids.update(line.daily_ids.ids)
            all_price_type_ids.add(line.price_type_id.id)
            all_ngay_hieuluc.add(line.ngay_hieuluc)
            

        # 1. Unlink all other wizard lines matching these params but not in this wizard
        WizardLine = self.env['rubber.price.wizard.line']
        domain = [
            ('to_ids', 'in', list(all_to_ids)),
            ('daily_ids', 'in', list(all_daily_ids)),
            ('price_type_id', 'in', list(all_price_type_ids)),
            ('ngay_hieuluc', 'in', list(all_ngay_hieuluc)),
            ('wizard_id', '!=', self.id),
        ]
        other_lines = WizardLine.search(domain)
        other_lines.unlink()

        

        for line in self.price_line_ids:
            # Build all valid combinations for this line
            valid_keys = set(
                (to_id, daily_id, line.price_type_id.id, line.ngay_hieuluc)
                for to_id in line.to_ids.ids
                for daily_id in line.daily_ids.ids
            )

            # Find all rubber.price records for this line's ngay_hieuluc, price_type_id, to_ids, daily_ids
            prices = self.env['rubber.price'].search([
                ('ngay_hieuluc', '=', line.ngay_hieuluc),
                ('price_type_id', '=', line.price_type_id.id),
                ('to_id', 'in', line.to_ids.ids),
                ('daily_id', 'in', line.daily_ids.ids),]
            )
            
            # Unlink prices not matching any valid key for this line
            for price in prices:
                key = (price.to_id.id, price.daily_id.id, price.price_type_id.id, price.ngay_hieuluc)
                if key not in valid_keys:
                    price.unlink()
                    
        RubberPrice = self.env['rubber.price']
        created_or_updated_count = 0
        for rec in self:
            for line in rec.price_line_ids:                
                for to in line.to_ids:
                    for daily in line.daily_ids:
                        domain = [
                            ('ngay_hieuluc', '=', line.ngay_hieuluc),
                            ('to_id', '=', to.id),
                            ('daily_id', '=', daily.id),
                            ('price_type_id', '=', line.price_type_id.id),
                        ]
                        price = RubberPrice.search(domain, limit=1)
                        vals = {
                            'ngay_hieuluc': line.ngay_hieuluc,
                            'to_id': to.id,
                            'daily_id': daily.id,
                            'price_type_id': line.price_type_id.id,
                            'gia': line.new_price,  # Adjust if your field is named differently
                            'macdinh': line.macdinh,
                        }
                        if price:
                            price.write(vals)
                            created_or_updated_count += 1
                        else:
                            RubberPrice.create(vals)
                            created_or_updated_count += 1
        
        
        # Show notification and keep the wizard open
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
            'title': _('Success'),
            'message': _('%s price records updated') % created_or_updated_count,
            'type': 'success',
            'sticky': False,
            }
        }

    def action_load_lines(self):
        self.ensure_one()
        PriceLine = self.env['rubber.price.wizard.line']
        for price_type in self.price_type_ids:
            # Find existing line with this price_type and same ngay_hieuluc
            line = self.price_line_ids.filtered(
                lambda l: l.price_type_id == price_type and l.ngay_hieuluc == self.ngay_hieuluc
            )
            if line:
                # Update existing line
                line.daily_ids = [(6, 0, self.daily_ids.ids)]
                line.to_ids = [(6, 0, self.to_ids.ids)]
                line.ngay_hieuluc = self.ngay_hieuluc
            else:
                # Create missing line
                PriceLine.create({
                    'wizard_id': self.id,
                    'price_type_id': price_type.id,
                    'daily_ids': [(6, 0, self.daily_ids.ids)],
                    'to_ids': [(6, 0, self.to_ids.ids)],
                    'ngay_hieuluc': self.ngay_hieuluc,
                })
        # Reopen the wizard to refresh the lines
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rubber.price.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }        

    
class RubberPriceWizardLine(models.TransientModel):
    _name = 'rubber.price.wizard.line'
    _description = 'Rubber Price Wizard Line'
    
    wizard_id = fields.Many2one('rubber.price.wizard', string='Wizard')
    price_type_id = fields.Many2one('rubber.price.type', string='Loại giá')
    old_price = fields.Float('Giá hiện tại', digits='Product Price', readonly=True)
    new_price = fields.Float('Giá mới', digits='Product Price')
    #changed = fields.Boolean(compute='_compute_changed', store=True)
    
    # Added fields for per-line customization
    daily_ids = fields.Many2many('res.partner', string='Đại lý',
        domain=[('is_customer', '=', True)], required =True
        )
    
    to_ids = fields.Many2many('hr.department', string='Tổ', 
        domain=[('name', 'like', 'TỔ '),('name', '!=', 'TỔ 22'), ('name', 'not ilike', 'Tổ mì')], 
        required=True)
    ngay_hieuluc = fields.Date('Áp dụng từ', required=True)
    macdinh = fields.Boolean('Mặc định')    
    
    def name_get(self):
        result = []
        for rec in self:
            name = rec.ngay_hieuluc and rec.ngay_hieuluc.strftime('%d.%m.%y') or 'No Date'
            result.append((rec.id, name))
        return result

    def action_delete_line(self):
        self.unlink()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'rubber.price.wizard',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        } 
    
    def unlink(self):
        RubberPrice = self.env['rubber.price']
        for line in self:
            # Find and delete related rubber.price records
            prices = RubberPrice.search([
                ('ngay_hieuluc', '=', line.ngay_hieuluc),
                ('price_type_id', '=', line.price_type_id.id),
                ('to_id', 'in', line.to_ids.ids),
                ('daily_id', 'in', line.daily_ids.ids),
            ])
            prices.unlink()
        return super(RubberPriceWizardLine, self).unlink()

    @api.constrains('ngay_hieuluc', 'price_type_id', 'to_ids', 'daily_ids')
    def _check_unique_line(self):
        for rec in self:
            domain = [
                ('id', '!=', rec.id),
                ('ngay_hieuluc', '=', rec.ngay_hieuluc),
                ('price_type_id', '=', rec.price_type_id.id),
                ('to_ids', 'in', rec.to_ids.ids),
                ('daily_ids', 'in', rec.daily_ids.ids),
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
                for to in line.to_ids:
                    # Find other lines in the same wizard with the same price_type_id, ngay_hieuluc, and this to_id
                    domain = [
                        ('macdinh', '=', True),
                        ('price_type_id', '=', line.price_type_id.id),
                        ('to_ids', 'in', to.id),
                        ('ngay_hieuluc', '=', line.ngay_hieuluc),
                        ('wizard_id', '=', line.wizard_id.id),
                        ('id', '!=', line.id),
                    ]
                    if self.search_count(domain):
                        raise ValidationError(
                            "Chỉ được phép lấy giá một đại lý làm mặc định cho mỗi loại giá, trong cùng tổ và ngày hiệu lực trong wizard. "
                            f"Tổ bị trùng: {to.name}"
                        )
    