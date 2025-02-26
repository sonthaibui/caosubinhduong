# -*- coding: utf-8 -*-
from odoo import fields, models,api, _

class Wizardchangelocation(models.TransientModel):
    _name = "wizard.change.location"
    _description = "Wizard Change Location"

    picking_id = fields.Many2one(
        'stock.picking', 'Picking',
        default=lambda self: self.env['stock.picking'].browse(self._context.get('picking_id')),
        readonly=True,)

    location_id = fields.Many2one('stock.location', "Source Location",
                    default=lambda self: self.env['stock.picking'].browse(self._context.get('picking_id')).location_id)
    
    location_dest_id = fields.Many2one('stock.location', "Destination Location",
                    default=lambda self: self.env['stock.picking'].browse(self._context.get('picking_id')).location_dest_id)
    
    def action_change_location(self):
        value={}
        value_move = {}
        if self.location_dest_id:
            value['location_dest_id'] = self.location_dest_id.id
            value_move['location_dest_id'] = self.location_dest_id.id
        if self.location_id:
            value['location_id'] = self.location_id.id
            value_move['location_id'] = self.location_id.id
        self.picking_id.write(value)
        self.picking_id.move_ids_without_package.write(value_move)
        return True

