# import os, time, re, sys
from datetime import datetime, timezone
# from dateutil import tz
import argparse
from pathlib import Path
import re
import json
import html

import report_html_template




# TODO:
import pdb



def preptext_html(s):
    s =  html.escape('{s}'.format(s=s))
    s = re.sub(r'&lt;&lt;DATE:(.*?)&gt;&gt;',lambda m:'<span class="mdmreport-role-date" data-role="date">{d}</span>'.format(d=m[1]),s)
    s = re.sub('([^\t\r\n\x20-\x7E])',lambda m: '&#{n};'.format(n=ord(m[1])),s)
    return s

def preptext_date(s):
    return '<<DATE:{d}>>'.format(d=s)

def preptext_cleanidfield(s):
    return re.sub(r'-+','-',re.sub(r'^-*','',re.sub(r'-*$','',re.sub(r'[^\w\-\.]','-',s))))

def extract_filename(s):
    return re.sub(r'^.*[/\\](.*?)\s*?$',lambda m: m[1],'{sstr}'.format(sstr=s))



def preptext_cellvalue(s,col_type,section_type):
    if s is None:
        return ''
    is_syntax = not(not(re.match(r'^\s*?script\w*\s*?$',col_type))) or ( (not(not(re.match(r'^\s*?routing\w*\s*?$',section_type)))) and (not(not(re.match(r'^\s*?label\s*?$',col_type)))) )
    is_structural = isinstance(s,dict) or isinstance(s,list)
    result = preptext_html(s)
    if is_structural:
        result = ''
        # result = '<p class="mdmreport-prop-row">' + ',</p><p class="mdmreport-prop-row">'.join([ '<span class="mdmreport-prop-fieldname">{field}</span> = "<span class="mdmreport-prop-fieldvalue">{value}</span>"'.format(field=preptext_html(row['name']),value=preptext_html('{s}'.format(s=row['value']).replace('"','""'))) for row in s  ]) + '</p>'
        # removing css classes for property coloring - reduced memory consumption a lot; AP 10/12/2024
        result = '<p class="mdmreport-prop-row">' + ',</p><p class="mdmreport-prop-row">'.join([ '{field} = "{value}"'.format(field=preptext_html(row['name']),value=preptext_html('{s}'.format(s=row['value']).replace('"','""'))) for row in s  ]) + '</p>'
    if is_syntax:
        result = preptext_html(re.sub(r'(?:(?:\r)|(?:\n))+',"\n",s))
        result = '<pre>{content}</pre>'.format(content=result)
    return result








def produce_html(inp):

    result_ins_title = '???'
    result_ins_heading = '???'
    result_ins_reporttype = preptext_html(inp['report_type']) if 'report_type' in inp else '???'
    result_ins_banner = ''
    if result_ins_reporttype=='MDD':
        result_ins_title = 'MDD: {filepath}'.format(filepath=preptext_html(extract_filename(inp['source_file'])))
        result_ins_heading = 'MDD: {filepath}'.format(filepath=preptext_html(extract_filename(inp['source_file'])))
    elif result_ins_reporttype=='diff':
        result_ins_title = 'MDD Diff: ... (TBD)'
        result_ins_heading = 'MDD Diff: ... (TBD)'
    else:
        result_ins_title = '???'
        result_ins_heading = '???'
    result_ins_banner = ''.join( [ '<p>{content}</p>'.format(content=preptext_html('{propname}: {propvalue}'.format(propname=content['name'],propvalue=content['value']))) for content in []+[{'name':'datetime','value':preptext_date(inp['report_datetime_utc'])}]+inp['source_file_metadata'] ] )
    


    report_column_headers = ( ( [ '{col}'.format(col=preptext_html(col)) for col in inp['report_scheme']['columns'] ] if 'columns' in inp['report_scheme'] else [] ) if 'report_scheme' in inp else [] )

    report_data_sections = []
    for section_obj in ( inp['sections'] if 'sections' in inp else [] ):
        data_add = []
        for row in section_obj['content']:
            row_add = []
            for col in report_column_headers:
                row_add.append( preptext_cellvalue(row[col],col_type=col,section_type=section_obj['name']) if col in row else '' )
            data_add.append(row_add)
        report_data_sections.append({'name':section_obj['name'],'data':data_add})



    report_contents_headerrow = ''.join( [ '<tr class="mdmreport-record mdmreport-record-header">{columns}</tr>'.format(
        columns = ''.join(['<td class="mdmreport-contentcell mdmreport-col-{colclass} mdmreport-colindex-{coindex}">{col}</td>'.format(col=col,colclass=preptext_cleanidfield(report_column_headers[col_index]),coindex=col_index) for col_index,col in enumerate((row or ['']))])
    ) for row in [report_column_headers] ] )

    report_contents_formatted = ''.join([
        '{table_begin}{table_header_row}{table_contents}{table_end}'.format(
            table_begin = report_html_template.TEMPLATE_HTML_TABLE_BEGIN.replace('{{TABLE_NAME}}',preptext_html(section_data['name'])).replace('{{TABLE_ID}}',preptext_cleanidfield(section_data['name'])),
            table_header_row = report_contents_headerrow,
            table_contents = ''.join( [ '<tr class="mdmreport-record">{columns}</tr>'.format(
                columns = ''.join(['<td class="mdmreport-contentcell mdmreport-col-{colclass} mdmreport-colindex-{coindex}">{col}</td>'.format(col=col,colclass=preptext_cleanidfield(report_column_headers[col_index]),coindex=col_index) for col_index,col in enumerate((row or ['']))])
            ) for row in section_data['data'] ] ),
            table_end = report_html_template.TEMPLATE_HTML_TABLE_END
        ) for section_data in report_data_sections
    ])

    result_template = '{begin}{report_contents}{end}'.format(
        begin = report_html_template.TEMPLATE_HTML_BEGIN,
        report_contents = report_contents_formatted,
        end = report_html_template.TEMPLATE_HTML_END
    )



    # result = result_template.format(
    #     INS_TITLE = 'MDD: {MDD}'.format(MDD=preptext_html(inp['MDD'])),
    #     INS_REPORTTYPE = 'MDD',
    #     INS_HEADING = 'MDD: {MDD}'.format(MDD=preptext_html(inp['MDD'])),
    #     INS_BANNER = '???', # ''.join( [ '<p>{content}</p>'.format(content=preptext_html(content)) for content in fields_File_ReportInfo ] )
    # )
    ## unfortunately, I won't use format(), as the text includes css formatting with curly brackets - escaping it nnn times is not looking fine
    result = result_template.replace(
        '{{INS_TITLE}}', result_ins_title
    ).replace(
        '{{INS_REPORTTYPE}}', preptext_cleanidfield(result_ins_reporttype)
    ).replace(
        '{{INS_HEADING}}', result_ins_heading
    ).replace(
        '{{INS_BANNER}}', result_ins_banner
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

