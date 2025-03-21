from odoo import api, models
from datetime import datetime

class ReportRubberTest(models.AbstractModel):
    _name = 'report.caosu.rubbertest_report_template'
    _description = 'Rubber Test Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        data = data or {}
        # Retrieve parameters from wizard-data. Cast to string where needed.
        selected_nhom = data.get('nhom', 'all')
        compare_field = data.get('compare_field', 'mu_up')
        detail_field = data.get('detail_field', 'none')
        sort_order = data.get('sort_order', 'desc')
        selected_to = str(data.get('to', ''))
        selected_lo = str(data.get('lo', 'a'))
        dao_kt_up = str(data.get('dao_kt_up', ''))

        # Field label mapping.
        field_labels = {
            'mu_up': 'Mũ Cạo Up',
            'do_up': 'Đỏ Cạo Up',
            'mu_ngua': 'Mũ Ngửa',
            'do_ngua': 'Đỏ Ngửa',
            'kichthich': 'Kích Thích',
            'none': 'None',
        }
        compare_field_label = field_labels.get(compare_field, compare_field)
        detail_field_label = field_labels.get(detail_field, detail_field)

        # Build domain for plantation.test records.
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

        # Retrieve plantation.test records ordered by socay.
        plantation_cols = self.env['plantation.test'].search(domain, order='socay')
        cols = []
        for pt in plantation_cols:
            cols.append({
                'id': pt.id,
                'name': pt.socay.name,
                'vanhcay': pt.vanhcay,  # Make sure this field exists on plantation.test
            })

        # Retrieve rubber.test records for those plantations.
        plantation_ids = [pt.id for pt in plantation_cols]
        rubber_domain = [('plantationtest_id', 'in', plantation_ids)]
        if dao_kt_up and dao_kt_up.strip():
            try:
                dao_kt_up_val = int(dao_kt_up)
            except ValueError:
                dao_kt_up_val = dao_kt_up
            rubber_domain.append(('dao_kt_up', '=', dao_kt_up_val))
        rubber_tests = self.env['rubber.test'].search(rubber_domain)

        # Group rubber.test records by their rubbertestbydate.
        grouped = {}
        for rec in rubber_tests:
            if not rec.rubbertestbydate_id:
                continue
            group_key = rec.rubbertestbydate_id.id
            if group_key not in grouped:
                try:
                    if hasattr(rec.rubbertestbydate_id.ngay, 'strftime'):
                        date_value = rec.rubbertestbydate_id.ngay
                    else:
                        date_value = datetime.strptime(rec.rubbertestbydate_id.ngay, '%Y-%m-%d')
                    long_date = date_value.strftime('%d.%m.%y')
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
            cell_data = {
                'value': int(getattr(rec, compare_field, 0)),
                'kichthich': bool(getattr(rec, 'kichthich', False)),
                'ctktup': getattr(rec, 'ctktup').name if getattr(rec, 'ctktup', False) else '',
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

        rows = sorted(
            list(grouped.values()),
            key=lambda g: g.get('date_value') or datetime.min,
            reverse=(sort_order == 'desc')
        )

        # Load available filter options.
        available_to = self.env['hr.department'].search([('name','ilike','TỔ')], order='name')
        available_lo = self.env['plantation.test'].fields_get(['lo'])['lo']['selection']
        available_nhom_group = self.env['plantation.test'].read_group([], ['nhom'], ['nhom'])
        available_nhom = [{'id': 'all', 'name': 'All'}]
        for group in available_nhom_group:
            value = group.get('nhom')
            if value:
                available_nhom.append({'id': value, 'name': value.capitalize()})

        available_dao_group = self.env['rubber.test'].read_group([], ['dao_kt_up'], ['dao_kt_up'])
        available_dao = [{'id': '', 'name': '-- All --'}]
        for grp in available_dao_group:
            dao_val = grp.get('dao_kt_up')
            if dao_val not in (False, None):
                available_dao.append({'id': dao_val, 'name': str(dao_val)})

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
            'dao_kt_up': dao_kt_up,
        }