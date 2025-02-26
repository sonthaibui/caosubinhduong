from odoo import models,api,_


class StockPicking(models.Model):
    _inherit = "stock.picking"


    def action_show_wizard_change_location(self):
        view = self.env.ref('odb_stock_management.wizard_change_location')
        context={'picking_id':self.id,}
        return {
            'name': 'Wizards Change Location',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.change.location',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }
