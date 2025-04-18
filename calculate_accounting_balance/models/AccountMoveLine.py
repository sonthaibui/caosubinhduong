import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero
import math

class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    ngay = fields.Integer('Ngay', compute='_compute_ntq', store=True, copy=True)
    thang = fields.Char('Thang', compute='_compute_ntq', store=True, copy=True)
    quy = fields.Char('Quy', compute='_compute_ntq', store=True, copy=True)
    stock_move_id = fields.Many2one('stock.move', related='move_id.stock_move_id', string='Stock Move')
    giamdoc_duyet = fields.Boolean('GĐ Duyệt', store=True, copy=True)
    ketoan_duyet = fields.Boolean('KT Duyệt', store=True, copy=True)
    nguoitao = fields.Char(compute='_compute_nguoitao', string='Người Tạo:')
    namkt = fields.Char(string="NAMKT", compute="_compute_namkt", store=True)
    is_customer = fields.Boolean(string="Is Customer", compute="_compute_partner_types", store=True)
    is_vendor = fields.Boolean(string="Is Vendor", compute="_compute_partner_types", store=True)
    company_type = fields.Selection(        
        string="Company Type",
        related="partner_id.company_type",
        store=True,
        readonly=True
    )
    account_group = fields.Selection(
        string="Account Group", 
        related="account_id.internal_group", 
        store=True, 
        readonly=True
    )
    account_type = fields.Many2one(
        comodel_name='account.account.type',
        string="Account Type", 
        related="account_id.user_type_id", 
        store=True, 
        readonly=True
    )
    ghichu = fields.Html(
        string="Ghi Chú",
        help="Notes or comments in rich text format",
        sanitize=True,
        strip_style=False,
        store=True,
        copy=True
    )
    
    @api.model
    def _compute_nguoitao(self):
        self.nguoitao = str(self.env.user.id)
        
    @api.depends('date')
    def _compute_ntq(self):
        for rec in self:
            if rec.date:
                rec.ngay = rec.date.timetuple().tm_yday
                thang = rec.date.month
                if thang < 10:
                    rec.thang = "Tháng 0" + str(thang)
                else:
                    rec.thang = "Tháng " + str(thang)
                rec.quy = "Quý " + str(math.ceil(rec.date.month / 3))

    @api.depends('date', 'analytic_account_id')
    def _compute_namkt(self):
        for rec in self:
            # Default values if date is not set
            if not rec.date:
                rec.namkt = ""
                continue
                
            # Extract month and year from date
            month = rec.date.month
            year = rec.date.year
            
            # Apply the logic based on analytic account name
            if rec.analytic_account_id and rec.analytic_account_id.name == "Tổ MÌ NOVA":
                # For "Tổ MÌ NOVA" - months 1-9 use previous year, 10-12 use current year
                if month in range(1, 10):  # 1 to 9
                    rec.namkt = str(year - 1)
                else:
                    rec.namkt = str(year)
            else:
                # For other analytic accounts - only month 1 uses previous year
                if month == 1:
                    rec.namkt = str(year - 1)
                else:
                    rec.namkt = str(year)

    @api.depends('partner_id')
    def _compute_partner_types(self):
        for rec in self:
            if rec.partner_id:
                # Safely access the fields with getattr to avoid errors
                rec.is_customer = getattr(rec.partner_id, 'is_customer', False)
                rec.is_vendor = getattr(rec.partner_id, 'is_vendor', False)
            else:
                rec.is_customer = False
                rec.is_vendor = False