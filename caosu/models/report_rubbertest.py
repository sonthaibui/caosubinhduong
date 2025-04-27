from odoo import api, models
from datetime import datetime
import io
import xlsxwriter
from odoo.http import content_disposition, request
import logging

_logger = logging.getLogger(__name__)

class ReportRubberTest(models.AbstractModel):
    _name = 'report.caosu.rubbertest_report_template'
    _description = 'Rubber Test Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        
        # Get the department record with name TỔ 140 and return its id
        if not data.get('to'):
            department = self.env['hr.department'].search([('name', '=', 'TỔ 140')], limit=1)
            data['to'] = department.id if department else ''
         

        # Add this list at the top of the _get_report_values method (after parameters are extracted)
        decimal_fields = ['do_up', 'do_ngua', 'do_bo', 'quykho_up', 'quykho_ngua', 'do_up3', 'do_up6', 'chenhlechkho_up', 'chenhlechkho_ngua']

        # Use empty strings when parameter is not provided
        selected_nhom = data.get('nhom', 'all')
        compare_field = data.get('compare_field', 'mu_up')
        detail_field = data.get('detail_field', 'none')
        sort_order = data.get('sort_order', 'desc')        
        selected_lo = str(data.get('lo', 'a'))
        selected_to = data.get('to')
        dao_kt_up = data.get('dao_kt_up', 'all')
        
        # Convert selected_to to int for comparisons
        selected_to_int = False
        if selected_to:
            try:
                selected_to_int = int(selected_to)
            except (ValueError, TypeError):
                pass
        
        # Use the configured departments instead of hardcoded list
        available_to = self.env['rubbertest.department.config'].get_departments()
        
        # Build domain for plantation.test based on parameters.
        domain = []
        if selected_nhom and selected_nhom != 'all':
            try:
                nhom_id = int(selected_nhom)
                # Filter where the many2many field nhom_ids includes the selected nhom.
                domain.append(('nhom_ids', 'in', [nhom_id]))
            except ValueError:
                pass
        if selected_to:
            try:
                to_val = int(selected_to)
            except ValueError:
                to_val = selected_to
            domain.append(('to', '=', to_val))
        if selected_lo:
            domain.append(('lo', '=', selected_lo))

        # Build a single domain for plantation tests (removed duplicate code)
        plantation_filter_domain = []

        # Only add filters if we have values
        if selected_nhom and selected_nhom != 'all':
            try:
                nhom_id = int(selected_nhom)
                # Only filter on nhom if it's a valid ID
                if nhom_id > 0:
                    plantation_filter_domain.append(('nhom_ids', 'in', [nhom_id]))
            except (ValueError, TypeError):
                pass

        if selected_to:
            try:
                to_val = int(selected_to)
                # Add to_val as integer if conversion succeeded
                plantation_filter_domain.append(('to', '=', to_val))
            except (ValueError, TypeError):
                # Otherwise use the original string value
                plantation_filter_domain.append(('to', '=', selected_to))

        if selected_lo and selected_lo != '':
            plantation_filter_domain.append(('lo', '=', selected_lo))

        # Get all plantation tests if no filters are provided
        if not plantation_filter_domain:
            available_plantation_tests = self.env['plantation.test'].search([], order='socay', limit=100)
        else:
            available_plantation_tests = self.env['plantation.test'].search(plantation_filter_domain, order='socay')

        # For debugging - log or print these values
        #_logger.info(f"Plantation filter domain: {plantation_filter_domain}")
        #_logger.info(f"Available plantation tests: {len(available_plantation_tests)}")

        # Modify this section for processing selected plantation tests
        selected_plantation_tests = []
        sel_pt_raw = data.get('selected_plantation_tests')

        # Enable debugging to see what format we're receiving
        #_logger.info(f"Raw selected plantation tests: {sel_pt_raw} (type: {type(sel_pt_raw)})")

        # Handle all possible formats of selected_plantation_tests
        if sel_pt_raw:
            # Case 1: Value is already a list
            if isinstance(sel_pt_raw, list):
                for item in sel_pt_raw:
                    try:
                        selected_plantation_tests.append(int(item))
                    except (ValueError, TypeError):
                        pass
            
            # Case 2: Value is a string that might contain multiple values
            elif isinstance(sel_pt_raw, str):
                # Try parsing as JSON array first
                if sel_pt_raw.startswith('[') and sel_pt_raw.endswith(']'):
                    try:
                        import json
                        values = json.loads(sel_pt_raw)
                        if isinstance(values, list):
                            for item in values:
                                try:
                                    selected_plantation_tests.append(int(item))
                                except (ValueError, TypeError):
                                    pass
                    except:
                        pass
                
                # Try as comma-separated string
                elif ',' in sel_pt_raw:
                    for item in sel_pt_raw.split(','):
                        try:
                            selected_plantation_tests.append(int(item.strip()))
                        except (ValueError, TypeError):
                            pass
                
                # Try as single value
                else:
                    try:
                        selected_plantation_tests.append(int(sel_pt_raw))
                    except (ValueError, TypeError):
                        pass

        #_logger.info(f"Processed selected plantation tests: {selected_plantation_tests}")

        # Build domain for fetching cols
        # Use either selected plantation tests or the filtered domain
        if selected_plantation_tests:
            # Use only the selected plantation tests
            plantation_cols = self.env['plantation.test'].search([('id', 'in', selected_plantation_tests)], order='socay')
        else:
            # Use all plantation tests matching the filter domain
            plantation_cols = self.env['plantation.test'].search(plantation_filter_domain, order='socay')

        # Convert to your existing cols format
        cols = []
        for rec in plantation_cols:
            cols.append({
                'id': rec.id,
                'name': rec.socay.name,
                'vanhcay': rec.vanhcay,
                'somu': rec.somu,
            })

        plantation_ids = [pt.id for pt in plantation_cols]
        rubber_domain = [('plantationtest_id', 'in', plantation_ids)]
        if dao_kt_up and dao_kt_up.strip() and dao_kt_up.isdigit():
            dao_kt_up_val = int(dao_kt_up)
            rubber_domain.append(('dao_kt_up', '=', dao_kt_up_val))
        rubber_tests = self.env['rubber.test'].search(rubber_domain)

        grouped = {}
        for rec in rubber_tests:
            if not rec.rubbertestbydate_id:
                continue
            group_key = rec.rubbertestbydate_id.id
            if group_key not in grouped:
                try:
                    date_value = rec.rubbertestbydate_id.ngay
                    long_date = date_value.strftime('%d.%m.%y') if hasattr(date_value, 'strftime') else date_value
                except Exception:
                    long_date = rec.rubbertestbydate_id.ngay or 'No Name'
                    date_value = datetime.min
                grouped[group_key] = {
                    'id': group_key,
                    'name': long_date,
                    'date_value': date_value,
                    'group_values': {col['id']: {'value': 0, 'kichthich': False, 'ctktup': ''} for col in cols},
                }
                if detail_field != 'none':
                    grouped[group_key]['group_detail_values'] = {col['id']: {'value': 0} for col in cols}
            plant_id = rec.plantationtest_id.id
            selection_label = rec.ctktup.background if rec.ctktup else ''

            # Get the raw value
            raw_value = getattr(rec, compare_field, 0)

            # Format the value based on field type
            if compare_field in decimal_fields:
                try:
                    # Convert to float and format with one decimal place
                    formatted_value = f"{float(raw_value):.1f}"
                except (ValueError, TypeError):
                    formatted_value = raw_value
            else:
                try:
                    # For other fields, use integer formatting
                    formatted_value = int(raw_value)
                except (ValueError, TypeError):
                    formatted_value = raw_value

            # 1. For compare_field values - update the cell_data creation:
            cell_data = {
                'value': formatted_value if formatted_value not in [0, '0', '0.0', 0.0] else '-',
                'kichthich': bool(getattr(rec, 'kichthich', False)),
                'background': selection_label,
                'ghichu': getattr(rec, 'ghichu', ''),
            }
            grouped[group_key]['group_values'][plant_id] = cell_data
            if detail_field != 'none':
                try:
                    raw_val = getattr(rec, detail_field, '')
                except Exception:
                    raw_val = ''
                
                if detail_field == 'kichthich':
                    detail_val = 'Yes' if raw_val else 'No'
                # Add special handling for fields that need one decimal place
                elif detail_field in decimal_fields:
                    try:
                        # Convert to float and format with one decimal place
                        float_val = float(raw_val)
                        detail_val = f"{float_val:.1f}"
                    except (ValueError, TypeError):
                        detail_val = raw_val
                else:
                    try:
                        detail_val = int(raw_val)
                    except Exception:
                        detail_val = raw_val
                
                # 2. For detail_field values - update after detail_val is calculated:
                # Convert zero values to '-' (place after all the detail_val calculations)
                if detail_val in [0, '0', '0.0', 0.0]:
                    detail_val = '-'
                
                grouped[group_key]['group_detail_values'][plant_id] = {'value': detail_val}

        rows = sorted(
            list(grouped.values()),
            key=lambda g: g.get('date_value') or datetime.min,
            reverse=(sort_order == 'desc')
        )

        # Build available options.
        available_nhom = [{'id': 'all', 'name': 'Tất cả'}]
        for nhom in self.env['rubber.test.nhom'].search([]):
            available_nhom.append({'id': nhom.id, 'name': nhom.name})
        available_lo = self.env['plantation.test'].fields_get(['lo'])['lo']['selection']
        available_dao = [{'id': '', 'name': 'Tất cả'}]
        for grp in self.env['rubber.test'].read_group([], ['dao_kt_up'], ['dao_kt_up']):
            dao_val = grp.get('dao_kt_up')
            if dao_val not in (False, None):
                available_dao.append({'id': dao_val, 'name': str(dao_val)})

        # Generate HTML directly in Python for each dropdown
        to_options = ""
        for dept in available_to:
            selected = "selected" if str(selected_to) == str(dept.id) else ""
            to_options += f'<option value="{dept.id}" {selected}>{dept.name}</option>'

        lo_options = '<option value="" ' + ("selected" if not selected_lo else "") + '>-- All --</option>'
        for lo_opt in available_lo:
            selected = "selected" if selected_lo == lo_opt[0] else ""
            lo_options += f'<option value="{lo_opt[0]}" {selected}>{lo_opt[1]}</option>'

        nhom_options = ""
        for nhom_rec in available_nhom:
            # Convert both values to strings for proper comparison
            selected = "selected" if str(selected_nhom) == str(nhom_rec['id']) else ""
            nhom_options += f'<option value="{nhom_rec["id"]}" {selected}>{nhom_rec["name"]}</option>'

        dao_options = '<option value="" ' + ("selected" if not dao_kt_up else "") + '>-- All --</option>'
        for dao in available_dao:
            selected = "selected" if str(dao_kt_up) == str(dao['id']) else ""
            dao_options += f'<option value="{dao["id"]}" {selected}>{dao["name"]}</option>'

        detail_field_options = [
            ('none', 'Không chọn'),
            ('kichthich', 'Kichthich'),
            ('do_up', 'Độ úp'),
            ('do_phancay', 'Độ'),
            ('mu_ngua', 'Mũ ngửa'),
            ('do_ngua', 'Độ ngửa'),
            ('mu_bo', 'Mũ bợ'),
            ('do_bo', 'Độ bợ'),
            ('quykho_up', 'Quy khô úp'),
            ('quykho_ngua', 'Quy khô ngửa'),            

        ]
        detail_options = ""
        for detail_opt in detail_field_options:
            selected = "selected" if detail_field == detail_opt[0] else ""
            detail_options += f'<option value="{detail_opt[0]}" {selected}>{detail_opt[1]}</option>'

        compare_field_options = [
            ('cong', 'Mũ'),
            ('mu_up', 'Mũ Up'),
            ('mu_ngua', 'Mũ ngửa'),
            ('mu_bo', 'Mũ bợ'),
            ('quykho_up', 'Quy khô úp'),
            ('quykho_ngua', 'Quy khô ngửa'),
            ('do_up', 'Độ úp'),
            ('do_ngua', 'Độ ngửa'),
        ]
        compare_options = ""
        for comp_opt in compare_field_options:
            selected = "selected" if compare_field == comp_opt[0] else ""
            compare_options += f'<option value="{comp_opt[0]}" {selected}>{comp_opt[1]}</option>'
        
        # Return all options HTML
        return {
            'docs': rows,
            'cols': cols,
            'compare_field': compare_field,            
            'detail_field': detail_field,            
            'selected_nhom': selected_nhom,
            'sort_order': sort_order,
            'available_nhom': available_nhom,
            'available_to': available_to,
            'available_lo': available_lo,
            'selected_to': selected_to,
            'selected_to_int': selected_to_int,
            'selected_lo': selected_lo,
            'dao_kt_up': dao_kt_up,
            'available_dao': available_dao,
            'available_plantation_tests': available_plantation_tests,
            'selected_plantation_tests': selected_plantation_tests,
            
            # New HTML options
            'to_options_html': to_options,
            'lo_options_html': lo_options,
            'nhom_options_html': nhom_options,
            'dao_options_html': dao_options,
            'detail_options_html': detail_options,
            'compare_options_html': compare_options,
        }

    def create_excel_report(self, data):
        """Create Excel report based on the report data"""
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Rubber Test Report')

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#f8f9fa',
            'border': 1
        })

        data_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        vanh_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'italic': True,
            'bg_color': '#f2f2f2'
        })

        # Get report values
        report_values = self._get_report_values(None, data)
        cols = report_values.get('cols', [])
        docs = report_values.get('docs', [])  # Changed from grouped to docs

        # Write first header row - Cay numbers
        worksheet.write(0, 0, 'Ngày', header_format)
        for col_idx, col in enumerate(cols, 1):
            worksheet.write(0, col_idx, col['name'], header_format)

        # Write second header row - Vanh values
        worksheet.write(1, 0, 'Vanh', vanh_format)
        for col_idx, col in enumerate(cols, 1):
            worksheet.write(1, col_idx, col['vanhcay'], vanh_format)

        # Write data rows starting from row 2
        for row_idx, group in enumerate(docs, 2):  # Changed from grouped.values() to docs
            # Write date
            worksheet.write(row_idx, 0, group['name'], data_format)
            
            # Write values for each column
            for col_idx, col in enumerate(cols, 1):
                cell_data = group['group_values'].get(col['id'], {})
                value = cell_data.get('value', '-')
                
                # Create a new format for this cell to include background color if present
                cell_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1
                })
                
                # Add background color if present
                if cell_data.get('background'):
                    cell_format.set_bg_color(cell_data['background'])
                
                # Add bold if kichthich is True
                if cell_data.get('kichthich'):
                    cell_format.set_bold(True)
                
                worksheet.write(row_idx, col_idx, value, cell_format)

        # Set column widths
        worksheet.set_column(0, 0, 20)  # Date column
        worksheet.set_column(1, len(cols), 15)  # Data columns
        
        # Freeze panes for better viewing
        worksheet.freeze_panes(2, 1)  # Freeze the first two rows and first column

        workbook.close()
        output.seek(0)

        return output.getvalue()

    def create_pdf_report(self, data):
        """Create PDF report based on the report data"""
        # Get report values with the same structure as Excel
        report_values = self._get_report_values(None, data)
        
        # Get the report action
        report = self.env.ref('caosu.action_report_rubbertest_pdf')
        if not report:
            raise ValueError("PDF Report template not found")
        
        # Create a dummy record to render with
        dummy_record = self.env['rubber.test'].new({})
        
        # Generate PDF using the report action
        pdf_content = report._render([dummy_record.id], {
            'docs': report_values.get('docs', []),
            'cols': report_values.get('cols', []),
            'compare_field': report_values.get('compare_field'),
            'detail_field': report_values.get('detail_field'),
            'doc_model': 'rubber.test',
            'doc_ids': []
        })[0]
        
        return pdf_content