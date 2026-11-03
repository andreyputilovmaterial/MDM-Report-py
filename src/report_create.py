# import os, time, re, sys
from datetime import datetime, timezone
# from dateutil import tz
import argparse
from pathlib import Path
import re
import json
import traceback, sys


# STDOUT_COLOR_RED = "\033[91m"
STDOUT_COLOR_RED = "\033[31m"
STDOUT_COLOR_RESET = "\033[0m"
STDOUT_COLOR_GREEN = "\033[32m"





def is_in_pinliner():
    for p in sys.meta_path:
        try:
            cls_str = f'{(p.__class__)}'
            if re.match(r'.*\.InlinerImporter\b.*',cls_str):
                return True
        except:
            pass
    return False



should_prefer_src_template_import = not is_in_pinliner()
did_import_template = False




if should_prefer_src_template_import:
    try:
        if __name__ == '__main__':
            # run as a program
            import report_html_template
            did_import_template = True
        elif '.' in __name__:
            # package
            from . import report_html_template
            did_import_template = True
        else:
            # included with no parent package
            import report_html_template
            did_import_template = True
    except ImportError:
        did_import_template = False
        pass


if not did_import_template:
    if __name__ == '__main__':
        # run as a program
        from GENERATED import TEMPLATE as report_html_template
        did_import_template = True
    elif '.' in __name__:
        # package
        from .GENERATED import TEMPLATE as report_html_template
        did_import_template = True
    else:
        # included with no parent package
        from GENERATED import TEMPLATE as report_html_template
        did_import_template = True



if __name__ == '__main__':
    # run as a program
    from GENERATED._VERSION import _VERSION as script_version
elif '.' in __name__:
    # package
    from .GENERATED._VERSION import _VERSION as script_version
else:
    # included with no parent package
    from GENERATED._VERSION import _VERSION as script_version






# sanitization / formatting helpers, extracted into common_functions
try:
    from . import common_functions
except ImportError:
    import common_functions

# re-export helper names so existing call sites stay unchanged
for _name in (
    'is_property_list', 'sanitize_text_normalizelinebreaks', 'html_sanitize_text',
    'html_sanitize_htmlattribute', 'html_sanitize_text_date', 'sanitize_idfield',
    'sanitize_cssfield', 'sanitize_text_extract_filename', 'html_sanitize_value_astext',
    'html_sanitize_value_asproperties', 'html_sanitize_value_general',
    'htmlattr_sanitize_value_general', 'html_sanitize_tablecellcontents',
    'sanitize_text_general',
):
    globals()[_name] = getattr(common_functions, _name)



# backend enhancement plugins, extracted into plugins/
try:
    from .plugins import (
        enhancement_plugins,
        run_plugins,
        PluginContext,
        HOOK_TABLE_BEFORE,
        HOOK_ROW_BEFORE,
        HOOK_COL_BEFORE,
        HOOK_COL_AFTER,
        HOOK_ROW_AFTER,
        HOOK_TABLE_AFTER,
    )
except ImportError:
    from plugins import (
        enhancement_plugins,
        run_plugins,
        PluginContext,
        HOOK_TABLE_BEFORE,
        HOOK_ROW_BEFORE,
        HOOK_COL_BEFORE,
        HOOK_COL_AFTER,
        HOOK_ROW_AFTER,
        HOOK_TABLE_AFTER,
    )

# and now 2 main function - to prep column markup and row markup - the main things that we have in the report

def prep_htmlmarkup_col(col,col_index,flags=[],column_specs=[],other_cols_ref=[]):
    
    try:

        ctx = PluginContext(flags=flags, column_specs=column_specs, col=col, col_index=col_index, other_cols_ref=other_cols_ref)
        run_plugins(enhancement_plugins, HOOK_COL_BEFORE, ctx)
        col = ctx.col
        flags = ctx.flags
        
        col_css_classes = ['mdmreport-contentcell']
        if sanitize_cssfield( column_specs[col_index] ):
            col_css_classes.append('mdmreport-col-{colclass}'.format(colclass=sanitize_cssfield( column_specs[col_index] )))
        if col_index>=0:
            col_css_classes.append('mdmreport-colindex-{col_index}'.format(col_index=col_index))
        for flag in [flag for flag in flags if re.match(r'^\s*?format-cssclass-\w',flag)]:
            cssclassname = re.sub(r'^\s*?format-cssclass-(\w[\w\-.]*).*?$',lambda m: m[1],flag)
            col_css_classes.append(cssclassname)

        result_formatted = '<td class="{added_css_classes}"{otherattrs}>{col}</td>'.format(
            col = html_sanitize_tablecellcontents(col,flags),
            added_css_classes = ' '.join(col_css_classes),
            otherattrs = ' data-columnid="{colid}"'.format(colid=sanitize_cssfield( column_specs[col_index] ) if sanitize_cssfield( column_specs[col_index] ) else '') if 'header' in flags else ''
        )

        ctx.result_formatted = result_formatted
        run_plugins(enhancement_plugins, HOOK_COL_AFTER, ctx)
        result_formatted = ctx.result_formatted

        return result_formatted
    
    except Exception as e:
        err_ins = '<row>'
        try:
            err_ins = f'{col}'
            # err_ins = '{c}'.format(c='\t'.join(col))
        except:
            pass
        if len(err_ins)>64:
            err_ins = err_ins[:63]+'...'
        print(f'html markup: failed when processing column {err_ins}')
        raise e


def prep_htmlmarkup_row(row,flags=[],column_specs=[]):

    try:
        
        def prep_updated_col_flags(col,col_index,column_specs):
            flags_global = flags
            flags_add = []
            col_type = column_specs[col_index]
            if (not ('header' in flags_global)) and (not(not(re.match(r'^\s*?script\w*\s*?$',col_type))) or not(not(re.match(r'^\s*?rawtext\w*\s*?$',col_type))) or ( ('section-routing' in flags_global) and (not(not(re.match(r'^\s*?label',col_type)))) ) ):
                flags_add.append('format_syntax')
            return flags_global + flags_add
        
        if len(row)>len(column_specs):
            raise Exception('producing html markup for the row: number of items in a row is bigger than number of columns, we can\'t handle it')

        ctx = PluginContext(flags=flags, column_specs=column_specs, row=row, other_cols_ref=row)
        run_plugins(enhancement_plugins, HOOK_ROW_BEFORE, ctx)
        row = ctx.row
        flags = ctx.flags
        
        col_css_classes = ['mdmreport-record']
        if 'row-header' in flags:
            col_css_classes.append('mdmreport-record-header')
        for flag in [flag for flag in flags if re.match(r'^\s*?format-cssclass-\w',flag)]:
            cssclassname = re.sub(r'^\s*?format-cssclass-(\w[\w\-.]*).*?$',lambda m: m[1],flag)
            col_css_classes.append(cssclassname)

        result_formatted = '<tr class="{added_css_classes}">{columns}</tr>'.format(
            columns = ''.join([ prep_htmlmarkup_col(col,col_index,flags=prep_updated_col_flags(col,col_index,column_specs),column_specs=column_specs,other_cols_ref=row) for col_index,col in enumerate((row or [''])) ]),
            added_css_classes = ' '.join(col_css_classes)
        )
        
        ctx.result_formatted = result_formatted
        run_plugins(enhancement_plugins, HOOK_ROW_AFTER, ctx)
        result_formatted = ctx.result_formatted
        
        return result_formatted
    
    except Exception as e:
        err_ins = '<row>'
        try:
            err_ins = f'{row}'
            err_ins = '{c}'.format(c='\t'.join(row))
        except:
            pass
        if len(err_ins)>64:
            err_ins = err_ins[:63]+'...'
        print(f'html markup: failed when processing row {err_ins}')
        raise e

def prep_htmlmarkup_section(section_obj,column_specs_global,column_titles,flags=[]):

    try:

        column_specs = section_obj['columns'] if 'columns' in section_obj else column_specs_global

        if 'column_headers' in section_obj:
            column_titles = { **column_titles, **section_obj['column_headers'] }

        section_data = section_obj['data']
        row_first = [
            [ (column_titles[col] if col in column_titles else col ) for col in column_specs ]
        ]
        rows = row_first + section_data

        column_specs_localcopy = column_specs

        table_name = section_obj['title']

        table_id = section_obj['id']

        ins_banner = ''
        if 'statistics' in section_obj:
                ins_banner = '<div class="mdmreport-banner mdmreport-banner-table-details mdmreport-banner-table-details-statistics"><p>Statistics: </p>{body}</div>'.format( body = html_sanitize_tablecellcontents( section_obj['statistics'], flags=['format_semicolon'] ) )

        ctx = PluginContext(flags=flags, column_specs=column_specs_localcopy, rows=rows)
        run_plugins(enhancement_plugins, HOOK_TABLE_BEFORE, ctx)
        rows = ctx.rows
        column_specs_localcopy = ctx.column_specs
        flags = ctx.flags
        
        result_formatted = '{table_begin}{table_contents}{table_end}'.format(
            table_begin = report_html_template.TEMPLATE_HTML_TABLE_BEGIN.replace('{{TABLE_NAME}}',html_sanitize_tablecellcontents(table_name)).replace('{{TABLE_ID}}',sanitize_cssfield(table_id)).replace('{{INS_TABBANNER}}',ins_banner),
            table_contents = ''.join( [ prep_htmlmarkup_row(row,column_specs=column_specs_localcopy,flags=[]+flags+(['row-header'] if i==0 else [])+['section-{sec_id}'.format(sec_id=sanitize_cssfield(section_obj['name']))]) for i,row in enumerate(rows) ] ),
            table_end = report_html_template.TEMPLATE_HTML_TABLE_END
        )

        ctx.table_id = table_id
        ctx.result_formatted = result_formatted
        run_plugins(enhancement_plugins, HOOK_TABLE_AFTER, ctx)
        result_formatted = ctx.result_formatted
        
        return result_formatted
    
    except Exception as e:
        print('html markup: failed when processing section {c}'.format(c=section_obj['name']))
        raise e




# and the main procedure - prepare overall html markup
# that's the meaningful entry point
# that's what this script does - gets input data from json and produces html

def produce_html(inp,config={}):

    config = {**(config or {})}
    script_version = (config.get('script_version') or '').strip() or '?'

    result_ins_htmlmarkup_title = '???'
    result_ins_htmlmarkup_heading = '???'
    result_ins_htmlmarkup_reporttype = html_sanitize_text(inp['report_type']) if 'report_type' in inp else '???'
    result_ins_htmlmarkup_headertext = '{reporttype} Report'.format(reporttype=result_ins_htmlmarkup_reporttype)
    result_ins_htmlmarkup_banner = ''
    if result_ins_htmlmarkup_reporttype=='MDD':
        result_ins_htmlmarkup_title = 'MDD: {filepath}'.format(filepath=html_sanitize_text(sanitize_text_extract_filename(inp['source_file'])))
        result_ins_htmlmarkup_heading = 'MDD: {filepath}'.format(filepath=html_sanitize_text(sanitize_text_extract_filename(inp['source_file'])))
        result_ins_htmlmarkup_headertext = '' # it's too obvious, we shouldn't print unnecessary line; it says "MDD" with a very big font size in h1
    elif result_ins_htmlmarkup_reporttype=='diff':
        result_ins_htmlmarkup_title = 'Diff: {MDD_A} vs {MDD_B}'.format(MDD_A=html_sanitize_text(sanitize_text_extract_filename(inp['source_left'])),MDD_B=html_sanitize_text(sanitize_text_extract_filename(inp['source_right'])))
        result_ins_htmlmarkup_heading = 'Diff'
    else:
        if( result_ins_htmlmarkup_reporttype and (len(result_ins_htmlmarkup_reporttype)>0) and not (result_ins_htmlmarkup_reporttype=='???') ):
            result_ins_htmlmarkup_title = '{report_desc}: {filepath}'.format(filepath=html_sanitize_text(sanitize_text_extract_filename(inp['source_file'])),report_desc=result_ins_htmlmarkup_reporttype)
            result_ins_htmlmarkup_heading = '{report_desc}: {filepath}'.format(filepath=html_sanitize_text(sanitize_text_extract_filename(inp['source_file'])),report_desc=result_ins_htmlmarkup_reporttype)
        elif len([flag for flag in ( (inp['report_scheme']['flags'] if 'flags' in inp['report_scheme'] else []) if 'report_scheme' in inp else []) if re.match(r'^\s*?data-type\s*?:',flag)])>0:
            flags_indicating_data_type = [flag for flag in ( (inp['report_scheme']['flags'] if 'flags' in inp['report_scheme'] else []) if 'report_scheme' in inp else []) if re.match(r'^\s*?data-type\s*?:',flag)]
            data_type_str = '/'.join([re.sub(r'^\s*?data-type\s*?:\s*?(.*?)\s*?$',lambda m: m[1],flag) for flag in flags_indicating_data_type])
            result_ins_htmlmarkup_title = '{report_desc}: {filepath}'.format(filepath=html_sanitize_text(sanitize_text_extract_filename(inp['source_file'])),report_desc=data_type_str)
            result_ins_htmlmarkup_heading = '{report_desc}: {filepath}'.format(filepath=html_sanitize_text(sanitize_text_extract_filename(inp['source_file'])),report_desc=data_type_str)
        else:
            result_ins_htmlmarkup_title = '{report_desc}: {filepath}'.format(filepath=html_sanitize_text(sanitize_text_extract_filename(inp['source_file'])),report_desc='File')
            result_ins_htmlmarkup_heading = '{report_desc}: {filepath}'.format(filepath=html_sanitize_text(sanitize_text_extract_filename(inp['source_file'])),report_desc='File')
    result_ins_htmlmarkup_banner = html_sanitize_tablecellcontents( []+[{'name':'datetime','value':html_sanitize_text_date(inp['report_datetime_utc'])}]+inp['source_file_metadata'], flags=['format_semicolon'] )

    result_ins_cssclasses = [
        f'mdmreportpage-type-{sanitize_cssfield(result_ins_htmlmarkup_reporttype)}',
    ]
    inp_data_flags = [f'{f}' for f in inp.get('report_scheme',{}).get('flags',[])]
    result_ins_cssclasses += [ f'mdmreport-inpdataflag-{sanitize_cssfield(flag)}' for flag in inp_data_flags ]
    if len([flag for flag in inp_data_flags if re.match(r'^\s*?diff_source_\w+:.*data-type:diff\s*?$',flag)])>0:
        result_ins_cssclasses += [ 'mdmdiff-in-diff' ]


    result_column_headers_global = ( ( [ '{col}'.format(col=col) for col in inp['report_scheme']['columns'] ] if 'columns' in inp['report_scheme'] else [] ) if 'report_scheme' in inp else [] )
    result_column_headers_global_text_specs = (inp['report_scheme']['column_headers'] if 'column_headers' in inp['report_scheme'] else {}) if 'report_scheme' in inp else {}
    for col in result_column_headers_global:
        if not col in result_column_headers_global_text_specs:
            result_column_headers_global_text_specs[col] = col

    flags = []
    reporttype = html_sanitize_text(inp['report_type']) if 'report_type' in inp else None
    if reporttype in ['MDD','diff']:
        flags += [f'reporttype-{reporttype}'] # older format sent in flags, for generating css classes in <body>
    flags += [ f':reporttype:{reporttype}' ] # newer format sent in flags, should be like something universal
    flags += [ f':scriptversion:{script_version}' ]
    flags += [ f':inp-data:{flag}' for flag in inp_data_flags ]
    flags += [ f':disable-plugin:{name}' for name in (config.get('plugins_to_disable') or []) ]
    report_data_sections = []
    section_ids_used = []
    for section_obj in ( inp['sections'] if 'sections' in inp else [] ):
        data_add = []
        result_column_headers = [ '{col}'.format(col=col) for col in section_obj['columns'] ] if 'columns' in section_obj else result_column_headers_global
        for row in ( section_obj['content'] if section_obj['content']else [] ):
            row_add = []
            for col in result_column_headers:
                row_add.append( row[col] if col in row else '' )
            data_add.append(row_add)
        
        section_title = section_obj['name']
        if 'title' in section_obj:
            section_title = section_obj['title']
        
        section_id = section_obj['name']
        section_id = re.sub(r'([^a-zA-Z])',lambda m: '_x{d}_'.format(d=ord(m[1])),section_id,flags=re.I)
        while True:
            if not (section_id in section_ids_used):
                section_ids_used.append(section_id)
                break
            else:
                section_id = section_id+ '_' + str(section_ids_used.index(section_id)+2)

        section = {
            **section_obj,
            'content': None,
            'name': section_obj['name'],
            'title': section_title,
            'id': section_id,
            # 'statistics': section_obj['statistics'],
            'data': data_add
        }
        report_data_sections.append(section)



    report_htmlmarkup_mainpart_with_tables = ''.join([
        prep_htmlmarkup_section(section_data,result_column_headers_global,result_column_headers_global_text_specs,flags) for section_data in report_data_sections
    ])

    result_template = '{begin}{report_contents}{end}'.format(
        begin = report_html_template.TEMPLATE_HTML_BEGIN,
        report_contents = '{{INS_MAIN_PART}}',
        end = report_html_template.TEMPLATE_HTML_END
    )



    # result = result_template.format(
    #     ...
    # )
    ## unfortunately, I won't use format(), as the text includes css formatting with curly brackets - escaping it nnn times is not looking fine
    # also, previously I had result.replace().replace().replace().replace()... all in one line - it was causing memory issues; now I have these steps on separate lines
    result = result_template
    result = result.replace(
        '{{INS_TITLE}}', result_ins_htmlmarkup_title
    )
    result = result.replace(
        '{{INS_PAGEHEADER}}', result_ins_htmlmarkup_headertext
    )
    result = result.replace(
        '{{INS_REPORTTYPE}}', sanitize_cssfield(result_ins_htmlmarkup_reporttype)
    )
    result = result.replace(
        '{{INS_SCRIPTVERSION}}', sanitize_cssfield(script_version) or '?'
    )
    # <span class="mdmreport-role-date" data-role="date">2026-05-27T22:37:56Z</span>
    result = result.replace(
        '{{NOW}}', html_sanitize_value_general(f"{datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",flags=['role-date'])
    )
    result = result.replace(
        '{{INS_ADDEDCLASSES}}', ' ' + ' '.join([ sanitize_cssfield(s) for s in result_ins_cssclasses])
    )
    result = result.replace(
        '{{INS_HEADING}}', result_ins_htmlmarkup_heading
    )
    result = result.replace(
        '{{INS_BANNER}}', result_ins_htmlmarkup_banner
    )
    # result = result.replace(
    #     '{{INS_MAIN_PART}}', report_htmlmarkup_mainpart_with_tables
    # )
    # more memory efficient than text replacements
    prefix_replacement = '{{INS_MAIN_PART}}'
    prefix_end = result.index(prefix_replacement)
    postfix_begin = prefix_end + len(prefix_replacement)
    result = result[:prefix_end] + report_htmlmarkup_mainpart_with_tables + result[postfix_begin:]

    return result





def entry_point(*argcs,**kwargs):
    try:
        time_start = datetime.now()
        script_name = 'mdmtoolsap html report script'

        parser = argparse.ArgumentParser(
            description="Produce a summary of input file in html (read from json)",
            prog='mdmtoolsap --program report'
        )
        parser.add_argument(
            '--inpfile',
            help='JSON with file data',
            type=str,
            required=True
        )
        parser.add_argument(
            '--output-format',
            help='Set output format: html or excel',
            type=str,
            required=False
        )
        parser.add_argument(
            '--output-filename',
            help='Set preferred output file name, with path',
            type=str,
            required=False
        )
        parser.add_argument(
            '--disable-plugin',
            help='Disable certain functionality',
            action='append',
            default=[],
            choices=[s.get('name') for s in enhancement_plugins],
            required=False
        )

        # args = None
        # args_rest = None
        # if( ('arglist_strict' in config) and (not config['arglist_strict']) ):
        #     args, args_rest = parser.parse_known_args()
        # else:
        args = parser.parse_args(*argcs,**kwargs)
        input_map_filename = None
        if args.inpfile:
            input_map_filename = Path(args.inpfile)
            # input_map_filename = '{input_map_filename}'.format(input_map_filename=input_map_filename.resolve())
        # input_map_filename_specs = open(input_map_filename_specs_name, encoding="utf8")
        config_output_format = 'html'
        if args.output_format:
            config_output_format = args.output_format

        print(f'{script_name}: script started at {time_start}')

        #print(f'{script_name}: reading {input_map_filename}')
        if not(Path(input_map_filename).is_file()):
            raise FileNotFoundError('file not found: {fname}'.format(fname=input_map_filename))
        
        inpfile_map_in_json = None
        with open(input_map_filename, encoding="utf8") as input_map_file:
            try:
                inpfile_map_in_json = json.load(input_map_file)
            except json.JSONDecodeError as e:
                # just a more descriptive message to the end user
                # can happen if the tool is started two times in parallel and it is writing to the same json simultaneously
                raise TypeError('Diff: Can\'t read input file as JSON: {msg}'.format(msg=e))
        
        config = {
            'script_name': script_name,
            'script_version': script_version.strip(),
            'script_started': time_start,
            'output_format': config_output_format,
            'inp_filename': f'{input_map_filename}',
            'plugins_to_disable': [plugin_name for plugin_name in (args.disable_plugin or [])],
        }
        
        assert all(s in [s.get('name') for s in enhancement_plugins] for s in config.get('plugins_to_disable')), f'--disable-plugin option is wrong: an entry is not a plugin name'

        result = None
        if config_output_format=='html':
            result = produce_html(inpfile_map_in_json,config)
        else:
            raise ValueError('report.py: unsupported output format: {fmt}'.format(fmt=config_output_format))
        
        if args.output_filename:
            result_fname = Path(args.output_filename)
        else:
            result_fname = ( Path(input_map_filename).parents[0] / '{basename}{ext}'.format(basename=re.sub(r'\.json\s*?$','','{n}'.format(n=Path(input_map_filename).name),flags=re.I),ext='.html') if Path(input_map_filename).is_file() else re.sub(r'^\s*?(.*?)(?:\.json)?\s*?$',lambda m: '{base}{added}'.format(base=m[1],added='.html'),'{path}'.format(path=input_map_filename)) )
        print(f'{script_name}: saving as {STDOUT_COLOR_GREEN}"{result_fname}"{STDOUT_COLOR_RESET}')
        with open(result_fname, "w") as outfile:
            outfile.write(result)

        time_finish = datetime.now()
        print(f'{script_name}: finished at {time_finish} (elapsed {time_finish-time_start})')
    except Exception as e:
        # the program is designed to be user-friendly
        # that's why we reformat error messages a little bit
        # stack trace is still printed (I even made it longer to 20 steps!)
        # but the error message itself is separated and printed as the last message again

        # for example, I don't write "print('File Not Found!');exit(1);", I just write "raise FileNotFoundErro()"
        print('',file=sys.stderr)
        print('Stack trace:',file=sys.stderr)
        print('',file=sys.stderr)
        traceback.print_exception(e,limit=20)
        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print('',file=sys.stderr)
        print(f'{STDOUT_COLOR_RED}Error:{STDOUT_COLOR_RESET}',file=sys.stderr)
        print('',file=sys.stderr)
        print(f'{STDOUT_COLOR_RED}{e}{STDOUT_COLOR_RESET}',file=sys.stderr)
        print('',file=sys.stderr)
        exit(1)


if __name__ == '__main__':
    entry_point()
