# import os, time, re, sys
from datetime import datetime
# from dateutil import tz
import argparse
from pathlib import Path
import re
import json
import html




if __name__ == '__main__':
    # run as a program
    import report_html_template
elif '.' in __name__:
    # package
    from . import report_html_template
else:
    # included with no parent package
    import report_html_template



# TODO: Excel Provider!!!



# helper text prep functions first


# TODO:
# # Jira - grabbing project number - check that all is working correctly when we exclude mdmproperteis sectiton

# TODO:
# all js code - check that if something is added to an error banner, syntax is always escaped

# TODO: double quotes - not working, not escaped

# TODO: when attributes are comvbined into "name" column we need to remove/suppress blank remaining columns

def sanitize_text_normalizelinebreaks(str_output):
    str_output = re.sub(r'\r','\n',re.sub(r'\r?\n','\n',str_output))
    return str_output

def sanitize_text_html(str_output,flags=[]):
    str_output = sanitize_text_normalizelinebreaks(str_output)
    # basic clean up - basic conversion escaping all tags
    str_output =  html.escape('{str_output}'.format(str_output=str_output))
    special_pattern = '<<KEYWORD>>'
    special_pattern = html.escape(special_pattern)
    # TODO: finding injected markers should be depricated in future versions
    str_output = str_output.replace(special_pattern.replace('KEYWORD','ADDED'),'<span class="mdmdiff-inlineoverlay-added">').replace(special_pattern.replace('KEYWORD','REMOVED'),'<span class="mdmdiff-inlineoverlay-removed">').replace(special_pattern.replace('KEYWORD','ENDADDED'),'</span>').replace(special_pattern.replace('KEYWORD','ENDREMOVED'),'</span>')
    # some replacement to add syntax so that dates are formatted
    # if there'str_output some certain markup - that shouln't be escape
    # it should be printed as markup so that js works and converts UTC dates to local time
    str_output = re.sub(r'&lt;&lt;DATE:(.*?)&gt;&gt;',lambda m:'<span class="mdmreport-role-date" data-role="date">{d}</span>'.format(d=m[1]),str_output)
    # and one more transformation - some parts
    # (called "scripting" - including MDD syntax for all MDD items and routing syntax)
    # so these parts include raw multi-line text - we'll normalize line breaks
    str_output = re.sub('([^\t\r\n\x20-\x7E])',lambda m: '&#{n};'.format(n=ord(m[1])),str_output)
    return str_output

def sanitize_text_date(s):
    #return '<<DATE:{d}>>'.format(d=s)
    return {'parts':[{'text':s,'role':'date'}]}

def sanitize_idfield(s):
    return re.sub(r'-+','-',re.sub(r'^-*','',re.sub(r'-*$','',re.sub(r'[^\w\-\.]','-',s))))

def sanitize_text_extract_filename(s):
    return re.sub(r'^.*[/\\](.*?)\s*?$',lambda m: m[1],'{sstr}'.format(sstr=s))



def sanitize_value_astext(inp_value,col_type='',flags=[]):
    if 'format-escapequotes-vbsstyle' in flags:
        inp_value = inp_value.replace('"','""')
    return sanitize_text_html(inp_value,flags=list(set(flags)-set(['format-escapequotes-vbsstyle'])))

def sanitize_value_asproperties(inp_value,col_type='',flags=[]):
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
                fieldname = sanitize_text_html(row['name']),
                fieldvalue = sanitize_value_general(row['value'],[]+flags+['format-escapequotes-vbsstyle']),
                ins_partbegin = ins_partbegin,
                ins_partconjunction = ins_partconjunction,
                ins_partend = ins_partend
            ) for row in inp_value
        ]),
        part_end = '</p>'
    )
    return result

def sanitize_value_general(inp_value,col_type='',flags=[]):
    # it's recursive!
    for flag in flags:
        if (flag=='role-time') or (flag=='role-date') or (flag=='role-datetime'):
            return '<span class="mdmreport-role-date" data-role="date">{d}</span>'.format(d=sanitize_value_general(inp_value,col_type,flags=list(set(flags)-set([flag]))))
        elif flag=='role-added':
            return '<span class="mdmdiff-inlineoverlay-added">{d}</span>'.format(d=sanitize_value_general(inp_value,col_type,flags=list(set(flags)-set([flag]))))
        elif flag=='role-removed':
            return '<span class="mdmdiff-inlineoverlay-removed">{d}</span>'.format(d=sanitize_value_general(inp_value,col_type,flags=list(set(flags)-set([flag]))))
        elif flag=='role-sronly':
            return '<span class="mdmreport-sronly">{d}</span>'.format(d=sanitize_value_general(inp_value,col_type,flags=list(set(flags)-set([flag]))))
        elif flag=='role-label':
            return '<label>{d}</label>'.format(d=sanitize_value_general(inp_value,col_type,flags=list(set(flags)-set([flag]))))
    result = None
    if not inp_value:
        return ''
    # is_syntax = not(not(re.match(r'^\s*?script\w*\s*?$',col_type))) or ( (not(not(re.match(r'^\s*?routing\w*\s*?$',section_type)))) and (not(not(re.match(r'^\s*?label\s*?$',col_type)))) )
    if isinstance(inp_value,list) and ([(True if 'name' in dict.keys(item) else False) for item in inp_value].count(True)==len(inp_value)):
        result = sanitize_value_asproperties(inp_value,col_type,flags)
    elif isinstance(inp_value,dict) and 'parts' in dict.keys(inp_value):
        result = ''.join( sanitize_value_general(part['text'],col_type,[]+flags+['role-{cssclasspart}'.format(cssclasspart=re.sub(r'^\s*?(?:role-\s*?)?','',part['role']))]) if isinstance(part,dict) and 'text' in dict.keys(part) else sanitize_value_general(part,col_type,flags) for part in inp_value['parts'] )
    elif isinstance(inp_value,dict) and 'text' in dict.keys(inp_value):
        result = sanitize_value_general(inp_value['text'],col_type,flags)
    elif isinstance(inp_value,str):
        result =  sanitize_value_astext(inp_value,col_type,flags)
    elif isinstance(inp_value,dict) or isinstance(inp_value,list):
        result =  sanitize_value_astext(json.dumps(inp_value),col_type,flags)
    elif ('{fmt}'.format(fmt=inp_value)==inp_value):
        result =  sanitize_value_astext(inp_value,col_type,flags)
    else:
        result =  sanitize_value_astext(json.dumps(inp_value),col_type,flags)
    return result

def sanitize_tablecellcontents(inp_value,col_type='',flags=[]):
    result = None
    if not inp_value:
        return ''
    result = sanitize_value_general(inp_value,col_type,[flag for flag in flags if flag!='format_syntax'])
    if 'format_syntax' in flags:
        result = '<pre>{content}</pre>'.format(content=sanitize_text_normalizelinebreaks(result)) # it's already done globally at the first line of sanitize_value_astext which should have been already called
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
def enchancement_plugin__combine_attributes_into_master_name_col__on_col(col_data,col_index=None,flags=[],column_specs=[],other_cols_ref=[]):
    def is_column_id_for_attribute_column(col_id):
        return re.match(r'^.*?\b(?:attribute)(?:s)?\b\s*?(?:\s*?.*?)?\s*?$',re.sub(r'_',' ',col_id))
    is_active = ( not ('plugin_combine_attributes_already_called' in flags) ) and ( ('name' in column_specs) and (len([col for col in column_specs if is_column_id_for_attribute_column(col)])>0) )
    if is_active:
        if column_specs[col_index] == 'name':
            # attributes are added to the "name" column
            result_parts = [col_data]
            result_parts_added_check = [] # to avoid duplicates - if left MDD column and right MDD column are identical we will only print it once
            for col_id_column_add_with_attrs in [col for col in column_specs if is_column_id_for_attribute_column(col)]:
                col_attributes_data = other_cols_ref[column_specs.index(col_id_column_add_with_attrs)]
                if col_attributes_data:
                    col_attributes_data_check = json.dumps(col_attributes_data) # to avoid duplicates - if left MDD column and right MDD column are identical we will only print it once
                    if not (col_attributes_data_check in result_parts_added_check): # to avoid duplicates - if left MDD column and right MDD column are identical we will only print it once
                        result_parts.append({'text':{'parts':[{'text':', with ','role':'sronly'},col_attributes_data]},'role':'label'})
                        result_parts_added_check.append(col_attributes_data_check)
            col_data = {'parts':result_parts}
            return col_data,flags
        if is_column_id_for_attribute_column(column_specs[col_index]):
            # null out - attributes are added to "name" column
            return None,flags
        else:
            return col_data,flags
    return col_data,flags


def enchancement_plugin__add_diff_classes_per_row__on_row(row,flags,column_specs,other_cols_ref=[]):
    is_active = ( not ('plugin_add_diff_classes_per_row_already_called' in flags) ) and ( ('flagdiff' in column_specs) )
    flags_added = []
    if is_active:
        classes_add = ''
        diffflag = row[column_specs.index('flagdiff')]
        was_row_added = re.match(r'^.*?(?:(?:add)|(?:insert)).*?',diffflag)
        was_row_removed = re.match(r'^.*?(?:(?:remove)|(?:delete)).*?',diffflag)
        was_row_changed = False
        was_row_moved = re.match(r'^.*?(?:(?:move)).*?',diffflag) and not re.match(r'^.*?(?:(?:remove)).*?',diffflag)
        # if was_row_moved:
        #     was_row_changed = True
        for col in other_cols_ref:
            col_text = '{c}'.format(c=col)
            if isinstance(col,dict) or isinstance(col,list):
                col_text = json.dumps(col)
            was_row_changed = was_row_changed or re.match(r'.*?(?:(?:<<ADDED>>)|(?:<<REMOVED>>)).*?',col_text,flags=re.DOTALL)
        if was_row_added:
            flags_added.append('format-cssclass-mdmdiff-added')
        if was_row_removed:
            flags_added.append('format-cssclass-mdmdiff-removed')
        if was_row_changed and not ( was_row_added or was_row_removed ):
            flags_added.append('format-cssclass-mdmdiff-diff')
        if was_row_moved and not ( was_row_added or was_row_removed or was_row_changed ):
            flags_added.append('format-cssclass-mdmdiff-moved')
            flags_added.append('format-cssclass-mdmdiff-ghost')
    return row,flags+flags_added

def enchancement_plugin__add_diff_classes_per_row__on_col(col_data,col_index=None,flags=[],column_specs=[],other_cols_ref=[]):
    is_active = ( not ('plugin_add_diff_classes_per_row_already_called' in flags) ) and ( ('flagdiff' in column_specs) )
    if is_active:
        if column_specs[col_index] == 'flagdiff':
            row = other_cols_ref
            diffflag = row[column_specs.index('flagdiff')]
            was_row_added = re.match(r'^.*?(?:(?:add)|(?:insert)).*?',diffflag)
            was_row_removed = re.match(r'^.*?(?:(?:remove)|(?:delete)).*?',diffflag)
            was_row_changed = False
            was_row_moved = re.match(r'^.*?(?:(?:move)).*?',diffflag) and not re.match(r'^.*?(?:(?:remove)).*?',diffflag)
            # if was_row_moved:
            #     was_row_changed = True
            for col in row:
                col_text = '{c}'.format(c=col)
                if isinstance(col,dict) or isinstance(col,list):
                    col_text = json.dumps(col)
                # TODO: iteratively detect {'parts':[...,{'text':'...','role':'added|removed|role-added...'}]}
                # super complicated
                was_row_changed = was_row_changed or re.match(r'.*?(?:(?:<<ADDED>>)|(?:<<REMOVED>>)).*?',col_text,flags=re.DOTALL)
            was_row_changed = was_row_changed or was_row_moved # changing position is a change too
            if was_row_added or was_row_removed or was_row_changed:
                col_data = {'parts':[col_data,' (changed)']}
    return col_data,flags


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
        'on_col': enchancement_plugin__add_diff_classes_per_row__on_col,
    },
]











# and now 2 main function - to prep column markup and row markup - the main things that we have in the report

def prep_htmlmarkup_col(col,col_index,flags=[],column_specs=[],other_cols_ref=[]):
    
    if not('skip_plugin_enchancement' in flags):
        for plugin in enchancement_plugins:
            if plugin['enabled']:
                if 'on_col' in plugin:
                    result_upd,flags_upd = plugin['on_col'](col,col_index,flags,column_specs,other_cols_ref)
                    col = result_upd
                    flags = list(set([]+flags+flags_upd))
    
    col_css_classes = ['mdmreport-contentcell']
    if sanitize_idfield( column_specs[col_index] ):
        col_css_classes.append('mdmreport-col-{colclass}'.format(colclass=sanitize_idfield( column_specs[col_index] )))
    if col_index>=0:
        col_css_classes.append('mdmreport-colindex-{col_index}'.format(col_index=col_index))
    for flag in [flag for flag in flags if re.match(r'^\s*?format-cssclass-\w',flag)]:
        cssclassname = re.sub(r'^\s*?format-cssclass-(\w[\w\-.]*).*?$',lambda m: m[1],flag)
        col_css_classes.append(cssclassname)

    result_formatted = '<td class="{added_css_classes}"{otherattrs}>{col}</td>'.format(
        col = sanitize_tablecellcontents(col,column_specs[col_index],flags),
        added_css_classes = ' '.join(col_css_classes),
        otherattrs = ' data-columnid="{colid}"'.format(colid=sanitize_idfield( column_specs[col_index] ) if sanitize_idfield( column_specs[col_index] ) else '') if 'header' in flags else ''
    )
    return result_formatted


def prep_htmlmarkup_row(row,flags=[],column_specs=[]):
    
    def prep_updated_col_flags(col,col_index,column_specs):
        flags_global = flags
        flags_add = []
        col_type = column_specs[col_index]
        if (not ('header' in flags_global)) and (not(not(re.match(r'^\s*?script\w*\s*?$',col_type))) or not(not(re.match(r'^\s*?rawtext\w*\s*?$',col_type))) or ( ('section-routing' in flags_global) and (not(not(re.match(r'^\s*?label',col_type)))) ) ):
            flags_add.append('format_syntax')
        return flags_global + flags_add
    
    if not('skip_plugin_enchancement' in flags):
        for plugin in enchancement_plugins:
            if plugin['enabled']:
                if 'on_row' in plugin:
                    row_upd,flags_upd = plugin['on_row'](row,flags,column_specs,other_cols_ref=row)
                    row = row_upd
                    flags = list(set([]+flags+flags_upd))
    
    col_css_classes = ['mdmreport-record']
    if 'header' in flags:
        col_css_classes.append('mdmreport-record-header')
    for flag in [flag for flag in flags if re.match(r'^\s*?format-cssclass-\w',flag)]:
        cssclassname = re.sub(r'^\s*?format-cssclass-(\w[\w\-.]*).*?$',lambda m: m[1],flag)
        col_css_classes.append(cssclassname)

    result_formatted = '<tr class="{added_css_classes}">{columns}</tr>'.format(
        columns = ''.join([ prep_htmlmarkup_col(col,col_index,flags=prep_updated_col_flags(col,col_index,column_specs),column_specs=column_specs,other_cols_ref=row) for col_index,col in enumerate((row or [''])) ]),
        added_css_classes = ' '.join(col_css_classes)
    )
    
    return result_formatted




# and the main procedure - prepare overall html markup
# that's the meaningful entry point
# that's what this script does - gets input data from json and produces html

def produce_html(inp):

    result_ins_htmlmarkup_title = '???'
    result_ins_htmlmarkup_heading = '???'
    result_ins_htmlmarkup_reporttype = sanitize_text_html(inp['report_type']) if 'report_type' in inp else '???'
    result_ins_htmlmarkup_headertext = '{reporttype} Report'.format(reporttype=result_ins_htmlmarkup_reporttype)
    result_ins_htmlmarkup_banner = ''
    if result_ins_htmlmarkup_reporttype=='MDD':
        result_ins_htmlmarkup_title = 'MDD: {filepath}'.format(filepath=sanitize_text_html(sanitize_text_extract_filename(inp['source_file'])))
        result_ins_htmlmarkup_heading = 'MDD: {filepath}'.format(filepath=sanitize_text_html(sanitize_text_extract_filename(inp['source_file'])))
        result_ins_htmlmarkup_headertext = '' # it's too obvious, we shouldn't print unnecessary line; it says "MDD" with a very big font size in h1
    elif result_ins_htmlmarkup_reporttype=='diff':
        result_ins_htmlmarkup_title = 'Diff: {MDD_A} vs {MDD_B}'.format(MDD_A=sanitize_text_html(sanitize_text_extract_filename(inp['source_left'])),MDD_B=sanitize_text_html(sanitize_text_extract_filename(inp['source_right'])))
        result_ins_htmlmarkup_heading = 'Diff'
    else:
        result_ins_htmlmarkup_title = '???'
        result_ins_htmlmarkup_heading = '???'
    result_ins_htmlmarkup_banner = sanitize_tablecellcontents( []+[{'name':'datetime','value':sanitize_text_date(inp['report_datetime_utc'])}]+inp['source_file_metadata'], flags=['format_semicolon'] )
    


    result_column_headers = ( ( [ '{col}'.format(col=col) for col in inp['report_scheme']['columns'] ] if 'columns' in inp['report_scheme'] else [] ) if 'report_scheme' in inp else [] )
    result_column_headers_text_specs = (inp['report_scheme']['column_headers'] if 'column_headers' in inp['report_scheme'] else {}) if 'report_scheme' in inp else {}

    report_data_sections = []
    for section_obj in ( inp['sections'] if 'sections' in inp else [] ):
        data_add = []
        for row in ( section_obj['content'] if section_obj['content']else [] ):
            row_add = []
            for col in result_column_headers:
                # row_add.append( sanitize_tablecellcontents(row[col],col_type=col,section_type=section_obj['name']) if col in row else '' )
                row_add.append( row[col] if col in row else '' )
            data_add.append(row_add)
        report_data_sections.append({'name':section_obj['name'],'data':data_add})



    report_htmlmarkup_column_headers = ''.join( [ prep_htmlmarkup_row(row,flags=['header'],column_specs=result_column_headers) for row in [[(result_column_headers_text_specs[col_title] if col_title in result_column_headers_text_specs else col_title) for col_title in result_column_headers]] ] )

    report_htmlmarkup_mainpart_with_tables = ''.join([
        '{table_begin}{table_header_row}{table_contents}{table_end}'.format(
            table_begin = report_html_template.TEMPLATE_HTML_TABLE_BEGIN.replace('{{TABLE_NAME}}',sanitize_text_html(section_data['name'])).replace('{{TABLE_ID}}',sanitize_idfield(section_data['name'])),
            table_header_row = report_htmlmarkup_column_headers,
            table_contents = ''.join( [ prep_htmlmarkup_row(row,column_specs=result_column_headers,flags=['section-{sec_id}'.format(sec_id=sanitize_idfield(section_data['name']))]) for row in section_data['data'] ] ),
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
        '{{INS_REPORTTYPE}}', sanitize_idfield(result_ins_htmlmarkup_reporttype)
    ).replace(
        '{{INS_HEADING}}', result_ins_htmlmarkup_heading
    ).replace(
        '{{INS_BANNER}}', result_ins_htmlmarkup_banner
    )

    return result





def entry_point(config={}):
    time_start = datetime.now()
    parser = argparse.ArgumentParser(
        description="Produce a summary of MDD in html (read from json)"
    )
    parser.add_argument(
        '--inpfile',
        help='JSON with Input MDD map'
    )
    args = None
    args_rest = None
    if( ('arglist_strict' in config) and (not config['arglist_strict']) ):
        args, args_rest = parser.parse_known_args()
    else:
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


if __name__ == '__main__':
    entry_point({'arglist_strict':True})
