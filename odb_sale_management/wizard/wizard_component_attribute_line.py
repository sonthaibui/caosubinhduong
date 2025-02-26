
from odoo import models, fields, api


class ComponentAttributeLine(models.TransientModel):
    _name = 'component.attribute.line'
    _description = 'Component Attribute Line'
    
    attribute_ids = fields.Many2many('product.attribute', string="Attributes", ondelete='cascade')
    value_ids = fields.Many2many('product.attribute.value', string="Values", ondelete='cascade')

    product_tmpl_id = fields.Many2one(related='component_attribute_id.product_tmpl_id', store=True)
    component_attribute_id = fields.Many2one(string='component_attribute', comodel_name='component.attribute', ondelete='cascade')


