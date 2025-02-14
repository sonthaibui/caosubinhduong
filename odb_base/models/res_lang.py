# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_TIME_FORMAT

MODE_DATETIME = "MODE_DATETIME"
MODE_DATE = "MODE_DATE"
MODE_TIME = "MODE_TIME"

class Lang(models.Model):
    _inherit = "res.lang"

    @api.model
    def best_match(self, lang=None, failure_safe=True):
        first_installed = self.search([("active", "=", True)], limit=1)
        if not lang:
            lang = (
                (self.ids and self[0].code)
                or self.env.context.get("lang")
                or self.env.user.lang
                or first_installed.code
            )
        record = self.search([("code", "=", lang)])
        try:
            record.ensure_one()
        except ValueError:
            if not failure_safe:
                raise UserError(_("Best matched language (%s) not found.") % lang)
            else:
                record = first_installed
        return record

    @api.model
    def datetime_formatter(self, value, lang=None, template=MODE_DATETIME, separator=" ", failure_safe=True):
        lang = self.best_match(lang)
        # Get the template
        if template in {MODE_DATETIME, MODE_DATE, MODE_TIME}:
            defaults = []
            if "DATE" in template:
                defaults.append(lang.date_format or DEFAULT_SERVER_DATE_FORMAT)
            if "TIME" in template:
                defaults.append(lang.time_format or DEFAULT_SERVER_TIME_FORMAT)
            template = separator.join(defaults)
        # Convert str to datetime objects
        if isinstance(value, str):
            try:
                value = fields.Datetime.to_datetime(value)
            except ValueError:
                # Probably failed due to value being only time
                value = datetime.strptime(value, DEFAULT_SERVER_TIME_FORMAT)
        # Time-only fields are floats for Odoo
        elif isinstance(value, float):
            # Patch values >= 24 hours
            if value >= 24:
                template = template.replace("%H", "%d" % value)
            # Convert to time
            value = (datetime.min + timedelta(hours=value)).time()
        return value.strftime(template)
