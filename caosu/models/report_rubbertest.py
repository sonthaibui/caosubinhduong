from odoo import api, models
from datetime import datetime

class ReportRubberTest(models.AbstractModel):
    _name = 'report.caosu.rubbertest_report_template'
    _description = 'Rubber Test Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        data.setdefault('lo', 'a')
        data.setdefault('nhom', 'all')
        # Get the department record with name TỔ 140 and return its id
        if not data.get('to'):
            department = self.env['hr.department'].search([('name', '=', 'TỔ 140')], limit=1)
            data['to'] = department.id if department else ''
        data.setdefault('dao_kt_up', 'all')
        data.setdefault('compare_field', 'mu_up')
        data.setdefault('detail_field', 'none')
        data.setdefault('sort_order', 'desc')

        # Add this list at the top of the _get_report_values method (after parameters are extracted)
        decimal_fields = ['do_up', 'do_ngua', 'do_bo', 'quykho_up', 'quykho_ngua', 'do_up3', 'do_up6', 'chenhlechkho_up', 'chenhlechkho_ngua']

        # Use empty strings when parameter is not provided
        selected_nhom = data.get('nhom')
        compare_field = data.get('compare_field')
        detail_field = data.get('detail_field')
        sort_order = data.get('sort_order')        
        selected_lo = str(data.get('lo'))
        selected_to = data.get('to')
        dao_kt_up = data.get('dao_kt_up')
        
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

        plantation_cols = self.env['plantation.test'].search(domain, order='socay')
        cols = []
        for pt in plantation_cols:
            cols.append({
                'id': pt.id,
                'name': pt.socay.name,
                'vanhcay': pt.vanhcay,
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
            selected = "selected" if selected_nhom == nhom_rec['id'] else ""
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
            
            # New HTML options
            'to_options_html': to_options,
            'lo_options_html': lo_options,
            'nhom_options_html': nhom_options,
            'dao_options_html': dao_options,
            'detail_options_html': detail_options,
            'compare_options_html': compare_options,
        }