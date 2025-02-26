from . import models

import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        action = env.ref("erpvn_document_management.action_page")
        action.write({
            'view_mode': "tree,form,kanban"
        })
    except ValueError as e:
            _logger.warning(e)
