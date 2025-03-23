from odoo import api, models
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class ReportRubber(models.AbstractModel):
    _name = 'report.caosu.rubber_report_template'
    _description = 'Rubber Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        # Use setdefault like in rubbertest
        data.setdefault('lo', 'a')
        data.setdefault('nhom', 'all')
        data.setdefault('compare_field', 'cong')
        data.setdefault('detail_field', 'none')
        data.setdefault('sort_order', 'desc')
        data.setdefault('dao_kt', '')        
        # For the 'to' field, use the same approach as rubbertest
        if not data.get('to'):
            # Set default department
            department = self.env['hr.department'].search([('name', '=', 'TỔ 70-25')], limit=1)
            data['to'] = department.id if department else ''
        
        # Extract parameters
        selected_nhom = data.get('nhom')
        compare_field = data.get('compare_field')
        detail_field = data.get('detail_field')
        sort_order = data.get('sort_order')
        selected_lo = data.get('lo')
        selected_to = data.get('to')
        dao_kt = data.get('dao_kt')
        
        # Convert selected_to to int for comparisons
        selected_to_int = False
        if selected_to:
            try:
                selected_to_int = int(selected_to)
            except (ValueError, TypeError):
                pass
        
        # HARDCODED DEPARTMENT APPROACH
        # Replace your hardcoded_departments list with this:
        available_to = self.env['rubber.department.config'].get_departments()
        
        # 2. SECOND: Fetch all available options BEFORE any data processing
        # Force immediate evaluation with list() and store as lists
        
        available_lo = self.env['plantation'].fields_get(['lo'])['lo']['selection']        
        available_nhom_group = self.env['plantation'].read_group([], ['nhom'], ['nhom'])
        available_nhom = [{'id': 'all', 'name': 'Tất cả'}]
        for group in available_nhom_group:
            value = group.get('nhom')
            if value:
                available_nhom.append({'id': value, 'name': value.capitalize()})
        
        available_dao_group = self.env['rubber'].read_group([], ['dao_kt'], ['dao_kt'])
        available_dao = [{'id': '', 'name': 'Tất cả'}]
        for grp in available_dao_group:
            dao_val = grp.get('dao_kt')
            if dao_val not in (False, None):
                available_dao.append({'id': dao_val, 'name': str(dao_val)})
        
        # 3. THIRD: Build your domain and process data
        domain = []
        if selected_nhom and selected_nhom != 'all':
            domain.append(('nhom', '=', selected_nhom))
        if selected_to_int:  # Use selected_to_int consistently
            domain.append(('to', '=', selected_to_int))
        if selected_lo and selected_lo.strip():
            domain.append(('lo', '=', selected_lo))
        
        # Retrieve plantation records based on domain, ordered by sttcn.
        plantation_objs = self.env['plantation'].search(domain, order='sttcn')
        # Build dynamic column headers.
        cols = []
        for pt in plantation_objs:
            try:
                employee_name = pt.employee_id.name
                employee_address = pt.employee_id.diachi if hasattr(pt.employee_id, 'diachi') else ''
            except Exception as e:
                employee_name = "N/A"
                employee_address = ""
                _logger.warning(f"Error accessing employee data: {e}")
            if ('-' in employee_name):
                employee_name = employee_name.split('-')[0].strip()
            cols.append({
                'id': pt.id,
                'name': pt.sttcn,
                'CN': employee_name  # Trimmed name, removed characters to the right of '-'
            })
        
        # Retrieve rubber records for those plantations.
        plantation_ids = [pt.id for pt in plantation_objs]
        rubber_domain = [('plantation_id', 'in', plantation_ids)]
        # Add filter for dao_kt if provided.
        if dao_kt and dao_kt != 'all':
            rubber_domain.append(('dao_kt', '=', dao_kt))
        # Add filter for rubberbydate_id.cong > 0
        rubber_domain.append(('rubberbydate_id.tongmu', '>', 0))
        rubber_objs = self.env['rubber'].search(rubber_domain)
        
        # Group rubber records by their rubbertestbydate.
        grouped = {}
        for rec in rubber_objs:
            if not rec.rubberbydate_id:
                continue
            group_key = rec.rubberbydate_id.id
            if group_key not in grouped:
                try:
                    if hasattr(rec.rubberbydate_id.ngay, 'strftime'):
                        date_value = rec.rubberbydate_id.ngay
                    else:
                        date_value = datetime.strptime(rec.rubberbydate_id.ngay, '%Y-%m-%d')
                    long_date = date_value.strftime('%d.%m.%y')
                except Exception:
                    long_date = rec.rubberbydate_id.ngay or 'No Name'
                    date_value = datetime.min
                grouped[group_key] = {
                    'id': group_key,
                    'name': long_date,
                    'date_value': date_value,
                    'group_values': {col['id']: {'value': 0, 'kichthich': False, 'background': ''} for col in cols},
                }
                if detail_field != 'none':
                    grouped[group_key]['group_detail_values'] = {col['id']: {'value': 0} for col in cols}
            plant_id = rec.plantation_id.id
            selection_label = rec.ctktup.background or (rec.rubberbydate_id.ctktup.background if rec.rubberbydate_id and rec.rubberbydate_id.ctktup else '')

            # Get the raw value
            raw_value = getattr(rec, compare_field, 0)

            # Format the value based on field type
            if compare_field in ('quykho', 'do_phancay', 'muday'):
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

            cell_data = {
                'value': formatted_value,
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
                elif detail_field in ('quykho', 'do_phancay', 'muday'):
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
                
                grouped[group_key]['group_detail_values'][plant_id] = {'value': detail_val}
        
        # Sort rows by ngay.
        rows = sorted(
            list(grouped.values()),
            key=lambda g: g.get('date_value') or datetime.min,
            reverse=(sort_order == 'desc')
        )
        
        # Generate HTML directly in Python
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
            selected = "selected" if selected_nhom == nhom_rec['id'] else ""
            nhom_options += f'<option value="{nhom_rec["id"]}" {selected}>{nhom_rec["name"]}</option>'

        dao_options = '<option value="" ' + ("selected" if not dao_kt else "") + '>-- All --</option>'
        for dao in available_dao:
            selected = "selected" if str(dao_kt) == str(dao['id']) else ""
            dao_options += f'<option value="{dao["id"]}" {selected}>{dao["name"]}</option>'

        detail_field_options = [
            ('none', 'hông chọn'),
            ('kichthich', 'Kichthich'),
            ('do_phancay', 'Độ'),
            ('quykho', 'Quy khô'),
        ]
        detail_options = ""
        for detail_opt in detail_field_options:
            selected = "selected" if detail_field == detail_opt[0] else ""
            detail_options += f'<option value="{detail_opt[0]}" {selected}>{detail_opt[1]}</option>'

        compare_field_options = [
            ('cong', 'Cộng'),
            ('quykho', 'Quy khô'),
            ('congnuoc', 'Cộng nước'),
            ('congtap', 'Cộng tạp'),
            ('muday', 'Mũ dây'),
            ('muchen', 'Mũ chén'),
            ('mudong', 'Mũ đông'),
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
            'available_to': available_to,  # Use hardcoded list
            'available_lo': available_lo,
            'selected_to': selected_to,
            'selected_to_int': selected_to_int,
            'selected_lo': selected_lo,
            'available_nhom': available_nhom,
            'available_dao': available_dao,
            'dao_kt': dao_kt,
            'to_options_html': to_options,
            'lo_options_html': lo_options,
            'nhom_options_html': nhom_options,
            'dao_options_html': dao_options,
            'detail_options_html': detail_options,
            'compare_options_html': compare_options,
        }
