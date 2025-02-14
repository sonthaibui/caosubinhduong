import pytz
import logging
from odoo import models, fields, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import remove_accents, formataddr


_logger = logging.getLogger(__name__)


class OdooBase(models.AbstractModel):
    _name = 'odb.base'
    _description = 'Base Model'
    
    def convert_time_to_utc(self, dt, tz_name=None, is_dst=None):
        """
        :param dt: an instance of datetime object to convert to UTC
        :param tz_name: the name of the timezone to convert. In case of no tz_name passed, this method will try to find the timezone in context or the login user record
        :param is_dst: respecting daylight saving time or not

        :return: an instance of datetime object in UTC (with timezone notation)
        :rtype: datetime
        """
        tz_name = tz_name or self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise ValidationError(
                _("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
        local = pytz.timezone(tz_name)
        local_dt = local.localize(dt, is_dst=is_dst)
        return local_dt.astimezone(pytz.utc)

    def convert_utc_time_to_tz(self, utc_dt, tz_name=None, is_dst=None):
        """
        Method to convert UTC time to local time
        :param utc_dt: datetime in UTC
        :param tz_name: the name of the timezone to convert. In case of no tz_name passed, this method will try to find the timezone in context or the login user record
        :param is_dst: respecting daylight saving time or not

        :return: datetime object presents local time
        """
        tz_name = tz_name or self._context.get('tz') or self.env.user.tz
        if not tz_name:
            raise ValidationError(
                _("Local time zone is not defined. You may need to set a time zone in your user's Preferences."))
        tz = pytz.timezone(tz_name)
        return pytz.utc.localize(utc_dt, is_dst=is_dst).astimezone(tz)