from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from datetime import timedelta

class SmallLand(models.Model):
    _name = 'farm.zone'
    _description = 'Farm Zone'
    _rec_name = 'name'

    @api.returns('self')
    def _default_stage(self):
        return self.env['farm.stage'].search([], limit=1)

    active = fields.Boolean(string = "Active", default=False)
    code = fields.Char('Code')
    name = fields.Char('Zone Name', required=True)
    acreage_land = fields.Integer('Acreage Zone')
    currency_id = fields.Many2one('res.currency', string="Currency")
    land_mana_id = fields.Many2one('farm.land', string='Farm Land')
    stage = fields.Many2one('farm.stage', string='Stage', group_expand='_read_group_stage_ids', default=_default_stage)
    farm_job_ids = fields.Many2many('farm.job', 'farm_job_farm_zone_rel', string='Jobs Of Land')
    farmer_team_ids = fields.One2many('farmer.team', 'farm_zone_id', string='Farm Team')
    farm_job_line_ids = fields.Many2many('farm.job.line', 'farm_job_line_farm_zone_rel', string='Job Lines')

    image_1920 = fields.Binary(string='Image')
    is_public = fields.Boolean(string='Is Public', groups='odb_farm_management.group_farm_manager',default=False)
    private_notes = fields.Text(string='Private Notes', groups='odb_farm_management.group_farm_manager')
    disable_reason = fields.Text(string='Disable Reason', groups='odb_farm_management.group_farm_manager')

    @api.constrains('acreage_land')
    def _check_acreage_land(self):
        for record in self:
            land_mana_ids = self.env['farm.zone'].search([('land_mana_id', '=', self.land_mana_id.id), ('id', '!=', record.id)])
            total_arc = [ x.acreage_land for x in land_mana_ids]
            if record.acreage_land < 0:
                raise ValidationError(_("Acreage small land is not allowed to be less than 0"))
            if record.acreage_land + sum(total_arc) > record.land_mana_id.acreage:
                raise ValidationError(_("Acreage small land must be less than Area land"))

    @api.constrains('stage')
    def _check_stage(self):
        for record in self:
            if self.env['farm.stage'].search_count([]) > 0:
                if self.env['farm.stage'].search([])[-1].id == self.env['farm.stage'].search([('name', '=', record.stage.name)]).id:
                    record.active = True
                    record.is_public = False
                else:
                    record.active = False

    @api.model 
    def create(self, vals):
            vals['code'] =  self.env['ir.sequence'].next_by_code('farm.zone')
            return super(SmallLand, self).create(vals)

    def action_disable_land(self):
        return self.env.ref('odb_farm_management.wizard_disable_farm_zone_action').read()[0]

    def action_update_code(self):
        for record in self:
            new_code =  self.env['ir.sequence'].next_by_code('farm.zone')
            if record.code == False or record.code:
                record.write({'code': new_code})

    def action_view_job(self):
        action = self.env["ir.actions.actions"]._for_xml_id("odb_farm_management.action_farm_job_act_window")
        action['domain'] = [('id', 'in', self.farm_job_ids.ids)]
        return action        

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        """ Read group customization in order to display all the stages in the
            kanban view, even if they are empty
        """
        stage_ids = stages._search([], order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)
