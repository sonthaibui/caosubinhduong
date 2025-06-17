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
    show_ngay_hieuluc_suggestions = fields.Boolean(string="Hiển thị ngày hiệu lực đã có")
    ngay_hieuluc_suggestions = fields.Html(string='Ngày hiệu lực đã có', readonly=True)

    price_line_ids = fields.One2many('rubber.price.wizard.line', 'wizard_id', string='Giá mũ')
    
    #filter rubber.price.wizard.line in the range of rubber.price.wizard
    @api.onchange('daily_ids', 'to_ids', 'ngay_hieuluc')
    def _onchange_params(self):
        domain = []
        if self.daily_ids:
            domain.append(('daily_ids', 'in', self.daily_ids.ids))
        if self.to_ids:
            domain.append(('to_ids', 'in', self.to_ids.ids))
        if self.ngay_hieuluc:
            domain.append(('ngay_hieuluc', '=', self.ngay_hieuluc))
        if domain:
            price_lines = self.env['rubber.price.wizard.line'].search(domain)
            # Set old_price = new_price for each found line
            for line in price_lines:
                line.old_price = line.new_price
            self.price_line_ids = [(6, 0, price_lines.ids)]
        else:
            self.price_line_ids = [(5, 0, 0)]

    #Khi bấm nút "Lưu giá", sẽ lưu tất cả các giá đã thay đổi
    def save_prices(self):
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
                        }
                        if price:
                            price.write(vals)
                            created_or_updated_count += 1
                        else:
                            RubberPrice.create(vals)
                            created_or_updated_count += 1
        
        # Show notification and return to the form
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Success'),
                'message': _('%s price records updated') % created_or_updated_count,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
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

    @api.onchange('show_ngay_hieuluc_suggestions', 'price_type_ids')
    def _onchange_show_ngay_hieuluc_suggestions(self):
        if self.show_ngay_hieuluc_suggestions:
            lines = self.env['rubber.price.wizard.line'].search([
                ('price_type_id', 'in', self.price_type_ids.ids)
            ])
            dates = lines.mapped('ngay_hieuluc')
            unique_dates = sorted(set(dates))
            if unique_dates:
                self.ngay_hieuluc_suggestions = (
                    "<b>Ngày hiệu lực đã có:</b> " +
                    " - ".join(d.strftime('%d.%m.%y') for d in unique_dates if d) + ";"
                )
            else:
                self.ngay_hieuluc_suggestions = "<i>Chưa có ngày hiệu lực nào.</i>"
        else:
            self.ngay_hieuluc_suggestions = False

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

