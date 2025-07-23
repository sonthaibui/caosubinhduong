from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
import logging
_logger = logging.getLogger(__name__)

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def name_get(self):
        """Override name_get to hide default code for Mũ products"""
        result = []
        for product in self:
            name = product.name
            # Always hide code for 'Mũ' category products, or when context requests it
            hide_code = (
                self._context.get('hide_default_code', False) or 
                (product.categ_id and product.categ_id.name == 'Mũ')
            )
            
            if not hide_code and self._context.get('display_default_code', True) and product.default_code:
                name = '[%s] %s' % (product.default_code, name)
                
            result.append((product.id, name))
        return result

class RubberHarvest(models.Model):
    _name = 'rubber.harvest'
    _description = 'Temporary model for migration'
    # Add basic fields
    name = fields.Char()

class RubberDeliver(models.Model):
    _name = 'rubber.deliver'
    _description = 'Rubber Deliver Model'

    ngay = fields.Date('Ngày giao', related='rubberbydate_id.ngay')
    ngay_giao = fields.Date(string='Ngày giao', compute='_compute_ngay_giao', store=True)    
    to_id = fields.Many2one('hr.department', string ='Tổ', related='rubberbydate_id.to', store=True)
    to_name = fields.Char(string='Tổ', related='to_id.name', store=True)    
    daily = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer','=',True)],
                default=lambda self: self.env['res.partner'].search([('is_customer','=',True),('name','=','Xe nhà')], limit=1))
    daily_id = fields.Many2one('res.partner', string='Đại Lý', domain=[('is_customer','=',True)], required=True,
                default=lambda self: self.env['res.partner'].search([('is_customer','=',True),('name','=','Xe nhà')], limit=1))
    daily_name = fields.Char('Tên đại lý', related='daily_id.name')
    daily_ban = fields.Many2one('res.partner', string='Đại lý', compute='_compute_daily_ban', inverse='_inverse_daily_ban', readonly=False)
    _daily_ban_manual = fields.Many2one('res.partner', string='Đại lý bán (manual)', store=True)
    sanpham = fields.Selection([
        ('nuoc', 'Mũ nước'), ('tap', 'Mũ tạp'), ('day', 'Mũ dây'), ('dong', 'Mũ đông'), ('chen', 'Mũ chén')
    ], string='Sản phẩm', required=True, default='nuoc')
    product_id = fields.Many2one(
        'product.product', 
        string='MŨ',
        domain=[('categ_id.name', '=', 'Mũ')],
        required=True
    )
    product_name_only = fields.Char(
        string='MŨ Display', 
        related='product_id.name', 
        readonly=True,
        store=False
    )
    product_name = fields.Char(related='product_id.name', string='MŨ', readonly=True)
    soluong = fields.Float('Số lượng', default='0', digits='Product Price')
    do = fields.Float('Độ', default='0', digits='One Decimal')
    quykho = fields.Float('Quykhô', default='0', digits='Product Price', compute='_compute_quykho')
    soluongtt = fields.Float('SL thực', default='0', digits='Product Price')
    dott = fields.Float('Độ thực', default='0', digits='One Decimal')
    quykhott = fields.Float('QK thực', default='0', digits='Product Price', compute='_compute_quykhott')
    do_lythuyet = fields.Float('Độ lý thuyết', compute='_compute_do_lythuyet', digits='One Decimal')
    do_thu = fields.Float('Độ thử', digits='One Decimal')
    state = fields.Selection([
        ('luu','Chưa lưu'),('chua', 'Chưa giao'), ('giao', 'Đã giao'), ('mua', 'Mua mũ'), ('nhan', 'Đã nhận'), ('order', 'Đã order')], string='Trạng thái',
        copy=False, default='chua', index=True, readonly=True,
        help="Trạng thái của mũ.")
    rubberbydate_id = fields.Many2one('rubber.date', string='Nhập sản lượng', ondelete='cascade')
    company_truck_id = fields.Many2one('company.truck', string='Xe công ty', ondelete='set null')
    tyle = fields.Float(compute='_compute_tyle', string='Tỷ lệ (%)')
    is_selected = fields.Boolean(
        'Selected', 
        default=False, 
        compute='_compute_is_selected',
        inverse='_inverse_is_selected',
        store=True,
        help="Select this line for batch operations. Cannot select lines that already have orders."
    )
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', copy=False, ondelete='set null')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', copy=False, ondelete='set null')

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to handle giaomu for new records"""
        records = super().create(vals_list)
        # Process each record individually to avoid affecting other records
        for rec in records:
            if rec.to_id and rec.to_id.id != 81:
                rec.giaomu()
        return records
        
    def write(self, vals):
        # If no actual field changes are being made, skip validation
        if not vals:
            return super().write(vals)
            
        # Skip validation for new records (records without real IDs)
        existing_records = self.filtered(lambda r: r.id and not isinstance(r.id, type(self.env['rubber.deliver'].new()._origin.id)))
        
        for rec in existing_records:
            # Only validate if this record is actually being modified with protected fields
            protected_fields = {'daily_id', 'daily_ban', 'product_id', 'soluong', 'do'}
            
            # Check if any protected field is actually being changed for this specific record
            fields_being_changed = []
            for field in protected_fields:
                if field in vals:
                    current_value = getattr(rec, field)
                    new_value = vals[field]
                    # For Many2one fields, compare IDs
                    if hasattr(current_value, 'id'):
                        current_value = current_value.id
                    if current_value != new_value:
                        fields_being_changed.append(field)
            
            # Skip validation if no protected fields are actually being changed for this record
            if not fields_being_changed:
                continue
                
            if rec.state == 'order':
                if any(field in vals for field in protected_fields):
                    raise UserError(_(
                        "Bạn không thể chỉnh sửa khi đã tạo đơn hàng. Hãy yêu cầu kế toán thay đổi trạng thái của đơn hàng."
                    ))
            elif rec.state == 'nhan':
                # Allow editing daily_id if user is in admin group
                # Use custom admin group for rubber.deliver
                admin_group = self.env.ref('caosu.group_rubber_deliver_admin')
                is_admin = admin_group in self.env.user.groups_id #checks if the retrieved admin group is present in the current user's list of groups (self.env.user.groups_id). The result is a boolean value: True if the user is an administrator, False otherwise.
                # If editing daily_id and not admin, block
                if any(field in vals for field in protected_fields - {'daily_ban'}):
                    raise UserError(_(
                        "Bạn không thể chỉnh sửa khi trạng thái đã nhận. Hãy yêu cầu tài xế thay đổi trạng thái của lệnh trước khi chỉnh sửa."
                    ))
                if 'daily_ban' in vals and not is_admin:
                    raise UserError(_(
                        "Chỉ admin mới có thể sửa Đại lý bán."
                    ))
            elif rec.state == 'giao':
                # Allow editing dott, soluongtt if user is in admin group or truck group
                admin_group = self.env.ref('caosu.group_rubber_deliver_admin')
                truck_group = self.env.ref('caosu.group_rubber_deliver_truck')
                is_admin = admin_group in self.env.user.groups_id
                is_truck = truck_group in self.env.user.groups_id
                # Only allow editing 'soluongtt' and 'dott' for admin or truck group
                allowed_fields = {'soluongtt', 'dott'}
                if any(field in vals for field in protected_fields - allowed_fields):
                    raise UserError(_(
                        "Bạn không thể chỉnh sửa khi trạng thái đã giao. Phải sửa trạng thái chưa giao mới chỉnh sửa được"
                    ))
                if any(field in vals for field in allowed_fields) and not (is_admin or is_truck):
                    raise UserError(_(
                        "Chỉ admin hoặc tài xế mới có thể sửa Số lượng thực nhận hoặc Độ thực nhận."
                    ))

            elif rec.state == 'chua':
                # Only creator can modify certain fields
                creator_only_fields = {'soluong', 'do', 'product_id', 'daily_id'}
                current_user_id = self.env.user.id
                admin_group = self.env.ref('caosu.group_rubber_deliver_admin')
                is_admin = admin_group in self.env.user.groups_id
                if any(field in vals for field in creator_only_fields):
                    if rec.create_uid.id != current_user_id and not is_admin:
                        raise UserError(_(
                            "Bạn không có quyền chỉnh sửa các trường này. Chỉ người tạo lệnh và admin mới có thể chỉnh sửa các trường này."
                        ))            
        res = super().write(vals)
        return res

    def unlink(self):
        for record in self:
            # Check user permissions: only allow delete for create user or user_id = 43
            current_user_id = self.env.user.id
            if current_user_id != 43 and record.create_uid.id != current_user_id:
                raise UserError(_("Bạn không được quyền xóa lệnh này. Chỉ người tạo hoặc quản trị viên mới có thể xóa lệnh này."))                        
            elif record.state not in ['chua', 'giao', 'mua']:
                raise UserError(_("Bạn không thể xóa. Lệnh này đã được xe nhận hoặc đã được tạo hóa đơn."))
            
        return super().unlink()
    @api.depends('ngay')
    def _compute_ngay_giao(self):
        for rec in self:
            rec.ngay_giao = rec.ngay    
    
    @api.depends('quykhott')
    def _compute_tyle(self):
        for rec in self:
            rec.tyle = 0
            rbs = self.env['rubber.deliver'].search([('product_id','=',rec.product_id.id),('ngay','=',rec.ngay)])
            qktt = 0
            if len(rbs) > 0:
                for rb in rbs:
                    qktt += rb.quykhott
                if qktt > 0:
                    rec.tyle = rec.quykhott / qktt

    @api.depends('daily_id', 'company_truck_id', '_daily_ban_manual')
    def _compute_daily_ban(self):
        for record in self:
            # Default: daily_ban = daily_id
            if record._daily_ban_manual:
                record.daily_ban = record._daily_ban_manual
            else: 
                record.daily_ban = record.daily_id            
                # If daily_id is "Xe nhà", apply special logic
                if (record.daily_id and record.daily_id.name == 'Xe nhà' and record.company_truck_id) or (record.to_id and record.to_name == 'TỔ Xe tải' and record.company_truck_id):
                    # Search for rubber.sell records with the same company_truck_id and product
                    sell_records = self.env['rubber.sell'].search([
                        ('company_truck_id', '=', record.company_truck_id.id),
                        ('product_id', '=', record.product_id.id)
                    ])
                    
                    # If exactly one sell record exists, use its daily_id
                    if len(sell_records) == 1:
                        record.daily_ban = sell_records.daily_id
                    else:
                        # If no sell records or multiple sell records, set to False
                        record.daily_ban = False
    def _inverse_daily_ban(self):
        for rec in self:
            # Save the manually set value to a real field (e.g., a new field: daily_ban_manual)
            rec._daily_ban_manual = rec.daily_ban.id
    
    @api.depends('ngay', 'product_id', 'daily_id', 'to_id', 'quykhott', 'soluongtt')
    def _compute_do_lythuyet(self):
        for rec in self:
            do_lythuyet = 0
            # Skip computation for new records without ID
            if not rec.id or isinstance(rec.id, type(self.env['rubber.deliver'].new()._origin.id)):
                rec.do_lythuyet = do_lythuyet
                continue
                
            # Find all previous rubber.deliver records matching the criteria and created before this record
            domain = [
            ('ngay', '=', rec.ngay),
            ('product_id.default_code', '=', rec.product_id.default_code),
            '|',
            ('daily_id.name', '=', 'Xe nhà'),
            ('to_id', '=', 81),
            ('id', '<=', rec.id),  # Only records created before this one
            ]
            prev_delivers = self.env['rubber.deliver'].search(domain)
            sum_quykhott = sum(line.quykhott for line in prev_delivers)
            sum_soluongtt = sum(line.soluongtt for line in prev_delivers)
            if sum_soluongtt > 0:
                do_lythuyet = sum_quykhott / sum_soluongtt * 100
            rec.do_lythuyet = do_lythuyet
    
    def giaomu(self):
        for rec in self:
            # Only allow creator or admin group to perform this action
            current_user_id = self.env.user.id
            admin_group = self.env.ref('caosu.group_rubber_deliver_admin')
            is_admin = admin_group in self.env.user.groups_id
            if rec.create_uid.id != current_user_id and not is_admin:
                raise UserError(_("Bạn không có quyền giao mũ. Chỉ người tạo hoặc admin mới có thể thực hiện thao tác này."))
            if rec.state == 'chua':                   
                # Find a truck with the same date as the delivery
                truck = self.env['company.truck'].search([
                    ('ngaygiao', '=', rec.ngay)
                ], limit=1)                
                
                # If no truck exists for this date, create a new one
                if not truck:
                    truck = self.env['company.truck'].create({
                        'ngaygiao': rec.ngay,
                        'ngayban': rec.ngay,
                    })  
                
                # Update all required fields                
                rec.soluongtt = rec.soluong
                rec.dott = rec.do                
                rec.company_truck_id = truck.id
                rec.state = 'giao'
        
    def sualai(self):
        for rec in self:
            # Permission checks based on state
            admin_group = self.env.ref('caosu.group_rubber_deliver_admin')
            truck_group = self.env.ref('caosu.group_rubber_deliver_truck')
            is_admin = admin_group in self.env.user.groups_id
            is_truck = truck_group in self.env.user.groups_id
            is_creator = rec.create_uid.id == self.env.user.id

            if rec.state == 'order':
                if not is_admin:
                    raise UserError(_("Chỉ admin mới có thể sửa khi đã tạo đơn hàng."))
            elif rec.state == 'nhan':
                if not (is_admin or is_truck):
                    raise UserError(_("Chỉ admin hoặc tài xế mới có thể sửa khi đã nhận mũ."))
            elif rec.state == 'giao':
                if not (is_admin or is_creator):
                    raise UserError(_("Chỉ admin hoặc người tạo mới có thể sửa khi đã giao mũ."))

            if rec.state == 'order':
                # Direct access to the order line - no search needed
                if rec.sale_order_line_id:
                    order_line = rec.sale_order_line_id
                    sale_order = order_line.order_id

                    # Check if order is in an editable state
                    if sale_order.state not in ['draft', 'cancel']:
                        raise UserError(_(
                            "Cannot revert: the sales order is in '{}' state. Please cancel the sales order first."
                        ).format(sale_order.state))

                    # If we can proceed, unlink the order line
                    line_count = len(sale_order.order_line)
                    order_line.unlink()

                    if line_count == 1:
                        sale_order.unlink()

                # Update state and clear references
                rec.sale_order_id = False
                rec.sale_order_line_id = False
                if rec.to_id and rec.company_truck_id.to_id and rec.to_id == rec.company_truck_id.to_id:
                    rec.state = 'mua'
                else:    
                    rec.state = 'nhan'

            elif rec.state == 'nhan':
                rec.state = 'giao'
            elif rec.state == 'giao':
                rec.state = 'chua'
                rec.company_truck_id = False        

    def nhanmu(self):
        for rec in self:
            # Only allow users in admin or truck group to perform this action
            admin_group = self.env.ref('caosu.group_rubber_deliver_admin')
            truck_group = self.env.ref('caosu.group_rubber_deliver_truck')
            is_admin = admin_group in self.env.user.groups_id
            is_truck = truck_group in self.env.user.groups_id
            if not (is_admin or is_truck):
                raise UserError(_("Chỉ admin hoặc tài xế mới có thể nhận mũ."))
            if rec.state == 'giao':
                rec.state = 'nhan'
                if rec.soluongtt == 0:
                    rec.soluongtt = rec.soluong
                if rec.dott == 0:    
                    rec.dott = rec.do

    @api.depends('soluong', 'do')
    def _compute_quykho(self):
        for rec in self:
            rec.quykho = rec.soluong * rec.do / 100

    @api.depends('soluongtt', 'dott')
    def _compute_quykhott(self):
        for rec in self:
            rec.quykhott = rec.soluongtt * rec.dott / 100
    
    @api.depends('state')
    def _compute_is_selected(self):
        """Automatically uncheck selection if state becomes 'order'"""
        for record in self:
            if record.state == 'order':
                record.is_selected = False
            # Keep current value for other states

    def _inverse_is_selected(self):
        """Prevent selection of lines with state='order'"""
        for record in self:
            if record.state == 'order' and record.is_selected:
                record.is_selected = False
                # Optionally show a warning
                return {
                    'warning': {
                        'title': _('Không thể chọn'),
                        'message': _('Dòng này đã có đơn hàng, không thể chọn lại.')
                    }
                }
        
    def order(self):
        """Only allow admin group to create sale order for rubber.deliver line"""
        admin_group = self.env.ref('caosu.group_rubber_deliver_admin')
        if admin_group not in self.env.user.groups_id:
            raise UserError(_("Chỉ admin mới được phép tạo đơn hàng."))

        """Create sale order for single rubber.deliver line"""
        self.ensure_one()
        
        if not self.daily_ban:
            raise UserError(_("Line for product %s has no partner (daily_id).") % self.product_id.name)
        
        if self.state == 'order':
            raise UserError(_("This line is already ordered."))
        
        # Get analytic account from to_id
        analytic_account_id = self.to_id.analytic_account_id.id if self.to_id and self.to_id.analytic_account_id else False
        
        # Check for existing orders with same criteria
        domain = [
            ('partner_id', '=', self.daily_ban.id),
            ('commitment_date', '=', self.ngay),
            ('state', 'in', ['draft', 'sent']),  # Only consider draft/sent orders
        ]
        
        # Add to_id to domain if it exists
        if self.to_id:
            domain.append(('analytic_account_id', '=', analytic_account_id))
        
        existing_order = self.env['sale.order'].search(domain, limit=1)
        
        if existing_order:
            # Use existing order
            sale_order = existing_order
        else:
            # Create sale order
            sale_order_vals = {
                'partner_id': self.daily_ban.id,
                'date_order': self.ngay,
                'commitment_date': self.ngay,
                'expected_date': self.ngay,
                'analytic_account_id': analytic_account_id,
            }
            
            sale_order = self.env['sale.order'].create(sale_order_vals)
        
        # Get price using helper method
        price, price_type_code = self._get_rubber_price()
        
        # Create order line based on price type
        if price_type_code == 'giamutap':
            order_line = self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': self.product_id.id,
                'product_uom_qty': self.soluongtt,
                'price_unit': price,
                'commitment_date': self.ngay,
            })
        else:
            order_line = self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': self.product_id.id,
                'sanluong': self.soluongtt,
                'do': self.dott,
                'product_uom_qty': self.dott * self.soluongtt / 100,
                'price_unit': price,
                'commitment_date': self.ngay,
            })
        
        # Update the rubber.deliver line to mark it as processed
        self.write({
            'sale_order_id': sale_order.id,
            'sale_order_line_id': order_line.id,
            'state': 'order'
        })
        
        return {
            'name': _('Sale Order Created'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'target': 'current',
        }
    
    def _get_rubber_price(self):
        """Get rubber price for this delivery line"""
        self.ensure_one()
        
        domain = [
            ('daily_id', '=', self.daily_id.id),             
            ('ngay_hieuluc', '<', self.ngay),
            ('to_id', '=', self.to_id.id)                      
        ]       
        
        # Try to determine price type from product_id first
        if self.product_id and self.product_id.default_code:
            code = self.product_id.default_code
            if code == 'munuoc':
                domain.append(('price_type_id.code', '=', 'giamunuoc'))
            elif code == 'mutap':
                domain.append('|')
                domain.append(('price_type_id.code', '=', 'giamutap'))
                domain.append(('price_type_id.code', '=', 'giamutap_do'))
            elif code == 'mudong':
                domain.append(('price_type_id.code', '=', 'giamudong'))
            elif code == 'muday':
                domain.append(('price_type_id.code', '=', 'giamuday'))
            elif code == 'muchen':
                domain.append(('price_type_id.code', '=', 'giamuchen'))
        else:
            domain.append(('price_type_id.code', '=', ''))
        
        price = self.env['rubber.price'].search(domain, limit=1)
        
        if price:
            if price.price_type_id.code == 'giamutap_do' or price.price_type_id.code == 'giamunuoc':
                return price.gia * 100, price.price_type_id.code
            else:
                return price.gia, price.price_type_id.code
        return 0, None

class RubberSell(models.Model):
    _name = 'rubber.sell'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Rubber Sell Model'

    ngay = fields.Date('Ngày', default=fields.Datetime.now(), required=True, store=True)
    daily = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer','=',True)], required=True,
        default=lambda self: self.env['res.partner'].search([('is_customer','=',True)], limit=1))
    daily_id = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer','=',True)], required=True,
        default=lambda self: self.env['res.partner'].search([('is_customer','=',True)], limit=1))
    
    sanpham = fields.Selection([
        ('nuoc', 'Mũ nước'), ('tap', 'Mũ tạp'), ('day', 'Mũ dây'), ('dong', 'Mũ đông'), ('chen', 'Mũ chén')
    ], string='Sản phẩm', required=True, default='nuoc')
    product_id = fields.Many2one(
        'product.product', 
        string='MŨ',
        domain=[('categ_id.name', '=', 'Mũ')],
        required=True
    )
    product_name_only = fields.Char(
        string='MŨ Display', 
        related='product_id.name', 
        readonly=True,
        store=False
    )
    product_name = fields.Char(related='product_id.name', string='MŨ', readonly=True)
    soluong = fields.Float('SL bán', default='0', digits='Product Price')
    do = fields.Float('Độ bán', default='0', digits='One Decimal')
    quykho = fields.Float('QK bán', default='0', digits='Product Price', compute='_compute_quykho')
    company_truck_id = fields.Many2one('company.truck', string='Xe công ty', ondelete='cascade', required=True)
    ngaygiao = fields.Date(related='company_truck_id.ngaygiao')
    dailygiao = fields.Char('dailygiao', readonly=True, default='Xe nhà')
    state = fields.Selection([
        ('chua', 'Chưa order'), ('order', 'order')
    ], string='Trạng thái', default='chua')        
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', copy=False, ondelete='set null')
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', copy=False, ondelete='set null')
    
    @api.depends('soluong','do')
    def _compute_quykho(self):
        for rec in self:
            rec.quykho = rec.soluong * rec.do / 100    
           
    def order(self):
        """Create sale order for single rubber.sell line"""
        self.ensure_one()
        if self.state == 'order':
            raise UserError(_("This line is already ordered."))
        if not self.daily_id:
            raise UserError(_("No customer (daily_id) set for this line."))
        # Check for existing draft/sent sale order for this customer and date
        ngaygiao = self.company_truck_id.ngaygiao
        domain = [
            ('partner_id', '=', self.daily_id.id),
            ('commitment_date', '=', ngaygiao),
            ('state', 'in', ['draft', 'sent']),
        ]
        # Debug: log the domain and ngay/ngaygiao values
        
        '''_logger.info('RubberSell order() domain: %s', domain)
        _logger.info('RubberSell order() self.ngay: %s, self.ngaygiao: %s', self.ngay, self.ngaygiao)'''
        
        existing_order = self.env['sale.order'].search(domain, limit=1)
        if existing_order:
            sale_order = existing_order
        else:
            partner = self.daily_id
            pricelist_id = partner.property_product_pricelist.id or self.env['product.pricelist'].search([], limit=1).id
            addr = partner.address_get(['delivery', 'invoice'])
            partner_invoice_id = addr['invoice']
            partner_shipping_id = addr['delivery']
            sale_order = self.env['sale.order'].create({
                'partner_id': partner.id,
                'date_order': self.ngay,
                'commitment_date': ngaygiao,
                'expected_date': ngaygiao,
                'pricelist_id': pricelist_id,
                'partner_invoice_id': partner_invoice_id,
                'partner_shipping_id': partner_shipping_id,
            })
        # Create sale order line
        order_line = self.env['sale.order.line'].create({
            'order_id': sale_order.id,
            'product_id': self.product_id.id,
            'product_uom_qty': self.soluong,
            'price_unit': self._get_sell_price(ngaygiao),
            'commitment_date': ngaygiao,
        })
        raise UserError(f"{order_line.id} - {order_line.product_id} - {order_line.price_unit} - {order_line.product_uom_qty}")
        self.message_post(body=f"Debug info: sale_order={sale_order.id}, order_line={order_line.id}")
        # Mark as ordered and set sale order references
        self.write({
            'state': 'order',
            'sale_order_id': sale_order.id,
            'sale_order_line_id': order_line.id,
        })
        return {
            'name': _('Sale Order Created'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': sale_order.id,
            'target': 'current',
        }

    def _get_sell_price(self, ngaygiao):
        """Get price for this sell line (mimics deliver logic)"""
        self.ensure_one()
        domain = [
            ('daily_id', '=', self.daily_id.id),
            ('ngay_hieuluc', '<', ngaygiao),
        ]
        # Try to determine price type from product_id first
        if self.product_id and self.product_id.default_code:
            code = self.product_id.default_code
            if code == 'munuoc':
                domain.append(('price_type_id.code', '=', 'giamunuoc'))
            elif code == 'mutap':
                domain.append('|')
                domain.append(('price_type_id.code', '=', 'giamutap'))
                domain.append(('price_type_id.code', '=', 'giamutap_do'))
            elif code == 'mudong':
                domain.append(('price_type_id.code', '=', 'giamudong'))
            elif code == 'muday':
                domain.append(('price_type_id.code', '=', 'giamuday'))
            elif code == 'muchen':
                domain.append(('price_type_id.code', '=', 'giamuchen'))
        else:
            domain.append(('price_type_id.code', '=', ''))
        price = self.env['rubber.price'].search(domain, limit=1)
        if price:
            if price.price_type_id.code == 'giamutap_do' or price.price_type_id.code == 'giamunuoc':
                return price.gia * 100
            else:
                return price.gia
        return 0

    def sualai(self):
        """Revert sale order and sale order line for this rubber.sell record if possible."""
        for rec in self:
            if rec.state == 'order':
                if rec.sale_order_line_id:
                    order_line = rec.sale_order_line_id
                    sale_order = order_line.order_id
                    # Only allow revert if sale order is in draft or cancel
                    if sale_order.state not in ['draft', 'cancel']:
                        raise UserError(_(
                            "Cannot revert: the sales order is in '{}' state. Please cancel the sales order first."
                        ).format(sale_order.state))
                    # Unlink the order line
                    line_count = len(sale_order.order_line)
                    order_line.unlink()
                    if line_count == 1:
                        sale_order.unlink()
                # Clear references and reset state
                rec.sale_order_id = False
                rec.sale_order_line_id = False
                rec.state = 'chua'
            # Optionally handle other state transitions if needed
class RubberLoss(models.Model):
    _name = 'rubber.loss'
    _description = 'Rubber Loss Model'

    ngay = fields.Date('Ngày')
    to = fields.Char('Tổ')
    hhnuoc = fields.Float('Hao hụt nước', default='0', digits='One Decimal')
    hhdo = fields.Float('Hao hụt độ', default='0', digits='One Decimal')
    hhtap = fields.Float('Hao hụt tạp', default='0', digits='One Decimal')
    hhdong = fields.Float('Hao hụt đông', default='0', digits='One Decimal')
    hhday = fields.Float('Hao hụt dây', default='0', digits='One Decimal')
    company_truck_id = fields.Many2one('company.truck', string='Xe công ty', ondelete='cascade')