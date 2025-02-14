from odoo import models, api, fields, _
from odoo.exceptions import UserError
from odoo.tools.misc import clean_context, OrderedSet


class StockMove(models.Model):
    _inherit = 'stock.move'


    # overite function odoo 
    def _action_cancel(self):
        ''' Mục đích bỏ qua trường hợp state của picking là 'done' thì không được cancel:
            info : You cannot cancel a stock move that has been set to 'Done'  '''
        # if any(move.state == 'done' and not move.scrapped for move in self):
        #     raise UserError(_('You cannot cancel a stock move that has been set to \'Done\'. Create a return in order to reverse the moves which took place.'))
        moves_to_cancel = self.filtered(lambda m: m.state != 'cancel' and not (m.state == 'done' and m.scrapped))
        # self cannot contain moves that are either cancelled or done, therefore we can safely
        # unlink all associated move_line_ids
        moves_to_cancel._do_unreserve()

        for move in moves_to_cancel:
            siblings_states = (move.move_dest_ids.mapped('move_orig_ids') - move).mapped('state')
            if move.propagate_cancel:
                # only cancel the next move if all my siblings are also cancelled
                if all(state == 'cancel' for state in siblings_states):
                    move.move_dest_ids.filtered(lambda m: m.state != 'done')._action_cancel()
            else:
                if all(state in ('done', 'cancel') for state in siblings_states):
                    move.move_dest_ids.write({'procure_method': 'make_to_stock'})
                    move.move_dest_ids.write({'move_orig_ids': [(3, move.id, 0)]})
        moves_to_cancel.write({
            'state': 'cancel',
            'move_orig_ids': [(5, 0, 0)],
            'procure_method': 'make_to_stock',
        })
        return True

    # overite function odoo 
    def _do_unreserve(self):
        '''
           Mục đích bỏ qua trường hợp state của picking là 'done' thì không được unreserve: 
           info: You cannot unreserve a stock move that has been set to 'Done' 
        '''
        moves_to_unreserve = OrderedSet()
        for move in self:
            if move.state == 'cancel' or (move.state == 'done' and move.scrapped):
                # We may have cancelled move in an open picking in a "propagate_cancel" scenario.
                # We may have done move in an open picking in a scrap scenario.
                continue
            # elif move.state == 'done':
            #     raise UserError(_("You cannot unreserve a stock move that has been set to 'Done'."))
            moves_to_unreserve.add(move.id)
        moves_to_unreserve = self.env['stock.move'].browse(moves_to_unreserve)

        ml_to_update, ml_to_unlink = OrderedSet(), OrderedSet()
        moves_not_to_recompute = OrderedSet()
        for ml in moves_to_unreserve.move_line_ids:
            if ml.qty_done:
                ml_to_update.add(ml.id)
            else:
                ml_to_unlink.add(ml.id)
                moves_not_to_recompute.add(ml.move_id.id)
        ml_to_update, ml_to_unlink = self.env['stock.move.line'].browse(ml_to_update), self.env['stock.move.line'].browse(ml_to_unlink)
        moves_not_to_recompute = self.env['stock.move'].browse(moves_not_to_recompute)

        ml_to_update.write({'product_uom_qty': 0})
        ml_to_unlink.unlink()
        # `write` on `stock.move.line` doesn't call `_recompute_state` (unlike to `unlink`),
        # so it must be called for each move where no move line has been deleted.
        (moves_to_unreserve - moves_not_to_recompute)._recompute_state()
        return True