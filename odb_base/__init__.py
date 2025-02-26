# -*- coding: utf-8 -*-
import odoo 
from odoo import api, SUPERUSER_ID
from . import controllers
from . import wizard
from . import models 

#----------------------------------------------------------
# Hooks
#----------------------------------------------------------

XML_ID = "erpvn_web_branding._assets_primary_variables"
SCSS_URL = "/erpvn_web_branding/static/src/scss/colors.scss"

odoo.release.version_info = odoo.release.version_info[:5] + ('e',)
if '+e' not in odoo.release.version:     # not already patched by packaging
    odoo.release.version = '{0}+e{1}{2}'.format(*odoo.release.version.partition('-'))

odoo.service.common.RPC_VERSION_1.update(
    server_version=odoo.release.version,
    server_version_info=odoo.release.version_info)