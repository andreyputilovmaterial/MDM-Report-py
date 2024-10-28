# import os, time, re, sys
from datetime import datetime, timezone
# from dateutil import tz
import argparse
from pathlib import Path
import re
import json
import html

import report_html_template





# helper text prep functions first


def preptext_html(s):
    # basic clean up - basic conversion escaping all tags
    s =  html.escape('{s}'.format(s=s))
    special_pattern = '<<KEYWORD>>'
    special_pattern = html.escape(special_pattern)
    s = s.replace(special_pattern.replace('KEYWORD','ADDED'),'<span class="mdmdiff-inlineoverlay-added">').replace(special_pattern.replace('KEYWORD','REMOVED'),'<span class="mdmdiff-inlineoverlay-removed">').replace(special_pattern.replace('KEYWORD','ENDADDED'),'</span>').replace(special_pattern.replace('KEYWORD','ENDREMOVED'),'</span>')
    # some replacement to add syntax so that dates are formatted
    # if there's some certain markup - that shouln't be escape
    # it should be printed as markup so that js works and converts UTC dates to local time
    s = re.sub(r'&lt;&lt;DATE:(.*?)&gt;&gt;',lambda m:'<span class="mdmreport-role-date" data-role="date">{d}</span>'.format(d=m[1]),s)
    # and one more transformation - some parts
    # (called "scripting" - including MDD syntax for all MDD items and routing syntax)
    # so these parts include raw multi-line text - we'll normalize line breaks
    s = re.sub('([^\t\r\n\x20-\x7E])',lambda m: '&#{n};'.format(n=ord(m[1])),s)
    return s

def preptext_date(s):
    return '<<DATE:{d}>>'.format(d=s)

def preptext_cleanidfield(s):
    return re.sub(r'-+','-',re.sub(r'^-*','',re.sub(r'-*$','',re.sub(r'[^\w\-\.]','-',s))))

def extract_filename(s):
    return re.sub(r'^.*[/\\](.*?)\s*?$',lambda m: m[1],'{sstr}'.format(sstr=s))



def preptext_cellvalue(str_value,col_type='',flags=[]):
    if not str_value:
        return ''
    # is_syntax = not(not(re.match(r'^\s*?script\w*\s*?$',col_type))) or ( (not(not(re.match(r'^\s*?routing\w*\s*?$',section_type)))) and (not(not(re.match(r'^\s*?label\s*?$',col_type)))) )
    is_syntax = 'format_syntax' in flags
    is_structural = isinstance(str_value,dict) or isinstance(str_value,list)
    result = preptext_html(str_value)
    if is_structural:
        # removing css classes for property coloring - reduced memory consumption a lot; AP 10/12/2024
        # unsuppress to have properties colored
        # ins_partbegin = '<span class="mdmreport-prop-fieldname">'
        # ins_partconjunction =  '</span> = "<span class="mdmreport-prop-fieldvalue">'
        # ins_partend = '</span>"'
        ins_partbegin = ''
        ins_partconjunction =  ' = "'
        ins_partend = '"'
        if 'format_semicolon' in flags:
            ins_partbegin = ''
            ins_partconjunction =  ': '
            ins_partend = ''
        result = '{part_begin}{part_iterate}{part_end}'.format(
            part_begin = '<p class="mdmreport-prop-row">',
            part_iterate = ',</p><p class="mdmreport-prop-row">'.join([
                '{ins_partbegin}{fieldname}{ins_partconjunction}{fieldvalue}{ins_partend}'.format(
                    fieldname = preptext_html(row['name']),
                    fieldvalue = preptext_html('{val}'.format(val=row['value']).replace('"','""')),
                    ins_partbegin = ins_partbegin,
                    ins_partconjunction = ins_partconjunction,
                    ins_partend = ins_partend
                ) for row in str_value
            ]),
            part_end = '</p>'
        )
    if is_syntax:
        result = preptext_html(re.sub(r'(?:(?:\r)|(?:\n))+',"\n",str_value))
        result = '<pre>{content}</pre>'.format(content=result)
    return result







# and now, we list "plugins"
# pieces of modules that add certain unnecessary transformations to the report
# to make it more beautiful

# earlier I was doing such transformations in JS - right within page when it loads
# now I decided to bring it to earlier stage, when the file is processed, when it is created, in python
# I thought it is more efficient - final HTML is already prepared and optimized
# but in fact, what these "beautiful" transformations do is that they add more formatting
# which still increases memory usage
# any additional html tag increases memory consumption, especially if it has added styles
# (not necessary inline styles, global styles, but still - it is rendered differently - it takes more memory)



# this fancy "plugin" removes the "attributes" column and adds attributes as grey (<label> tag) to the "name" column
# it looks absolutely perfect aesthetically
# but is increasing memory consumption - report for merged disney BES MDD takes 2 GB in chrome memory witout these "labels" and 3 GB with this transformation performed
# UPD: wow, I reloaded the page and it now takes 1.6 GB of memory; chrome is like unpredictable - it includes that "labels" added to "name" column and the page takes 1.6 GB
def enchancement_plugin__combine_attributes_into_master_name_col__on_col(col_data,col_formatted,col_index=None,flags=[],column_specs=[],other_cols_ref=[]):
    is_active = ( not ('plugin_combine_attributes_already_called' in flags) ) and ( ('name' in column_specs) and ('attributes' in column_specs) )
    if is_active:
        if column_specs[col_index] == 'name':
            # attributes are added to the "name" column
            col_attributes_data = other_cols_ref[column_specs.index('attributes')]
            col_attributes_formatted = '{markup_begin}{contents_attributes_formatted}{markup_end}'.format( markup_begin = '<label><span class="mdmreport-sronly">, with </span>', markup_end = '</label>', contents_attributes_formatted = preptext_cellvalue(col_attributes_data) )
            updated_markup_with_marker_placeholder = prep_htmlmarkup_col('{keep}{add_marker}'.format(keep=col_data,add_marker='{{@}}'),col_index,flags=[]+flags+['plugin_combine_attributes_already_called','skip_plugin_enchancement'],column_specs=column_specs,other_cols_ref=other_cols_ref)
            updated_markup_final = updated_markup_with_marker_placeholder.replace('{{@}}',col_attributes_formatted)
            # return '{part_preserve}{part_add}'.format( part_preserve = col_formatted, part_add = col_attributes_formatted )
            return updated_markup_final
        if column_specs[col_index] == 'attributes':
            # null out - attributes are added to "name" column
            # also, as we null out the whole syntax, including <td> tags - it means we are removing the column completely, and that's what we wanted to achieve! perfect! it is also transformed/removed in the header row, which is perfect
            return ''
        else:
            return col_formatted
    return col_formatted


def enchancement_plugin__add_diff_classes_per_row__on_row(row,result_formatted,flags,column_specs,other_cols_ref=[]):
    is_active = ( not ('plugin_add_diff_classes_per_row_already_called' in flags) ) and ( ('flagdiff' in column_specs) )
    if is_active:
        classes_add = ''
        diffflag = row[column_specs.index('flagdiff')]
        if re.match(r'^.*?(?:(?:add)|(?:insert)).*?',diffflag):
            classes_add = classes_add+ ' mdmdiff-added'
        if re.match(r'^.*?(?:(?:remove)|(?:delete)).*?',diffflag):
            classes_add = classes_add+ ' mdmdiff-removed'
        result_formatted = re.sub(r'(<\s*?tr\b\s*\bclass\s*=\s*"[^"]*?)(")',lambda m:'{begin}{classes_add}{close}'.format(begin=m[1],close=m[2],classes_add=classes_add),result_formatted)
    return result_formatted


enchancement_plugins = [
    {
        'name': 'combine_attributes_into_master_name_col',
        'enabled': True,
        'on_col': enchancement_plugin__combine_attributes_into_master_name_col__on_col,
    },
    {
        'name': 'enchancement_plugin__add_diff_classes_per_row__on_row',
        'enabled': True,
        'on_row': enchancement_plugin__add_diff_classes_per_row__on_row,
    },
]











# and now 2 main function - to prep column markup and row markup - the main things that we have in the report

def prep_htmlmarkup_col(col,col_index,flags=[],column_specs=[],other_cols_ref=[]):
    result_input = col
    result_formatted = '<td class="mdmreport-contentcell{added_css_classes}"{otherattrs}>{col}</td>'.format(
        col = preptext_cellvalue(col,column_specs[col_index],flags),
        added_css_classes = ' mdmreport-col-{colclass}'.format( colclass = preptext_cleanidfield( column_specs[col_index] ) ) if preptext_cleanidfield( column_specs[col_index] ) else '' + ' mdmreport-colindex-{col_index}'.format( col_index = col_index ),
        otherattrs = ' data-columnid="{colid}"'.format(colid=preptext_cleanidfield( column_specs[col_index] ) if preptext_cleanidfield( column_specs[col_index] ) else '') if 'header' in flags else ''
    )
    if not('skip_plugin_enchancement' in flags):
        for plugin in enchancement_plugins:
            if plugin['enabled']:
                if 'on_col' in plugin:
                    result_formatted = plugin['on_col'](result_input,result_formatted,col_index,flags,column_specs,other_cols_ref)
    return result_formatted


def prep_htmlmarkup_row(row,flags=[],column_specs=[]):
    def prep_updated_col_flags(col,col_index,column_specs):
        flags_global = flags
        flags_add = []
        col_type = column_specs[col_index]
        if (not ('header' in flags_global)) and (not(not(re.match(r'^\s*?script\w*\s*?$',col_type))) or ( ('section-routing' in flags_global) and (not(not(re.match(r'^\s*?label',col_type)))) ) ):
            flags_add.append('format_syntax')
        return flags_global + flags_add
    result_formatted = '<tr class="mdmreport-record{added_css_classes}">{columns}</tr>'.format(
        columns = ''.join([ prep_htmlmarkup_col(col,col_index,flags=prep_updated_col_flags(col,col_index,column_specs),column_specs=column_specs,other_cols_ref=row) for col_index,col in enumerate((row or [''])) ]),
        added_css_classes = ' mdmreport-record-header' if 'header' in flags else ''
    )
    if not('skip_plugin_enchancement' in flags):
        for plugin in enchancement_plugins:
            if plugin['enabled']:
                if 'on_row' in plugin:
                    result_formatted = plugin['on_row'](row,result_formatted,flags,column_specs,other_cols_ref=row)
    return result_formatted




# and the main procedure - prepare overall html markup
# that's the meaningful entry point
# that's what this script does - gets input data from json and produces html

def produce_html(inp):

    result_ins_htmlmarkup_title = '???'
    result_ins_htmlmarkup_heading = '???'
    result_ins_htmlmarkup_reporttype = preptext_html(inp['report_type']) if 'report_type' in inp else '???'
    result_ins_htmlmarkup_headertext = '{reporttype} Report'.format(reporttype=result_ins_htmlmarkup_reporttype)
    result_ins_htmlmarkup_banner = ''
    if result_ins_htmlmarkup_reporttype=='MDD':
        result_ins_htmlmarkup_title = 'MDD: {filepath}'.format(filepath=preptext_html(extract_filename(inp['source_file'])))
        result_ins_htmlmarkup_heading = 'MDD: {filepath}'.format(filepath=preptext_html(extract_filename(inp['source_file'])))
        result_ins_htmlmarkup_headertext = '' # it's too obvious, we shouldn't print unnecessary line; it says "MDD" with a very big font size in h1
    elif result_ins_htmlmarkup_reporttype=='diff':
        result_ins_htmlmarkup_title = 'Diff'
        result_ins_htmlmarkup_heading = 'Diff'
    else:
        result_ins_htmlmarkup_title = '???'
        result_ins_htmlmarkup_heading = '???'
    result_ins_htmlmarkup_banner = preptext_cellvalue( []+[{'name':'datetime','value':preptext_date(inp['report_datetime_utc'])}]+inp['source_file_metadata'], flags=['format_semicolon'] )
    


    result_column_headers = ( ( [ '{col}'.format(col=col) for col in inp['report_scheme']['columns'] ] if 'columns' in inp['report_scheme'] else [] ) if 'report_scheme' in inp else [] )
    result_column_headers_text_specs = (inp['report_scheme']['column_headers'] if 'column_headers' in inp['report_scheme'] else {}) if 'report_scheme' in inp else {}

    report_data_sections = []
    for section_obj in ( inp['sections'] if 'sections' in inp else [] ):
        data_add = []
        for row in ( section_obj['content'] if section_obj['content']else [] ):
            row_add = []
            for col in result_column_headers:
                # row_add.append( preptext_cellvalue(row[col],col_type=col,section_type=section_obj['name']) if col in row else '' )
                row_add.append( row[col] if col in row else '' )
            data_add.append(row_add)
        report_data_sections.append({'name':section_obj['name'],'data':data_add})



    report_htmlmarkup_column_headers = ''.join( [ prep_htmlmarkup_row(row,flags=['header'],column_specs=result_column_headers) for row in [[(result_column_headers_text_specs[col_title] if col_title in result_column_headers_text_specs else col_title) for col_title in result_column_headers]] ] )

    report_htmlmarkup_mainpart_with_tables = ''.join([
        '{table_begin}{table_header_row}{table_contents}{table_end}'.format(
            table_begin = report_html_template.TEMPLATE_HTML_TABLE_BEGIN.replace('{{TABLE_NAME}}',preptext_html(section_data['name'])).replace('{{TABLE_ID}}',preptext_cleanidfield(section_data['name'])),
            table_header_row = report_htmlmarkup_column_headers,
            table_contents = ''.join( [ prep_htmlmarkup_row(row,column_specs=result_column_headers,flags=['section-{sec_id}'.format(sec_id=preptext_cleanidfield(section_data['name']))]) for row in section_data['data'] ] ),
            table_end = report_html_template.TEMPLATE_HTML_TABLE_END
        ) for section_data in report_data_sections
    ])

    result_template = '{begin}{report_contents}{end}'.format(
        begin = report_html_template.TEMPLATE_HTML_BEGIN,
        report_contents = report_htmlmarkup_mainpart_with_tables,
        end = report_html_template.TEMPLATE_HTML_END
    )



    # result = result_template.format(
    #     ...
    # )
    ## unfortunately, I won't use format(), as the text includes css formatting with curly brackets - escaping it nnn times is not looking fine
    result = result_template.replace(
        '{{INS_TITLE}}', result_ins_htmlmarkup_title
    ).replace(
        '{{INS_PAGEHEADER}}', result_ins_htmlmarkup_headertext
    ).replace(
        '{{INS_REPORTTYPE}}', preptext_cleanidfield(result_ins_htmlmarkup_reporttype)
    ).replace(
        '{{INS_HEADING}}', result_ins_htmlmarkup_heading
    ).replace(
        '{{INS_BANNER}}', result_ins_htmlmarkup_banner
    )

    return result






if __name__ == '__main__':
    time_start = datetime.now()
    parser = argparse.ArgumentParser(
        description="Produce a summary of MDD in html (read from json)"
    )
    parser.add_argument(
        'inpfile',
        help='JSON with Input MDD map'
    )
    args = parser.parse_args()
    input_map_filename = None
    if args.inpfile:
        input_map_filename = Path(args.inpfile)
        input_map_filename = '{input_map_filename}'.format(input_map_filename=input_map_filename.resolve())
    # input_map_filename_specs = open(input_map_filename_specs_name, encoding="utf8")

    print('MDM report script: script started at {dt}'.format(dt=time_start))

    mdd_map_in_json = None
    with open(input_map_filename, encoding="utf8") as input_map_file:
        mdd_map_in_json = json.load(input_map_file)

    result = produce_html(mdd_map_in_json)
    
    result_fname = ( Path(input_map_filename).parents[0] / '{basename}{ext}'.format(basename=Path(input_map_filename).name,ext='.html') if Path(input_map_filename).is_file() else re.sub(r'^\s*?(.*?)\s*?$',lambda m: '{base}{added}'.format(base=m[1],added='.html'),'{path}'.format(path=input_map_filename)) )
    print('MDM report script: saving as "{fname}"'.format(fname=result_fname))
    with open(result_fname, "w") as outfile:
        outfile.write(result)

    time_finish = datetime.now()
    print('MDM report script: finished at {dt} (elapsed {duration})'.format(dt=time_finish,duration=time_finish-time_start))

