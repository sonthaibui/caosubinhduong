    # -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError

from datetime import timedelta, date as datetime_date
from dateutil.relativedelta import relativedelta

import logging
_logger = logging.getLogger(__name__)


class IrSequence(models.Model):
    _inherit = 'ir.sequence'

    #thoi gian lap cua ma
    rollback = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly')], string='Rollback', default='yearly', copy=True)
    
    #loai ma 
    encoding = fields.Selection([
        ('sequence', 'Sequence'),
        ('ean13', 'EAN-13'),
        ('ean8', 'EAN-8'),
        ('upca', 'UPC-A')], string='Type of Encoding', default='sequence', copy=True)
    
    def _next_do(self):
        next_char = super(IrSequence, self)._next_do()
        if self.encoding != 'sequence':
            next_char = self.get_next_barcode(next_char, self.padding)
        return next_char
    
    def get_next_barcode(self, next_char, padding):
        code = str(next_char).rjust(padding, '0')
        if code:
            barcode = code + str(self.ean_checksum(code) if self.encoding in ('ean13','upca') else self.ean8_checksum(code))
            if not barcode:
                raise UserError(_('Error! When creating barcode!'))
        return next_char
    
    @api.model
    def ean_checksum(self, ean):
        code = list(ean)
        if len(code) != 13:
            raise UserError(_('Custom Barcode not enough 13 character!'))
        oddsum = evensum = 0
        for i in range(len(code)):
            if i % 2 == 0:
                evensum += int(code[i])
            else:
                oddsum += int(code[i])
        total = oddsum * 3 + evensum
        return int((10 - total % 10) % 10) 
    
    @api.model
    def ean8_checksum(self, ean):
        code = list(ean)
        if len(code) != 8:
            raise UserError(_('Custom Barcode not enough 8 character!'))
        sum1 = int(ean[1]) + int(ean[3]) + int(ean[5])
        sum2 = int(ean[0]) + int(ean[2]) + int(ean[4]) + int(ean[6])
        total = sum1 + 3 * sum2
        return int((10 - total % 10) % 10)
    
    # Kim: seq_date_range by rollback
    def _create_date_range_seq(self, date):
        if not self.rollback:
            return super()._create_date_range_seq(date)
        
        date_from, date_to = self._get_date_range(date)
        date_range = self.env['ir.sequence.date_range'].search([('sequence_id', '=', self.id), ('date_from', '>=', date), ('date_from', '<=', date_to)], order='date_from desc', limit=1)
        if date_range:
            date_to = date_range.date_from + timedelta(days=-1)
        date_range = self.env['ir.sequence.date_range'].search([('sequence_id', '=', self.id), ('date_to', '>=', date_from), ('date_to', '<=', date)], order='date_to desc', limit=1)
        if date_range:
            date_from = date_range.date_to + timedelta(days=1)

        seq_date_range = self.env['ir.sequence.date_range'].sudo().create({
            'date_from': date_from,
            'date_to': date_to,
            'sequence_id': self.id,
        })
        return seq_date_range
    
    def _get_date_range(self, date):
        self.ensure_one()
        
        if self.rollback == 'weekly':
            date_from = date - timedelta(days=date.weekday())
            date_to = date_from + timedelta(days=6)
        elif self.rollback == 'monthly':
            date_from = datetime_date(date.year, date.month, 1)
            date_to = date_from + relativedelta(months=1)
            date_to += relativedelta(days=-1)
        elif self.rollback == 'yearly':
            date_from = datetime_date(date.year, 1, 1)
            date_to = datetime_date(date_from.year, 12, 31)
        else:
            date_from = date_to = date
            
        return date_from, date_to


    def create_ir_loging(self,message,path,func):
        self.env["ir.logging"].sudo().create(
            {
                "name": message,
                "type": "server",
                "dbname": self.env.cr.dbname,
                "message": message,
                "path": path,
                "func": func,
                "line": 1,
            })

    def write(self, values):
        sequnce_ordigin = self.number_next_actual
        res = super(IrSequence, self).write(values)
        if self.code=='sequence.sale.order' and values.get('number_next') != sequnce_ordigin:
            _logger.info(self.env.user.name + " "+ "Change number sequence:- origin: %s,sequnce last : %s", sequnce_ordigin,self.number_next_actual)
            self.create_ir_loging(message=("Change number sequence:- origin:",sequnce_ordigin,"-","sequnce last:", self.number_next_actual),path=self._name,func='write')
        return res