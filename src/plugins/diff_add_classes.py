# Diff report enhancement: add diff CSS classes to rows and cells.

import re

try:
    from ..common_functions import sanitize_text_general
except ImportError:
    from common_functions import sanitize_text_general


def _did_col_change_deep_inspect(data):
    if isinstance(data, str):
        return False
    elif isinstance(data, list):
        result = False
        for slice in data:
            result = result or _did_col_change_deep_inspect(slice)
        return result
    elif isinstance(data, dict) and 'text' in data:
        if 'role' in data and data['role']:
            if re.match(r'^\s*?(?:role-)?(?:added|removed).*?', f"{data['role']}", flags=re.I):
                return True
        return _did_col_change_deep_inspect(data['text'])
    elif isinstance(data, dict) and 'parts' in data:
        return _did_col_change_deep_inspect(data['parts'])
    elif isinstance(data, dict) and 'name' in data and 'value' in data:
        return _did_col_change_deep_inspect(data['value'])
    else:
        return _did_col_change_deep_inspect('{f}'.format(f=data))


def diff_add_classes_on_row_before(ctx):
    flags = ctx.flags
    column_specs = ctx.column_specs
    row = ctx.row
    other_cols_ref = ctx.other_cols_ref
    is_active = ('flagdiff' in column_specs)
    flags_added = []
    if is_active:
        is_diff_on_diff = len([flag for flag in flags if re.match(r'^\s*?:inp-data:diff_source_\w+:.*data-type:diff\s*?$', flag)]) > 0
        diffflag = sanitize_text_general(row[column_specs.index('flagdiff')])
        was_row_added = re.match(r'^.*?(?:(?:add)|(?:insert)).*?', diffflag)
        was_row_removed = re.match(r'^.*?(?:(?:remove)|(?:delete)).*?', diffflag)
        did_any_col_change = False
        was_row_moved = re.match(r'^.*?(?:(?:move)).*?', diffflag) and not re.match(r'^.*?(?:(?:remove)).*?', diffflag)
        was_row_movedfromhere = 'moved from' in diffflag
        # TODO: inspecting the whole row, every column, to see if something
        # changed. This can be complicated, as cell contents are not always
        # plain text. Do we really need such inspections?
        for col in other_cols_ref:
            did_any_col_change = did_any_col_change or _did_col_change_deep_inspect(col)
        if was_row_added:
            flags_added.append('format-cssclass-mdmdiff-added')
        if was_row_removed:
            flags_added.append('format-cssclass-mdmdiff-removed')
        if did_any_col_change:
            flags_added.append('format-cssclass-mdmdiff-diff')
        if was_row_moved and not (was_row_added or was_row_removed or did_any_col_change):
            flags_added.append('format-cssclass-mdmdiff-moved')
            flags_added.append('format-cssclass-mdmdiff-ghost')
        if was_row_movedfromhere:
            flags_added.append('format-cssclass-mdmdiff-movedfrom')
    ctx.flags = list(set(ctx.flags + flags_added))


def diff_add_classes_on_col_before(ctx):
    col_data = ctx.col
    col_index = ctx.col_index
    flags = ctx.flags
    column_specs = ctx.column_specs
    other_cols_ref = ctx.other_cols_ref
    is_active = ('flagdiff' in column_specs)
    if is_active:
        is_diff_on_diff = len([flag for flag in flags if re.match(r'^\s*?:inp-data:diff_source_\w+:.*data-type:diff\s*?$', flag)]) > 0
        marker_text_append_diffflag_col = ' (changed)'
        if is_diff_on_diff:
            marker_text_append_diffflag_col = ''
        if column_specs[col_index] == 'flagdiff':
            row = other_cols_ref
            diffflag = sanitize_text_general(row[column_specs.index('flagdiff')])
            was_row_added = re.match(r'^.*?(?:(?:add)|(?:insert)).*?', diffflag)
            was_row_removed = re.match(r'^.*?(?:(?:remove)|(?:delete)).*?', diffflag)
            did_any_col_change = False
            was_row_moved = re.match(r'^.*?(?:(?:move)).*?', diffflag) and not re.match(r'^.*?(?:(?:remove)).*?', diffflag)
            # TODO: inspecting the whole row, every column, to see if something
            # changed. This can be complicated, as cell contents are not always
            # plain text.
            for col in row:
                did_any_col_change = did_any_col_change or _did_col_change_deep_inspect(col)
            if is_diff_on_diff:
                did_row_change = did_any_col_change
            else:
                did_row_change = did_any_col_change or was_row_moved  # changing position is a change too
                did_row_change = was_row_added or was_row_removed or did_row_change
            if did_row_change:
                col_data = {'parts': [col_data, marker_text_append_diffflag_col]}
    ctx.col = col_data
