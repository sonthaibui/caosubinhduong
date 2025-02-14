from odoo import models, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        self.ensure_one()
        if not self._context.get('manual_validate_date_time') and self.env.user.has_group('odb_stock_management.group_stock_warehouse_department'):
            view = self.env.ref('odb_stock_picking_backdate.view_stock_picking_backdate_form')
            ctx = dict(self._context or {})
            ctx.update({'default_picking_id': self.id})
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'stock.picking.backdate',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'context': ctx,
            }
        return super(StockPicking, self).button_validate()

    def action_done(self):
        res = super(StockPicking, self).action_done()
        manual_validate_date_time = self._context.get('manual_validate_date_time', False)
        if manual_validate_date_time:
            self.filtered(lambda x: x.state == 'done').write({'date_done': manual_validate_date_time})
        return res
