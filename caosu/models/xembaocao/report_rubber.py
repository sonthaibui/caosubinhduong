import io
import xlsxwriter
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
        # Get all parameters with defaults
        selected_lo = data.get('lo', 'a')
        selected_nhom = data.get('nhom', 'all')
        compare_field = data.get('compare_field', 'cong')
        detail_field = data.get('detail_field', 'none')
        sort_order = data.get('sort_order', 'desc')
        dao_kt = data.get('dao_kt', '')
        selected_nam = data.get('nam', 'Tất cả')
        selected_thang = data.get('thang', 'Tất cả')
        show_tree_count = data.get('show_tree_count', False)

        # For the 'to' field, special handling with default
        if 'to' not in data:
            department = self.env['hr.department'].search([('name', '=', 'TỔ 70-25')], limit=1)
            selected_to = department.id if department else ''
        else:
            selected_to = data.get('to')

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

        # Add this after defining your columns but before processing the rows
        # Create a map of plantation IDs to their tree counts
        tree_counts = {}
        if show_tree_count:
            # Get all plantation IDs from your columns
            plantation_ids = [col['id'] for col in cols]
            # Fetch tree count data efficiently with a single query
            plantations = self.env['plantation'].browse(plantation_ids).read(['caycao'])
            # Create a mapping of ID to tree count
            tree_counts = {p['id']: p['caycao'] or 0 for p in plantations}

        # Retrieve rubber records for those plantations.
        plantation_ids = [pt.id for pt in plantation_objs]
        rubber_domain = [('plantation_id', 'in', plantation_ids)]
        # Add filter for dao_kt if provided.
        if dao_kt and dao_kt != 'all':
            rubber_domain.append(('dao_kt', '=', dao_kt))
        # Add filter for year if selected
        if selected_nam and selected_nam != 'Tất cả':
            rubber_domain.append(('rubberbydate_id.nam_kt', '=', selected_nam))
        # Add filter for month if selected
        if selected_thang and selected_thang != 'Tất cả':
            rubber_domain.append(('rubberbydate_id.thang', '=', selected_thang))
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
                    'do_giao': rec.rubberbydate_id.do_giao or 0,  # Add this line
                    'tongmu': rec.rubberbydate_id.tongmu or 0,    # Add this line
                    'group_values': {col['id']: {'value': 0, 'kichthich': False, 'background': ''} for col in cols},
                }
                if detail_field != 'none':
                    grouped[group_key]['group_detail_values'] = {col['id']: {'value': 0} for col in cols}
            plant_id = rec.plantation_id.id
            selection_label = rec.ctktup.background or (rec.rubberbydate_id.ctktup.background if rec.rubberbydate_id and rec.rubberbydate_id.ctktup else '')

            # Get the raw value
            raw_value = getattr(rec, compare_field, 0)

            try:
                # Check for zero value first
                if float(raw_value) == 0:
                    formatted_value = '-'
                elif compare_field in ('quykho', 'do_phancay', 'muday'):
                    # Format with one decimal place for specific fields
                    formatted_value = f"{float(raw_value):.1f}"
                else:
                    # Integer formatting for other fields
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
                        if float_val == 0:
                            detail_val = '-'
                        else:
                            detail_val = f"{float_val:.1f}"
                    except (ValueError, TypeError):
                        detail_val = '-' if raw_val == 0 or raw_val == '0' else raw_val
                else:
                    try:
                        val = float(raw_val)
                        if val == 0:
                            detail_val = '-'
                        else:
                            detail_val = int(val)
                    except Exception:
                        detail_val = '-' if raw_val == 0 or raw_val == '0' else raw_val

                grouped[group_key]['group_detail_values'][plant_id] = {'value': detail_val}

        # In your _get_report_values method, add these values to each group
        for rec in rubber_objs:
            # Process each rubber record
            group_key = rec.rubberbydate_id.id

            if group_key not in grouped:
                # Format the date for display
                date_value = rec.rubberbydate_id.ngay
                try:
                    if hasattr(date_value, 'strftime'):
                        long_date = date_value.strftime('%A, %d %B %Y')
                    else:
                        date_obj = datetime.strptime(date_value, '%Y-%m-%d')
                        long_date = date_obj.strftime('%A, %d %B %Y')
                except Exception as e:
                    long_date = date_value

                # Get do_giao and tongmu values from rubberbydate_id
                do_giao_val = rec.rubberbydate_id.do_giao or 0
                do_giao_formatted = f"{float(do_giao_val):.1f}" if do_giao_val else '-'

                tongmu_val = rec.rubberbydate_id.tongmu or 0
                tongmu_formatted = f"{int(tongmu_val)}" if tongmu_val else '-'

                grouped[group_key] = {
                    'id': group_key,
                    'name': long_date,
                    'date_value': date_value,
                    'do_giao': do_giao_formatted,   # Add formatted do_giao
                    'tongmu': tongmu_formatted,     # Add formatted tongmu
                    'group_values': {},
                    'group_detail_values': {},
                }

        # Calculate total_tongmu for the header if needed
        total_tongmu = 0
        for group in grouped.values():
            tongmu_val = group.get('tongmu')
            if tongmu_val and tongmu_val != '-':
                try:
                    if isinstance(tongmu_val, str):
                        tongmu_val = tongmu_val.replace(',', '')
                    num_value = int(float(tongmu_val))
                except (ValueError, TypeError):
                    num_value = 0
                total_tongmu += num_value
        # After processing all groups, convert total_tongmu to Tấn (divide by 1000) and no decimals
        try:
            total_tongmu = int(total_tongmu)  # Ensure total_tongmu is an integer
        except (ValueError, TypeError):
            total_tongmu = 0  # Default to 0 if conversion fails

        # After processing all groups, convert total_tongmu to Tấn (divide by 1000) and no decimals
        total_tongmu = f"{total_tongmu // 1000} Tấn"

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

        # Get available months from rubber.date records
        thang_groups = self.env['rubber.date'].read_group([], ['thang'], ['thang'])
        thang_options = '<option value="Tất cả" ' + ("selected" if selected_thang == "Tất cả" else "") + '>Tất cả</option>'
        for thang in thang_groups:
            thang_val = thang.get('thang')
            if thang_val:
                selected = "selected" if str(selected_thang) == str(thang_val) else ""
                thang_options += f'<option value="{thang_val}" {selected}>{thang_val}</option>'

        # Get available years from rubber.date records
        nam_groups = self.env['rubber.date'].read_group([], ['nam_kt'], ['nam_kt'])
        nam_options = '<option value="Tất cả" ' + ("selected" if selected_nam == "Tất cả" else "") + '>Tất cả</option>'
        for nam in nam_groups:
            nam_val = nam.get('nam_kt')
            if nam_val:
                selected = "selected" if str(selected_nam) == str(nam_val) else ""
                nam_options += f'<option value="{nam_val}" {selected}>{nam_val}</option>'

        detail_field_options = [
            ('none', 'Không chọn'),
            ('kichthich', 'Kichthich'),
            ('do_phancay', 'Độ'),
            ('quykho', 'Quy khô'),
            ('congnuoc', 'Cộng nước'),
            ('congtap', 'Cộng tạp'),
            ('muday', 'Mũ dây'),
            ('muchen', 'Mũ chén'),
            ('mudong', 'Mũ đông'),
        ]
        detail_options = ""
        for detail_opt in detail_field_options:
            selected = "selected" if detail_field == detail_opt[0] else ""
            detail_options += f'<option value="{detail_opt[0]}" {selected}>{detail_opt[1]}</option>'

        compare_field_options = [
            ('cong', 'Cộng'),
            ('quykho', 'Quy khô'),
            ('do_phancay', 'Độ'),
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

        # Calculate column totals or averages based on compare_field
        column_totals = {}
        for col in cols:
            col_id = col['id']
            values = []

            # Collect all non-dash values for this column from all rows
            for row in rows:
                if col_id in row['group_values']:
                    val = row['group_values'][col_id]['value']
                    # Only process numeric values
                    if val != '-':
                        try:
                            values.append(float(val))
                        except (ValueError, TypeError):
                            pass

            # Calculate total or average based on compare_field
            if not values:
                column_totals[col_id] = '-'
            elif compare_field == 'do_phancay':
                # Calculate average for non-zero values
                non_zero_values = [v for v in values if v != 0]
                if non_zero_values:
                    avg = sum(non_zero_values) / len(non_zero_values)
                    # Format with one decimal place if specific field
                    column_totals[col_id] = f"{avg:.1f}" if avg != 0 else '-'
                else:
                    column_totals[col_id] = '-'
            else:
                # Calculate sum for other fields
                total = sum(values)
                if total == 0:
                    column_totals[col_id] = '-'
                # Format with one decimal place for specific fields
                elif compare_field in ('do_phancay', 'muday'):
                    column_totals[col_id] = f"{total:.1f}"
                else:
                    column_totals[col_id] = int(total)

        # Replace the current total_tongmu calculation with this new approach
        # Look for the section after calculating column_totals

        # Calculate total_tongmu based on sum of all column totals if compare_field is one of the specified fields
        total_tongmu = 0
        summing_fields = ['quykho', 'cong', 'congnuoc', 'congtap', 'mudong', 'muchen', 'muday']

        if compare_field in summing_fields:
            # Sum up all non-dash column totals
            for col_id, total in column_totals.items():
                if total != '-':
                    try:
                        # Convert to float first to handle decimal strings
                        total_tongmu += float(total)
                    except (ValueError, TypeError):
                        pass

            # Format as "X Tấn" - divided by 1000 and rounded to whole number
            if total_tongmu > 0:
                tons = int(total_tongmu / 1000)
                total_tongmu = f"{tons} Tấn"
            else:
                total_tongmu = "0 Tấn"
        else:
            # For other compare fields, don't show a sum total
            total_tongmu = '-'

        # Add to the return values
        return {
            'docs': rows,
            'cols': cols,
            'column_totals': column_totals,
            'tree_counts': tree_counts,
            'show_tree_count': show_tree_count,
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
            'selected_thang': selected_thang,
            'selected_nam': selected_nam,
            'to_options_html': to_options,
            'lo_options_html': lo_options,
            'nhom_options_html': nhom_options,
            'dao_options_html': dao_options,
            'detail_options_html': detail_options,
            'compare_options_html': compare_options,
            'thang_options_html': thang_options,
            'nam_options_html': nam_options,
            'total_tongmu': total_tongmu,  # Add the total
        }

    def create_excel_report(self, data):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Rubber Report')

        header_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#f8f9fa',
            'border': 1
        })
        vanh_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'italic': True,
            'bg_color': '#f2f2f2'
        })
        total_format = workbook.add_format({
            'bold': True,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bg_color': '#e6ffe6'
        })
        data_format = workbook.add_format({
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })

        report_values = self._get_report_values(None, data)
        cols = report_values.get('cols', [])
        docs = report_values.get('docs', [])
        total_tongmu = report_values.get('total_tongmu', 0)
        column_totals = report_values.get('column_totals', {})

        # First header row: STT, Độ, Tổng, plantation columns (col['name'])
        worksheet.write(0, 0, 'STT', header_format)
        worksheet.write(0, 1, 'Độ', header_format)
        worksheet.write(0, 2, 'Tổng', header_format)
        for col_idx, col in enumerate(cols, 3):
            worksheet.write(0, col_idx, col['name'], header_format)

        # Second header row: TÊN, -, -, plantation columns (col['CN'])
        worksheet.write(1, 0, 'TÊN', vanh_format)
        worksheet.write(1, 1, '-', vanh_format)
        worksheet.write(1, 2, '-', vanh_format)
        for col_idx, col in enumerate(cols, 3):
            worksheet.write(1, col_idx, col.get('CN', ''), vanh_format)

        # Third header row: Tổng, -, total_tongmu, column_totals
        worksheet.write(2, 0, 'Tổng', total_format)
        worksheet.write(2, 1, '-', total_format)
        worksheet.write(2, 2, total_tongmu if total_tongmu else '-', total_format)
        for col_idx, col in enumerate(cols, 3):
            worksheet.write(2, col_idx, column_totals.get(col['id'], ''), total_format)

        # Data rows: group['name'], group['do_giao'], group['tongmu'], then group_values
        for row_idx, group in enumerate(docs, 3):
            worksheet.write(row_idx, 0, group.get('name', ''), data_format)
            worksheet.write(row_idx, 1, group.get('do_giao', ''), data_format)
            worksheet.write(row_idx, 2, group.get('tongmu', ''), data_format)
            for col_idx, col in enumerate(cols, 3):
                cell_data = group.get('group_values', {}).get(col['id'], {})
                value = cell_data.get('value', '-')
                cell_format = workbook.add_format({
                    'align': 'center',
                    'valign': 'vcenter',
                    'border': 1
                })
                if cell_data.get('background'):
                    cell_format.set_bg_color(cell_data['background'])
                if cell_data.get('kichthich'):
                    cell_format.set_bold(True)
                worksheet.write(row_idx, col_idx, value, cell_format)

        worksheet.set_column(0, 0, 15)  # STT column
        worksheet.set_column(1, 2, 10)  # Độ, Tổng columns
        worksheet.set_column(3, 3 + len(cols), 12)  # Data columns
        worksheet.freeze_panes(3, 1)  # Freeze the first three rows and first column

        workbook.close()
        output.seek(0)
        return output.getvalue()
