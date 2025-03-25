# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class ReportController(http.Controller):
    
    @http.route('/report/update_rubbertest_ghichu', type='json', auth="user")
    def update_rubbertest_ghichu(self):
        try:
            # Get data from the request
            data = request.jsonrequest
            _logger.info(f"Received data: {data}")
            
            rubbertestbydate_id = data.get('rubbertestbydate_id')
            plantation_test_id = data.get('plantation_test_id')
            ghichu = data.get('ghichu', '')
            
            if not rubbertestbydate_id or not plantation_test_id:
                _logger.warning("Missing required parameters")
                return {'success': False, 'error': 'Missing required parameters'}
            
            # Find the rubber test record
            domain = [
                ('rubbertestbydate_id', '=', int(rubbertestbydate_id)),
                ('plantationtest_id', '=', int(plantation_test_id)),
            ]
            
            _logger.info(f"Searching with domain: {domain}")
            rubber_test = request.env['rubber.test'].search(domain, limit=1)
            
            if not rubber_test:
                _logger.warning(f"No record found with domain: {domain}")
                
                # Check if the record exists at all
                test_by_date = request.env['rubber.test.date'].browse(int(rubbertestbydate_id))
                plantation = request.env['plantation.test'].browse(int(plantation_test_id))
                
                _logger.info(f"Test by date exists: {test_by_date.exists()}, Plantation test exists: {plantation.exists()}")
                
                # Try to create the record if it doesn't exist
                if test_by_date.exists() and plantation.exists():
                    _logger.info(f"Creating new rubber.test record")
                    rubber_test = request.env['rubber.test'].create({
                        'rubbertestbydate_id': int(rubbertestbydate_id),
                        'plantationtest_id': int(plantation_test_id),
                        'ghichu': ghichu
                    })
                    return {'success': True, 'created': True}
                else:
                    return {'success': False, 'error': 'Record not found and could not be created'}
            
            # Update the ghichu field
            _logger.info(f"Found record ID {rubber_test.id}, updating ghichu to: {ghichu}")
            result = rubber_test.write({'ghichu': ghichu})
            _logger.info(f"Update result: {result}")
            
            return {'success': True}
        except Exception as e:
            _logger.exception(f"Error updating rubber test ghichu: {str(e)}")
            return {'success': False, 'error': str(e)}