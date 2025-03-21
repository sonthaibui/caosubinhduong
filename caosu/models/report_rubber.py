from odoo import api, models
from datetime import datetime

class ReportRubber(models.AbstractModel):
    _name = 'report.caosu.rubber_report_template'
    _description = 'Rubber Report'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        # Cast parameters to string to use .strip()
        selected_nhom = data.get('nhom', 'all')
        compare_field = data.get('compare_field', 'cong')
        detail_field = data.get('detail_field', 'none')
        sort_order = data.get('sort_order', 'desc')
        selected_to = str(data.get('to', ''))
        selected_lo = str(data.get('lo', 'a'))
        dao_kt = data.get('dao_kt', '')
        
        # Map field keys to human-readable labels.
        field_labels = {
            'cong': 'Cộng',
            'do_phancay': 'Độ',            
            'kichthich': 'Kichthich',
            'none': 'None',
        }
        compare_field_label = field_labels.get(compare_field, compare_field)
        detail_field_label = field_labels.get(detail_field, detail_field)
        
        # Build domain for plantation records.
        domain = []
        if selected_nhom and selected_nhom != 'all':
            domain.append(('nhom', '=', selected_nhom))
        if selected_to and selected_to.strip():
            try:
                to_val = int(selected_to)
            except ValueError:
                to_val = selected_to
            domain.append(('to', '=', to_val))
        if selected_lo and selected_lo.strip():
            domain.append(('lo', '=', selected_lo))
        
        # Retrieve plantation records based on domain, ordered by sttcn.
        plantation_objs = self.env['plantation'].search(domain, order='sttcn')
        # Build dynamic column headers.
        cols = []
        for pt in plantation_objs:
            employee_name = pt.employee_id.name
            if '-' in employee_name:
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
        if dao_kt:
            try:
                dao_kt_val = int(dao_kt)
            except ValueError:
                dao_kt_val = dao_kt
            rubber_domain.append(('dao_kt', '=', dao_kt_val))
        
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
                    'group_values': {col['id']: {'value': 0, 'kichthich': False, 'congthuc_kt': ''} for col in cols},
                }
                if detail_field != 'none':
                    grouped[group_key]['group_detail_values'] = {col['id']: {'value': 0} for col in cols}
            plant_id = rec.plantation_id.id
            selection_label = rec.congthuc_kt or (rec.rubberbydate_id.congthuc_kt if rec.rubberbydate_id and rec.rubberbydate_id.congthuc_kt else '')
            cell_data = {
                'value': int(getattr(rec, compare_field, 0)),
                'kichthich': bool(getattr(rec, 'kichthich', False)),
                'congthuc_kt': selection_label,
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
        
        # Load available options for "to" and "lo".
        available_to = self.env['hr.department'].search([('name','ilike','TỔ')], order='name')
        available_lo = self.env['plantation'].fields_get(['lo'])['lo']['selection']
        
        # Get distinct nhom values from plantation, include "all" as a default option.
        available_nhom_group = self.env['plantation'].read_group([], ['nhom'], ['nhom'])
        available_nhom = [{'id': 'all', 'name': 'All'}]
        for group in available_nhom_group:
            value = group.get('nhom')
            if value:
                available_nhom.append({'id': value, 'name': value.capitalize()})
        
        # Get distinct dao_kt values from rubber records.
        available_dao_group = self.env['rubber'].read_group([], ['dao_kt'], ['dao_kt'])
        available_dao = [{'id': '', 'name': '-- All --'}]
        for grp in available_dao_group:
            dao_val = grp.get('dao_kt')
            if dao_val not in (False, None):
                available_dao.append({
                    'id': dao_val,
                    'name': str(dao_val)
                })
        
        return {
            'docs': rows,
            'cols': cols,
            'compare_field': compare_field,
            'compare_field_label': compare_field_label,
            'detail_field': detail_field,
            'detail_field_label': detail_field_label,
            'selected_nhom': selected_nhom,
            'sort_order': sort_order,
            'available_to': available_to,
            'available_lo': available_lo,
            'selected_to': selected_to,
            'selected_lo': selected_lo,
            'available_nhom': available_nhom,
            'available_dao': available_dao,
            'dao_kt': dao_kt,
        }