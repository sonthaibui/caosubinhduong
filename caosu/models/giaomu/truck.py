from collections import defaultdict
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class RubberTruck(models.Model):
    _name = "rubber.truck"
    _description = "Rubber Truck Model"

    daily_id = fields.Many2one('res.partner', string='Đại lý', domain=[('is_customer', '=', 'True')])
    dayban = fields.Float('Mũ dây')
    doban = fields.Float('Độ')
    dongban = fields.Float('Mũ đông')
    nuocban = fields.Float('Mũ nước')
    tapban = fields.Float('Mũ tạp')
    tenxe = fields.Char('Tên xe')
    company_truck_id = fields.Many2one('company.truck', string='Xe công ty')

class CompanyTruck(models.Model):
    _name = "company.truck"
    _description = "Company Truck"
    _rec_name = 'ngaygiao'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    ngaygiao = fields.Date('Ngày giao', default=fields.Datetime.now(), required=True, tracking=True, store=True)
    thang = fields.Char('Tháng', compute='_compute_ngay', store=True)
    nam = fields.Char('Năm', compute='_compute_ngay', store=True)
    nam_kt = fields.Char('Năm khai thác', compute='_compute_ngay', store=True)
    ngayban = fields.Date('Ngày bán', default=fields.Datetime.now(), tracking=True, store=True)
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    debug = fields.Html('Debug Info')  
    sum_soluong = fields.Float('Sảnlượng', compute='_compute_sum', digits='Product Price', store=True)
    sum_do = fields.Float('Độ', compute='_compute_sum', digits='One Decimal',store=True)
    sum_quykho = fields.Float('Quykhô', compute='_compute_sum', digits='Product Price', store=True)
    sum_slban = fields.Float('SL bán', compute='_compute_sum', digits='Product Price', store=True)
    sum_doban = fields.Float('Độ bán', compute='_compute_sum', digits='One Decimal',store=True)
    sum_qkban = fields.Float('Quykhô bán', compute='_compute_sum', digits='Product Price', store=True)
    haohut_sl = fields.Float('Haohụt SL', compute='_compute_sum', digits='Product Price', store=True)
    haohut_do = fields.Float('Haohụt Độ', compute='_compute_sum', digits='One Decimal', store=True)
    haohut_qk = fields.Float('Haohụt QK', compute='_compute_sum', digits='Product Price', store=True)
    money_loss = fields.Float(string="$ Haohụt", compute="_compute_money_loss", digits='Product Price', store=True)
    money_chomu = fields.Float( string="$ Chở mủ", compute="_compute_money_chomu", store=True, digits='Product Price')
    money_loi = fields.Float(string="$ Lời", compute="_compute_money_loi", store=True, digits='Product Price')

    # 1. Thêm field để lọc loại sản phẩm
    active_sanpham = fields.Selection([
        ('all', 'Tất cả'),
        ('nuoc', 'Mũ nước'),
        ('tap', 'Mũ tạp'),
        ('day', 'Mũ dây'),
        ('dong', 'Mũ đông'),
        ('chen', 'Mũ chén')
    ], string="Lọc sản phẩm", default='all')
    active_product_id = fields.Many2one(
        'product.product', 
        string='Sản phẩm hoạt động',
        domain=[('categ_id.name', '=', 'MŨ')]
    )
    # 2. Giữ lại field one2many gốc - không thay đổi
    deliver_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        string='Nhận mũ'
    )    
    sell_line_ids = fields.One2many(
        'rubber.sell', 
        'company_truck_id', 
        string='Bán mũ nước')

    # 3. Tạo field computed để hiển thị dữ liệu được lọc
    filtered_deliver_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        compute='_compute_filtered_deliver_line_ids',
        readonly=False,  # Thêm dòng này
        string='Danh sách lọc'   )

    filtered_tructiep_deliver_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',
        compute='_compute_filtered_tructiep_deliver_line_ids',
        readonly=False,  # Thêm dòng này
        string='Danh sách lọc'   )

    filtered_sell_line_ids = fields.One2many(
        'rubber.sell',
        'company_truck_id',
        compute='_compute_filtered_sell_line_ids',
        readonly=False,
        string='Filtered Sell Lines'
    )
    # 6 trường one2many mới cho trang order
    order_xetainha_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',  # Quan trọng: Thêm field relation
        compute='_compute_order_xetainha_line_ids',
        readonly=False,
        string='Mũ xe tải nhà'
    )
    
    order_tructiep_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',  # Quan trọng: Thêm field relation
        compute='_compute_order_tructiep_line_ids',
        readonly=False,
        string='Mũ trực tiếp'
    )

    order_chomu_line_ids = fields.One2many(
        'rubber.deliver',
        'company_truck_id',  # Quan trọng: Thêm field relation
        compute='_compute_order_chomu_line_ids',
        readonly=False,
        string='Mũ chờ'
    )
    # 4. Phương thức tính toán cho filtered_deliver_line_ids
    @api.depends('active_product_id', 'deliver_line_ids', 
                'deliver_line_ids.product_id', 
                'deliver_line_ids.daily_id', 'deliver_line_ids.to_id', 
                'deliver_line_ids.state', 'ngaygiao')
    def _compute_filtered_deliver_line_ids(self):
        for truck in self:
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.ngay == truck.ngaygiao and
                          (l.soluong != 0 or l.soluongtt != 0) and
                          l.state in ['giao', 'mua', 'nhan', 'order']
            )
            # Lọc theo đại lý "Xe tải nhà" và tổ "TỔ Xe tải"
            lines = lines.filtered(
                lambda l: (l.daily_id.name == 'Xe tải nhà') or 
                          (l.to_id.name == 'TỔ Xe tải')
            )
            # Lọc theo product_id nếu được thiết lập
            if truck.active_product_id:
                lines = lines.filtered(lambda l: l.product_id == truck.active_product_id)
                
            # Sắp xếp theo daily, sanpham
            lines = lines.sorted(key=lambda l: (l.daily_id.name if l.daily_id else "", l.product_id))
            
            truck.filtered_deliver_line_ids = lines
    
    # Phương thức tính toán cho filtered_tructiep_deliver_line_ids
    @api.depends('deliver_line_ids', 
                'deliver_line_ids.product_id', 
                'deliver_line_ids.daily_id', 'deliver_line_ids.to_id', 
                'deliver_line_ids.state', 'ngaygiao')
    def _compute_filtered_tructiep_deliver_line_ids(self):
        for truck in self:
            # Lọc theo ngày, số lượng và trạng thái
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.ngay == truck.ngaygiao and
                          (l.soluong != 0 or l.soluongtt != 0) and
                          l.state in ['giao','nhan', 'order']
            )
            
            # Lọc theo đại lý khác "Xe tải nhà" và tổ khác "TỔ Xe tải"
            lines = lines.filtered(
                lambda l: (l.daily_id.name != 'Xe tải nhà' and 
                           l.to_id.name != 'TỔ Xe tải')
            ) 
                
            # Lọc theo product_id nếu được thiết lập
            if truck.active_product_id:
                lines = lines.filtered(lambda l: l.product_id == truck.active_product_id)
                
            # Sắp xếp theo daily, sanpham
            lines = lines.sorted(key=lambda l: (l.daily_id.name if l.daily_id else "", l.product_id))
            
            truck.filtered_tructiep_deliver_line_ids = lines
    
    @api.depends('active_product_id', 'sell_line_ids', 
                'sell_line_ids.product_id', 
                'sell_line_ids.daily_id', 'ngaygiao')
    def _compute_filtered_sell_line_ids(self):
        for truck in self:
            lines = truck.sell_line_ids
            
            # Filter by product_id if set
            if truck.active_product_id:
                lines = lines.filtered(lambda l: l.product_id == truck.active_product_id)
                
            # Sort by daily_id
            lines = lines.sorted(key=lambda l: (l.daily_id.name if l.daily_id else ""))
            
            truck.filtered_sell_line_ids = lines
        
    # 7 Phương thức tính toán cho order_xetainha_line_ids
    @api.depends('deliver_line_ids', 'deliver_line_ids.daily_id', 'deliver_line_ids.state', 'deliver_line_ids.ngay', 'ngaygiao')
    def _compute_order_xetainha_line_ids(self):
        for truck in self:
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.state in ['nhan','order'] and 
                          l.ngay == truck.ngaygiao and
                          l.daily_id.name == 'Xe tải nhà'
            )
            truck.order_xetainha_line_ids = lines
    
    # Phương thức tính toán cho order_tructiep_line_ids
    @api.depends('deliver_line_ids', 'deliver_line_ids.daily_id', 'deliver_line_ids.to_id', 'deliver_line_ids.state', 'deliver_line_ids.ngay', 'ngaygiao')
    def _compute_order_tructiep_line_ids(self):
        for truck in self:
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.state in ['nhan','order'] and 
                          l.ngay == truck.ngaygiao and
                          l.daily_id.name != 'Xe tải nhà' and
                          l.to_name != 'TỔ Xe tải'
            )
            truck.order_tructiep_line_ids = lines
    
    # Phương thức tính toán cho order_chomu_line_ids
    @api.depends('deliver_line_ids', 'deliver_line_ids.daily_id', 'deliver_line_ids.to_id', 'deliver_line_ids.state', 'deliver_line_ids.ngay', 'ngaygiao')
    def _compute_order_chomu_line_ids(self):
        for truck in self:
            lines = truck.deliver_line_ids.filtered(
                lambda l: l.state in ['mua','order'] and 
                          l.ngay == truck.ngaygiao and
                          l.daily_id.name != 'Xe tải nhà' and
                          l.to_name == 'TỔ Xe tải'
            )
            truck.order_chomu_line_ids = lines
   
    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)

    @api.depends('ngaygiao')
    def _compute_ngay(self):
        for rec in self:
            #rec.thang = '01'
            #rec.nam = '2024'
            #rec.nam_kt = '2024'
            #if rec.recorded == True:
            rec.thang = datetime.strptime(str(rec.ngaygiao),'%Y-%m-%d').strftime('%m')
            rec.nam = datetime.strptime(str(rec.ngaygiao),'%Y-%m-%d').strftime('%Y')
            if rec.thang == '01':
                rec.nam_kt = str(int(rec.nam) - 1)
            else:
                rec.nam_kt = rec.nam    
        
    def mua_mu(self):
        self.ensure_one()
        # Get current user's department
        current_department = self.env.user.department_id
        if not current_department:
            raise UserError(_("Current user does not have a department assigned."))

        # Search for rubber.date with ngay = self.ngaygiao and to = current user's department
        rubber_date = self.env['rubber.date'].search([
            ('ngay', '=', self.ngaygiao),
            ('to', '=', current_department.id)
        ], limit=1)

        if not rubber_date:
            rubber_date = self.env['rubber.date'].create({
                'ngay': self.ngaygiao,
                'to': current_department.id,
            })

        return {
            'name': _('Mua mũ'),
            'type': 'ir.actions.act_window',
            'res_model': 'rubber.deliver',
            'view_mode': 'form',
            'view_id': self.env.ref('caosu.rubber_deliver_buy_view_form').id,
            'target': 'new',
            'context': dict(self._context, **{
                'default_company_truck_id': self.id,
                'default_rubberbydate_id': rubber_date.id,
                'default_to_id': current_department.id,
                'default_state': 'mua'
            })
        }
    
    @api.depends('active_product_id', 'filtered_sell_line_ids', 'filtered_deliver_line_ids', 'deliver_line_ids','sell_line_ids')
    def _compute_sum(self):
        for rec in self:
            if len(rec.filtered_deliver_line_ids) > 0:
                slnhan = 0
                slxdonhan = 0
                donhan = 0
                qknhan = 0
                for line in rec.filtered_deliver_line_ids:
                    slnhan += line.soluongtt if line.soluongtt != 0 else line.soluong
                    slxdonhan += line.dott * line.soluongtt if line.soluongtt != 0 and line.dott != 0 else line.do * line.soluong
                    qknhan += line.quykhott if line.quykhott != 0 else line.quykho
                if slnhan > 0:
                    donhan = slxdonhan / slnhan
                rec.sum_soluong = slnhan
                rec.sum_do = donhan
                rec.sum_quykho = qknhan
            else:
                rec.sum_soluong = 0
                rec.sum_do = 0
                rec.sum_quykho = 0

            if len(rec.filtered_sell_line_ids) > 0:                
                slban = 0                
                slxdoban = 0                
                doban = 0
                qkban = 0                
                for line in rec.filtered_sell_line_ids:
                    slban += line.soluong
                    slxdoban += line.do * line.soluong
                    qkban += line.quykho
                if slban > 0:
                    doban = slxdoban / slban
                rec.sum_slban = slban
                rec.sum_doban = doban
                rec.sum_qkban = qkban
            else:
                rec.sum_slban = 0
                rec.sum_doban = 0
                rec.sum_qkban = 0

            if len(rec.filtered_deliver_line_ids) > 0 and len(rec.filtered_sell_line_ids) > 0:            
                haohut_sl = slban - slnhan
                #tylehh_nuoc = haohut_nuoc / nhan * 100            
                haohut_do = doban - donhan
                #tylehhdo_nuoc = haohutdo_nuoc / donhan * 100            
                haohut_qk = qkban - qknhan
                #tylehhqk_nuoc = haohutqk_nuoc / qknhan * 100
                rec.haohut_sl = haohut_sl
                rec.haohut_do = haohut_do
                rec.haohut_qk = haohut_qk 
            else:
                rec.haohut_sl = 0
                rec.haohut_do = 0
                rec.haohut_qk = 0           
       
    @api.constrains('ngaygiao')
    def _check_rubberdate_unique(self):
        companytruck_counts = self.search_count([('ngaygiao','=',self.ngaygiao),('id','!=',self.id)])
        if companytruck_counts > 0:
            raise ValidationError("Nhận và bán ngày " + str(datetime.strptime(str(self.ngaygiao),'%Y-%m-%d').strftime('%d/%m/%Y')) + " đã tồn tại.")
        '''if len(self.env['rubber.date'].search([('ngay','=',self.ngaygiao)])) == False:
            raise ValidationError(_('Ngày ' + str(datetime.strptime(str(self.ngaygiao),'%Y-%m-%d').strftime('%d/%m/%Y')) + ' không có mũ giao.'))'''
    
    def action_create_sale_order_from_selected_lines(self):
        self.ensure_one()
        
        # Get SELECTED rubber.deliver lines
        selected_lines = (self.order_xetainha_line_ids + 
                        self.order_tructiep_line_ids + 
                        self.order_chomu_line_ids).filtered(lambda l: l.is_selected)
        
        if not selected_lines:
            raise UserError(_("No lines selected. Please select at least one line."))
        
        # Group lines by daily_id and to_id
        lines_by_daily_to = defaultdict(list)
        for line in selected_lines:
            if not line.daily_ban:
                raise UserError(_("Line for product %s has no partner (daily_id).") % line.product_id)
            
            key = (line.daily_ban, line.to_id)
            lines_by_daily_to[key].append(line)
        '''debug_line = f"line: {lines_by_daily_to}"
        self.debug = (self.debug or '') + debug_line'''
        # Create sale orders for each partner+team combination
        SaleOrder = self.env['sale.order']
        SaleOrderLine = self.env['sale.order.line']
        Partner = self.env['res.partner']
        Product = self.env['product.product']
                        
        created_orders = []
        for (daily_ban, to_id), lines in lines_by_daily_to.items():
            # Find max ngay for date_order
            max_ngay = max(line.ngay for line in lines if line.ngay)
            
            # Get analytic account from to_id
            analytic_account_id = to_id.analytic_account_id.id if to_id and to_id.analytic_account_id else False
            
            # Check for existing orders with same criteria
            domain = [
                ('partner_id', '=', daily_ban.id),
                ('commitment_date', '=', max_ngay),
                ('state', 'in', ['draft', 'sent']),  # Only consider draft/sent orders
            ]
            
            # Add to_id to domain if it exists
            if to_id:
                domain.append(('analytic_account_id', '=', analytic_account_id))
            
            existing_order = SaleOrder.search(domain, limit=1)
            
            if existing_order:
                # Use existing order
                sale_order = existing_order
            else:
                # Create sale order
                sale_order_vals = {
                    'partner_id': daily_ban.id,
                    'date_order': max_ngay,
                    'commitment_date': max_ngay,
                    'expected_date': max_ngay,
                    'analytic_account_id': analytic_account_id,
                    #'user_id': self.env.user.id,
                    # Add other sale order fields as needed
                }
                
                sale_order = SaleOrder.create(sale_order_vals)
            created_orders.append(sale_order)
            
            # Create sale order lines
            for line in lines:
                # Use product_id if available, otherwise look up based on sanpham
                if line.product_id:
                    product = line.product_id
                
                
                # Get price using existing method
                price, price_type_code = self._get_rubber_price(line)
                
                # Create order line based on price type
                if price_type_code == 'giamutap':
                    order_line = SaleOrderLine.create({
                        'order_id': sale_order.id,
                        'product_id': product.id,
                        'product_uom_qty': line.soluongtt,
                        'price_unit': price,
                        'commitment_date': line.ngay,
                    })
                else:
                    order_line = SaleOrderLine.create({
                        'order_id': sale_order.id,
                        'product_id': product.id,
                        'sanluong': line.soluongtt,
                        'do': line.dott,
                        'product_uom_qty': line.dott * line.soluongtt / 100,
                        'price_unit': price,
                        'commitment_date': line.ngay,
                    })
                '''debug_line = f"order_line: {product.id}, ' \
                            'sanluong': {line.soluongtt}, ' \
                                'do': {line.dott}, ' \
                            'product_uom_qty': {line.soluongtt}, ' \
                                'commitment_date': {line.ngay}"

                self.debug = (self.debug or '') + debug_line'''
                # Update the rubber.deliver line to mark it as processed
                line.write({
                    'sale_order_id': sale_order.id,
                    'sale_order_line_id': order_line.id,  # Store the sale order line ID
                    'state': 'order'  # Change state to 'order'
                })
        # After creating sale orders, deselect all processed lines
        selected_lines.write({'is_selected': False})
        # Show the created sale orders
        if not created_orders:
            return {'type': 'ir.actions.act_window_close'}
            
        action = {
            'name': _('Created Sale Orders'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', [order.id for order in created_orders])],
        }
        
        if len(created_orders) == 1:
            action['view_mode'] = 'form'
            action['res_id'] = created_orders[0].id
            
        return action    
           
    def _get_rubber_price(self, order_line):      
        # Find to_id record where name matches harvest_line.to (char)
        
        domain = [
            ('daily_id', '=', order_line.daily_id.id),             
            ('ngay_hieuluc', '<', order_line.ngay),
            ('to_id', '=', order_line.to_id.id)                      
        ]       
        
        # Try to determine price type from product_id first
        if order_line.product_id and order_line.product_id.default_code:
            code = order_line.product_id.default_code
            if code == 'MUNUOC':
                domain.append(('price_type_id.code', '=', 'giamunuoc'))
            elif code == 'MUTAP':
                domain.append('|')
                domain.append(('price_type_id.code', '=', 'giamutap'))
                domain.append(('price_type_id.code', '=', 'giamutap_do'))
            elif code == 'MUDONG':
                domain.append(('price_type_id.code', '=', 'giamudong'))
            elif code == 'MUDAY':
                domain.append(('price_type_id.code', '=', 'giamuday'))
            elif code == 'MUCHEN':
                domain.append(('price_type_id.code', '=', 'giamuchen'))
        
        else:
            domain.append(('price_type_id.code', '=', ''))
        
        price = self.env['rubber.price'].search(domain, limit=1)
        
        '''debug_line = f"Domain: {domain}, Price: {price.gia if price else 'N/A'}\n"
        self.debug = (self.debug or '') + debug_line'''
        
        if price:
            if price.price_type_id.code == 'giamutap_do' or price.price_type_id.code == 'giamunuoc':
                return price.gia * 100, price.price_type_id.code
            else:
                return price.gia, price.price_type_id.code
        return 0.0, None
        
    @api.depends('filtered_sell_line_ids', 'active_product_id', 'ngaygiao')
    def _compute_money_loss(self):
        # Product code to price type mapping
        price_type_map = {
            'munuoc': 'giamunuoc', 
            'mutap': 'giamutap', 
            'muday': 'giamuday',
            'mudong': 'giamudong', 
            'muchen': 'giamuchen'
        }
        
        for rec in self:           
            rec.money_loss = 0
            total_haohut = rec.haohut_qk

            # Use the right field - if filtered_sell_line_ids doesn't exist, use sell_line_ids
            lines = getattr(rec, 'filtered_sell_line_ids', rec.sell_line_ids)
            if not lines or not rec.active_product_id:
                continue        
               
            try:               
                # Find highest line safely
                highest_line = lines[0] if lines else False
                if len(lines) > 1:
                    highest_line = sorted(lines, key=lambda x: getattr(x, 'quykho', 0) or 0, reverse=True)[0]
                
                # Default price
                price = 0.0
            
                if highest_line and highest_line.daily_id:
                    # Get price type from product code
                    product_code = rec.active_product_id.default_code or ''
                    price_type_code = price_type_map.get(product_code, 'giamunuoc')
                    
                    # Safely look up models
                    PriceType = self.env['rubber.price.type']
                    price_type = PriceType.search([('code', '=', price_type_code)], limit=1)
                    
                    if price_type:
                        # Base domain for price search
                        domain = [
                            ('ngay_hieuluc', '<=', rec.ngaygiao),
                            ('price_type_id', '=', price_type.id),
                            ('daily_id', '=', highest_line.daily_id.id),
                        ]                    
                        # Try with team first, then without
                        to_id = self.env['hr.department'].search([('name', '=', 'TỔ Xe tải')], limit=1)
                        price_record = False
                        if to_id:
                            price_record = self.env['rubber.price'].search(
                                domain + [('to_id', '=', to_id.id)], 
                                order='ngay_hieuluc desc', limit=1
                            )
                        
                        if not price_record:
                            price_record = self.env['rubber.price'].search(
                                domain, order='ngay_hieuluc desc', limit=1
                            )
                        
                        if price_record:
                            price = price_record.gia
            
                rec.money_loss = total_haohut * price *100
            except Exception as e:
                _logger.error(f"Error computing money_loss: {e}")
                rec.money_loss = 0.0
    
    @api.depends('active_product_id', 'sum_qkban')
    def _compute_money_chomu(self):
        for truck in self:
            # Use the existing sum_qkban field directly
            truck.money_chomu = truck.sum_qkban * 15 * 100
    @api.depends('money_chomu', 'money_loss')
    def _compute_money_loi(self):
        for truck in self:
            truck.money_loi = truck.money_chomu + truck.money_loss

    # Các methods để thiết lập active_sanpham qua buttons
    
    def set_sanpham_all(self):        
        # Setting to False to show all products (no filtering)
        self.active_product_id = False        
        return True

    def set_sanpham_nuoc(self):        
        product = self.env['product.product'].search([('default_code', '=', 'munuoc')], limit=1)
        self.active_product_id = product.id if product else False
        return True

    def set_sanpham_tap(self):        
        product = self.env['product.product'].search([('default_code', '=', 'mutap')], limit=1)
        self.active_product_id = product.id if product else False
        return True

    def set_sanpham_day(self):        
        product = self.env['product.product'].search([('default_code', '=', 'muday')], limit=1)
        self.active_product_id = product.id if product else False
        return True

    def set_sanpham_dong(self):        
        product = self.env['product.product'].search([('default_code', '=', 'mudong')], limit=1)
        self.active_product_id = product.id if product else False
        return True

    def set_sanpham_chen(self):        
        product = self.env['product.product'].search([('default_code', '=', 'muchen')], limit=1)
        self.active_product_id = product.id if product else False
        return True
    
    def action_select_all_order_lines(self):
        """Select all order lines"""
        lines = self.order_xetainha_line_ids + self.order_tructiep_line_ids + self.order_chomu_line_ids
        lines.write({'is_selected': True})
        return True

    def action_deselect_all_order_lines(self):
        """Deselect all order lines"""
        lines = self.order_xetainha_line_ids + self.order_tructiep_line_ids + self.order_chomu_line_ids
        lines.write({'is_selected': False})
        return True