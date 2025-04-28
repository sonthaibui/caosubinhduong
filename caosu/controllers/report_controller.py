# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request, content_disposition
import logging
import io
import xlsxwriter
from datetime import datetime

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

    @http.route('/report/update_rubber_ghichu', type='json', auth="user")
    def update_rubber_ghichu(self):
        try:
            # Get data from the request
            data = request.jsonrequest
            _logger.info(f"Received data: {data}")
            
            rubberbydate_id = data.get('rubberbydate_id')
            plantation_id = data.get('plantation_id')
            ghichu = data.get('ghichu', '')
            
            if not rubberbydate_id or not plantation_id:
                _logger.warning("Missing required parameters")
                return {'success': False, 'error': 'Missing required parameters'}
            
            # Find the rubber record
            domain = [
                ('rubberbydate_id', '=', int(rubberbydate_id)),
                ('plantation_id', '=', int(plantation_id)),
            ]
            
            _logger.info(f"Searching with domain: {domain}")
            rubber = request.env['rubber'].search(domain, limit=1)
            
            if not rubber:
                _logger.warning(f"No record found with domain: {domain}")
                return {'success': False, 'error': 'Record not found'}
            
            # Update the ghichu field
            _logger.info(f"Found record ID {rubber.id}, updating ghichu to: {ghichu}")
            result = rubber.write({'ghichu': ghichu})
            _logger.info(f"Update result: {result}")
            
            return {'success': True}
        except Exception as e:
            _logger.exception(f"Error updating rubber ghichu: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/caosu/excel', type='http', auth="user", website=True)
    def export_excel_rubbertest(self, **kw):
        try:
            # Get report data using the same method as HTML report
            ReportRubberTest = request.env['report.caosu.rubbertest_report_template']
            
            # Initialize data dictionary with required fields
            data = {
                'compare_field': kw.get('compare_field', 'cong'),
                'detail_field': kw.get('detail_field', 'none')
            }
            
            # Handle to parameter carefully
            if kw.get('to'):
                try:
                    if kw.get('to') != 'all':
                        data['to'] = int(kw.get('to'))
                except (ValueError, TypeError):
                    data['to'] = kw.get('to')  # Keep original value if not convertible to int
            
            # Handle other parameters
            if kw.get('lo'):
                data['lo'] = kw.get('lo')  # Keep as string
                
            if kw.get('dao_kt_up'):
                try:
                    if kw.get('dao_kt_up') != 'all':
                        data['dao_kt_up'] = int(kw.get('dao_kt_up'))
                except (ValueError, TypeError):
                    pass
                
            if kw.get('nhom'):
                try:
                    if kw.get('nhom') != 'all':
                        data['nhom'] = int(kw.get('nhom'))
                except (ValueError, TypeError):
                    pass

            # Get Excel binary data
            excel_data = ReportRubberTest.create_excel_report(data)
            
            filename = f'rubber_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            
            headers = [
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename))
            ]
            
            return request.make_response(excel_data, headers=headers)

        except Exception as e:
            _logger.error("Excel export error: %s", str(e), exc_info=True)
            return "Error generating Excel file: " + str(e)

    @http.route('/caosu/test', type='http', auth="user")
    def test_controller(self, **kw):
        return "Controller is working"