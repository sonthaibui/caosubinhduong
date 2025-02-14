# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class WizardSplitSale(models.TransientModel):
    _name = 'wizard.split.sale.order'
    _description = "Wizard Split Sale Order"

    wz_order_line_ids = fields.One2many(string='Wizard Sale Order', 
        comodel_name='wizard.split.sale.order.line', inverse_name='wz_sale_id')
    sale_id = fields.Many2one('sale.order', string='Sale Order')
    commitment_date = fields.Date(string='Commitment Date', required=True)

    @api.onchange("wz_order_line_ids")
    def onchange_validate_order(self):
        for wz_line in self.wz_order_line_ids:
            line = wz_line.so_line_id
            if wz_line.product_uom_qty > line.product_uom_qty:
                raise UserError(_('Quantity of %s is %s.\nEntered quantity must equal or less than %s')%(line.product_id.display_name, line.product_uom_qty, line.product_uom_qty))
            elif wz_line.product_uom_qty < 0.0:
                raise UserError(_('Invalid entered quantity: %s for %s.')%(wz_line.product_uom_qty, wz_line.product_id.display_name))

    def split_order(self):
        if len(self) != 1:
            raise ValidationError(_('SourceCodeError: Contact Odoo Coder!\nExpect One Sale Order.'))

        # check invalid value.
        if not self.sale_id.order_line:
            raise UserError(_('Please create some Sale lines.'))
        elif all(not wz_line.selected_field for wz_line in self.wz_order_line_ids):
            raise UserError(_('Select atleast one PR line to split.'))
        else: # valid value.
            new_order = self.sale_id.copy(default={'commitment_date': self.commitment_date})
            new_order.sudo().write({
                'order_line': [(6, 0 ,False)],
                'commitment_date': self.commitment_date,})
            for wz_line, line in zip(self.wz_order_line_ids, self.sale_id.order_line):
                if not wz_line.selected_field:
                    continue
                else:
                    if wz_line.product_uom_qty == line.product_uom_qty:
                        line.sudo().write({'order_id': new_order.id})
                    else: # wz_line.product_uom_qty < line.product_uom_qty:
                        # create new order line
                        values = line.copy_data({ 
                            'order_id': new_order.id, 
                            'product_uom_qty': wz_line.product_uom_qty,
                            'name': wz_line.description,
                            'commitment_date': wz_line.commitment_date})[0]
                        line.sudo().write({'product_uom_qty': line.product_uom_qty - wz_line.product_uom_qty})
                        self.env['sale.order.line'].create(values)
              

            new_order.sudo().write({
                'commitment_date': self.sale_id.commitment_date,
                'origin': self.sale_id.origin,
                'state': 'draft',
                'note': _("Splited from %s") % (self.sale_id.name),
                # 'custom_picking_type_id': self.sale_id.custom_picking_type_id.id,
                'parent_id': self.sale_id.id,
            })
            if new_order:
                body_01 = "This Purchase Requisition is splited from Purchase Requisition {}".format(self.sale_id.name)
                new_order.message_post(body=body_01)

                body_02 = "A new Purchase Requisition {} is created from this Purchase Requisition".format(new_order.name)
                self.sale_id.message_post(body=body_02)
            return True
