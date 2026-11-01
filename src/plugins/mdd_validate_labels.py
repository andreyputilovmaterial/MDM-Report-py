# MDD report enhancement: validate label XML and highlight issues.

import re
import sys
import xml.etree.ElementTree as ET

try:
    from ..common_functions import html_sanitize_text
except ImportError:
    from common_functions import html_sanitize_text


STDOUT_COLOR_RED = "\033[31m"
STDOUT_COLOR_RESET = "\033[0m"


def mdd_validate_labels(ctx):
    result_formatted = ctx.result_formatted
    col = ctx.col
    col_index = ctx.col_index
    flags = ctx.flags
    column_specs = ctx.column_specs
    other_cols_ref = ctx.other_cols_ref

    def is_mdd_report_type(flags):
        return 'reporttype-diff' in flags
    def is_label_column(result_formatted, col, col_index, flags, column_specs, other_cols_ref):
        return re.match(r'^\s*(?:label|langcode).*', column_specs[col_index])
    def get_flat_text(html):
        root = ET.fromstring(html)
        return ''.join(root.itertext())
    def is_xml_compatible(snippet: str) -> bool:
        try:
            # Wrap snippet in a dummy root
            ET.fromstring(f"<root>{snippet}</root>")
            return True
        except ET.ParseError as e:
            return False
    try:
        if is_label_column(result_formatted, col, col_index, flags, column_specs, other_cols_ref):
            css_classes_add = []
            css_classes_add += []
            css_classes_add += [] if is_xml_compatible(get_flat_text(result_formatted)) else ['mdmrep-plgn-labelxmlerr']
            css_classes_add = ' '.join(css_classes_add)
            if len(css_classes_add) > 0:
                m = re.match(r'^(\s*?<\s*?(?:td|th)(?:\s*?\w+\s*?=\s*?["\'].*?["\'])*?\s*?>)(.*)(<\s*?/\s*?(?:td|th)\s*?>\s*?)$', result_formatted, flags=re.I)
                if not m:
                    print(f'{STDOUT_COLOR_RED}DEBUG: plugin: mdmrep validate plugin: could not parse <td> markup: {result_formatted}{STDOUT_COLOR_RESET}', file=sys.stderr)
                    raise Exception('mdmrep validate plugin: could not parse <td> markup')
                result_outer_begin = m[1]
                result_inner = m[2]
                result_outer_end = m[3]
                ctx.result_formatted = f'{result_outer_begin}<span class="{css_classes_add}">{result_inner}</span>{result_outer_end}'
            else:
                ctx.result_formatted = result_formatted
        else:
            ctx.result_formatted = result_formatted
    except Exception as e:
        print(f'{STDOUT_COLOR_RED}mdmrep validate labels plugin: failed: {e}{STDOUT_COLOR_RESET}', file=sys.stderr)
        err_msg = 'ERROR'
        try:
            err_msg = f'{e}'
            err_msg = html_sanitize_text(err_msg)
        except:
            err_msg = 'ERROR'
        ctx.result_formatted = f'<span class="mdmreport-plugin-validate-labels-error">{err_msg}</span>{result_formatted}'
