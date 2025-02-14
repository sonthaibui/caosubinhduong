from odoo import models, fields, api


class ComponentAttribute(models.TransientModel):
    _name = 'component.attribute'
    _description = 'Component Attribute'
    
    product_tmpl_id = fields.Many2one(string='Product Template', comodel_name='product.template', ondelete='cascade', readonly=True, )
    product_id = fields.Many2one(string='Product Variant', comodel_name='product.product', ondelete='cascade', readonly=True)
    sale_order_line = fields.Many2one(string='Sale Order Line', comodel_name='sale.order.line', ondelete='cascade', readonly=True, store=True )
    component_line_ids = fields.One2many(string='Component Line',comodel_name='component.attribute.line', inverse_name='component_attribute_id',)
    #custom_config = fields.Selection(string='Config', selection=[('new', 'New'), ('available', 'Available')])
