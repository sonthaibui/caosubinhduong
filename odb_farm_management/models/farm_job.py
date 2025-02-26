from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from datetime import timedelta

class FarmJob(models.Model):
    _name = 'farm.job'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char('Job Name', required=True)
    start_date = fields.Date('Start Date', default=fields.Date.today())
    end_date = fields.Date('End Date')
    quantity = fields.Integer('Quantity', compute='_compute_quantity')
    device_ids = fields.Many2many('maintenance.equipment', 'land_job_maintenance_equipment_rel', string='Device')
    state = fields.Selection([
        ('pending', 'Pending'),     
        ('work', 'Work'),
        ('done', 'Done')],
        'State', default="pending", group_expand='_group_expand_states')
    remaining_days = fields.Char('Remaining Days', compute="_compute_remaining_days", readonly=True)
    product_id = fields.Many2one('product.product', string="Product")
    farm_job_operation_ids = fields.Many2many('farm.job.operation', 'land_job_farm_job_operation_rel', string='Job Operation')
    
    
    @api.constrains('end_date')
    def _check_end_date(self):
        for record in self:
            if record.end_date and record.end_date < record.start_date:
                raise ValidationError(_("The end date must be greater than the start date."))

    @api.depends('remaining_days')
    def _compute_remaining_days(self):
        for record in self:
            if record.end_date and record.start_date:
                day_left = record.end_date - record.start_date
                if day_left.days == 0:
                    record.remaining_days = 'Time Out'
                    record.state = 'done'
                else:
                    record.remaining_days = day_left.days
            else:
                record.remaining_days = ''

    @api.depends('farm_job_operation_ids')
    def _compute_quantity(self):
        for record in self:
            qty = 0.0
            for rc in record.farm_job_operation_ids:
                qty += rc.quantity
            record.quantity += qty
    
    def _group_expand_states(self, states, domain, order):
        return [key for key, val in type(self).state.selection]