from odoo import fields, models 


class WizardDisableFarmZone(models.TransientModel):
    _name = 'wizard.disable.farm.zone'
    _description = 'Disable Land Wizard'

    def _default_land(self):
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        return self.env[active_model].browse(active_id)

    farm_zone_id = fields.Many2one('farm.zone', string='Small land', default=_default_land, required=True)
    disable_reason = fields.Text(string='Disable Reason', groups='odb_farm_management.group_farm_manager', required=True)

    def action_confirm(self):
        self.farm_zone_id.disable_reason = self.disable_reason
        self.farm_zone_id.active = True
        self.farm_zone_id.is_public = False
        self.farm_zone_id.stage = self.env['farm.stage'].search([])[-1]
