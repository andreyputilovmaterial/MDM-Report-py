# MDD report enhancement: combine attribute columns into the master name column.

import re
import json


def mdd_combine_attributes(ctx):
    def is_column_id_for_attribute_column(col_id):
        return re.match(r'^.*?\b(?:attribute)(?:s)?\b\s*?(?:\s*?.*?)?\s*?$', re.sub(r'_', ' ', col_id))
    def is_empty(s):
        if isinstance(s, int) or isinstance(s, float):
            return False
        elif not s:
            return True
        else:
            return False
    column_specs = ctx.column_specs
    rows = ctx.rows
    col_id_name = column_specs.index('name') if 'name' in column_specs else -1
    col_ids_atts = []
    for i, col in enumerate(column_specs):
        if is_column_id_for_attribute_column(col):
            col_ids_atts.append(i)
    is_active = (col_id_name >= 0) and (len(col_ids_atts) > 0)
    if is_active:
        columns = []
        if len(rows) > 0:
            columns = [col for col in rows[0]]
        rows_upd = []
        row_exclusions = col_ids_atts
        for row in rows:
            name_col_updated_parts = []
            check_duplicates = []
            for col_id_att in col_ids_atts:
                col_att_data = row[col_id_att]
                row[col_id_att] = None
                if not is_empty(col_att_data):
                    col_att_data_formatted = col_att_data
                    col_att_data_fingerprint = json.dumps(col_att_data_formatted)
                    col_att_data_is_duplicate = col_att_data_fingerprint in check_duplicates
                    col_att_data_matchingcol = columns[col_id_att]
                    if not col_att_data_is_duplicate:
                        check_duplicates.append(col_att_data_fingerprint)
                    name_col_updated_parts.append({
                        'content': col_att_data_formatted,
                        'fingerprint': col_att_data_fingerprint,
                        'is_duplicate': col_att_data_is_duplicate,
                        'matching_col': col_att_data_matchingcol,
                        'data': col_att_data,
                    })
            name_col_upd_data = {'parts': [row[col_id_name]]}
            name_col_updated_parts_excluding_duplicates = [p for p in name_col_updated_parts if not p['is_duplicate']]
            for def_add in name_col_updated_parts_excluding_duplicates:
                add_col_label = True
                if len(name_col_updated_parts_excluding_duplicates) == 1:
                    add_col_label = False
                if def_add['matching_col'] == def_add['data']:
                    add_col_label = False
                add_parts = []
                add_parts.append({'text': {'text': ', with ', 'role': 'sronly'}, 'role': 'label'})
                if add_col_label:
                    add_parts.append({'text': def_add['matching_col'] + '\n', 'role': 'label'})
                add_parts.append(def_add['content'])
                name_col_upd_data['parts'].append({'role': 'label', 'text': {'role': 'noshowdiff', 'parts': add_parts}})
            row[col_id_name] = name_col_upd_data
            row_filtered = [col for i, col in enumerate(row) if not (i in row_exclusions)]
            rows_upd.append(row_filtered)
        rows = rows_upd
        column_specs = [col for i, col in enumerate(column_specs) if not (i in row_exclusions)]
    ctx.rows = rows
    ctx.column_specs = column_specs
