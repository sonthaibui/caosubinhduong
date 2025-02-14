from odoo import models, fields, api, SUPERUSER_ID, _
from odoo.exceptions import ValidationError
from odoo.tools.translate import _

from datetime import timedelta

class FarmFarm(models.Model):
    _name = 'farm.land'
    _description = 'Farm Management'
    _order = "date_release desc, name"
    _rec_name = 'name'

    name = fields.Char(string='Farm Name', required=True)
    address =  fields.Char(string='Address')
    acreage = fields.Integer(string='Acreage')
    date_release = fields.Date('Date Release')
    phone = fields.Char('Phone')

    @api.constrains('acreage')
    def _check_acreage(self):
        for record in self:
            if record.acreage < 0:
                raise ValidationError(_("Acreage is not allowed to be less than 0"))
    
    @api.constrains('phone')
    def _check_phone(self):
        for record in self:
            phone = record.phone
            if phone and phone.isnumeric() == False:
                raise ValidationError(_("%s is not valid. Please enter valid number", phone))
            if phone and (len(phone) < 9 or len(phone) > 12):
                raise ValidationError(_("Phone number cannot be less than 8 digits or more than 12 digits"))

    @api.constrains('date_release')
    def _check_release_date(self):
        for record in self:
            if record.date_release and record.date_release > fields.Date.today():
                raise models.ValidationError('Release date must be in the past')
    

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'The name must be unique !')
    ]
            

    def action_view_land(self):
        action = self.env["ir.actions.actions"]._for_xml_id("odb_farm_management.action_farm_zone_form_act_window")
        action['domain'] = [('land_mana_id','=',self.id)]
        return action
