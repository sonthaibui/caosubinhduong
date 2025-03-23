from . import models
from . import controllers
from . import wizard

def post_init_hook(cr, registry):
    from odoo import api, SUPERUSER_ID
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['rubber.department.config'].ensure_default_config()
    env['rubbertest.department.config'].ensure_default_config()