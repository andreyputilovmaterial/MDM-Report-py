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



# TODO: (done) detect columns to show in "routing" type reports better
# TODO: (what? I do not understand lol sad and funny) column widths in "routing" type reports should be fixed
# TODO: (too complicated - our diffed text is an array of "parts" and they do not correspond to lines; searching for "\n" within within all these {"parts":[{"text":... is complicated) introduce a class when something changed within a row - useful for "routing" type rreports with long lines where something changed far to the right and we can't quickly see it
# TODO: (declined, unnecessary complications) empty rows with name="" are looking strange - maybe add some "attribute" (hidden text to show, same as we are doing with attributes), and show something like "(root element)" so that it is less confusing
# TODO: a failed to save a file with diff when comparing html results with diffs - investigate
# TODO: (should be good, why would I change this; declined) col widths js code - .mdmreport-colindex-xxx classes - change it to some more general way of accessing columns by numbers - not working with added col with jira links



# helper text prep functions first

def sanitize_text_normalizelinebreaks(inp_value):
    return re.sub(r'\r','\n',re.sub(r'\r?\n','\n',inp_value))

def html_sanitize_text(inp_value,flags=[]):
    result = inp_value
    if not isinstance(result,str):
        raise Exception('when html_sanitize_text() called input must be of str type')
    if 'format-escapequotes-vbsstyle' in flags:
        result = result.replace('"','""')
    result = sanitize_text_normalizelinebreaks(result)
    # basic clean up - basic conversion escaping all tags
    result =  html.escape('{result}'.format(result=result))
    result = result.replace('\n','<br />')

    special_pattern = '<<KEYWORD>>'
    special_pattern = html.escape(special_pattern)
    # TODO: finding injected markers should be depricated in future versions
    result = result.replace(special_pattern.replace('KEYWORD','ADDED'),'<span class="mdmdiff-inlineoverlay-added">').replace(special_pattern.replace('KEYWORD','REMOVED'),'<span class="mdmdiff-inlineoverlay-removed">').replace(special_pattern.replace('KEYWORD','ENDADDED'),'</span>').replace(special_pattern.replace('KEYWORD','ENDREMOVED'),'</span>')
    for keyword in ['ADDED','REMOVED','ENDADDED','ENDREMOVED']:
        if special_pattern.replace('KEYWORD',keyword) in result:
            raise Exception('Text insert markers found: should be deprecated (found: "{aaa}" in "{bbb}")'.format(aaa=special_pattern.replace('KEYWORD',keyword),bbb=result))
    # # some replacement to add syntax so that dates are formatted
    # # if there'result some certain markup - that shouln't be escape
    # # it should be printed as markup so that js works and converts UTC dates to local time
    # result = re.sub(r'&lt;&lt;DATE:(.*?)&gt;&gt;',lambda m:'<span class="mdmreport-role-date" data-role="date">{d}</span>'.format(d=m[1]),result)
    # and one more transformation - some parts
    # (called "scripting" - including MDD syntax for all MDD items and routing syntax)
    # so these parts include raw multi-line text - we'll normalize line breaks
    
    result = re.sub('([^\t\r\n\x20-\x7E])',lambda m: '&#{n};'.format(n=ord(m[1])),result)
    return result

def html_sanitize_text_date(s):
    #return '<<DATE:{d}>>'.format(d=s)
    return {'parts':[{'text':s,'role':'date'}]}

def sanitize_idfield(s):
    return re.sub(r'-+','-',re.sub(r'^-*','',re.sub(r'-*$','',re.sub(r'[^\w\-\.]','-',s))))

def sanitize_text_extract_filename(s):
    return re.sub(r'^.*[/\\](.*?)\s*?$',lambda m: m[1],'{sstr}'.format(sstr=s))



def html_sanitize_value_astext(inp_value,flags=[]):
    return html_sanitize_text(inp_value,flags)

def html_sanitize_value_asproperties(inp_value,flags=[]):
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
        part_iterate = ', </p><p class="mdmreport-prop-row">'.join([
            '{ins_partbegin}{fieldname}{ins_partconjunction}{fieldvalue}{ins_partend}'.format(
                fieldname = html_sanitize_text(row['name']),
                fieldvalue = html_sanitize_value_general(row['value'],[]+flags+['format-escapequotes-vbsstyle']),
                ins_partbegin = ins_partbegin,
                ins_partconjunction = ins_partconjunction,
                ins_partend = ins_partend
            ) for row in inp_value
        ]),
        part_end = '</p>'
    )
    return result

def html_sanitize_value_general(inp_value,flags=[]):
    # it's recursive!
    if isinstance(inp_value,dict) and 'role' in inp_value and inp_value['role']:
        flag_add = 'role-{cssclasspart}'.format(cssclasspart=re.sub(r'^\s*?(?:role-\s*?)?','',inp_value['role']))
        if not (flag_add in flags):
            return html_sanitize_value_general({**inp_value,**{'role':None}},flags=[]+flags+[flag_add])
    for flag in flags:
        if (flag=='role-time') or (flag=='role-date') or (flag=='role-datetime'):
            return '<span class="mdmreport-role-date" data-role="date">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-added':
            return '<span class="mdmdiff-inlineoverlay-added">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-removed':
            return '<span class="mdmdiff-inlineoverlay-removed">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-sronly':
            return '<span class="mdmreport-sronly">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-label':
            # return '<label>{d}</label>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
            return '<span class="mdmreport-label-pseudo" data-added="{f}"></span>'.format(f=htmlattr_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
    result = None
    if False:
        pass
    elif isinstance(inp_value,int) or isinstance(inp_value,float):
        result = html_sanitize_value_general('{f}'.format(f=inp_value),flags) 
    elif not inp_value:
        result = ''
    elif isinstance(inp_value,list) and ([(True if 'name' in dict.keys(item) else False) for item in inp_value].count(True)==len(inp_value)):
        result = html_sanitize_value_asproperties(inp_value,flags)
    elif isinstance(inp_value,dict) and 'parts' in dict.keys(inp_value):
        result = ''.join( html_sanitize_value_general(part['text'],[]+flags+(['role-{cssclasspart}'.format(cssclasspart=re.sub(r'^\s*?(?:role-\s*?)?','',part['role']))] if 'role' in part else [])) if isinstance(part,dict) and 'text' in dict.keys(part) else html_sanitize_value_general(part,flags) for part in inp_value['parts'] )
    elif isinstance(inp_value,dict) and 'text' in dict.keys(inp_value):
        result = html_sanitize_value_general(inp_value['text'],flags)
    elif isinstance(inp_value,str):
        result =  html_sanitize_value_astext(inp_value,flags)
    elif isinstance(inp_value,dict) or isinstance(inp_value,list):
        result =  html_sanitize_value_astext(json.dumps(inp_value),flags)
    elif ('{fmt}'.format(fmt=inp_value)==inp_value):
        result =  html_sanitize_value_astext(inp_value,flags)
    else:
        result =  html_sanitize_value_astext(json.dumps(inp_value),flags)
    return result

def htmlattr_sanitize_value_general(inp_value,flags=[]):
    def is_empty(s):
        if isinstance(s,int) or isinstance(s,int):
            return False
        elif not s:
            return True
        else:
            return False
    for flag in flags:
        if flag=='role-sronly':
            return ''
        elif flag=='role-added' and not ('role-noshowdiff' in flags):
            return '[+added: {i}]'.format(i=htmlattr_sanitize_value_general({**inp_value,'role':None},[f for f in flags if not (flag==f)]))
        elif flag=='role-removed' and not ('role-noshowdiff' in flags):
            return '[-removed: {i}]'.format(i=htmlattr_sanitize_value_general({**inp_value,'role':None},[f for f in flags if not (flag==f)]))
    if isinstance(inp_value,dict) and 'role' in inp_value and inp_value['role']:
        return htmlattr_sanitize_value_general({**inp_value,'role':None},flags=[]+flags+['role-{cssclasspart}'.format(cssclasspart=re.sub(r'^\s*?(?:role-\s*?)?','',inp_value['role']))])
    if isinstance(inp_value,str):
        # return inp_value.replace('\\','\\\\').replace('"','\\"').replace('\n','\n') # lol funny
        return inp_value.replace('"','&#34;') # .replace('\n','&#13;')
    elif isinstance(inp_value,int) or isinstance(inp_value,float):
        return htmlattr_sanitize_value_general('{f}'.format(f=inp_value))
    elif not inp_value:
        return ''
    elif isinstance(inp_value,list):
        return ',\n'.join([p for p in [htmlattr_sanitize_value_general(part,flags=flags) for part in inp_value] if not is_empty(p)])
    elif isinstance(inp_value,dict) and 'text' in inp_value:
        return htmlattr_sanitize_value_general(inp_value['text'],flags)
    elif isinstance(inp_value,dict) and 'name' in inp_value and 'value' in inp_value:
        return '{prop} = &#34;{val}&#34;'.format(prop=htmlattr_sanitize_value_general(inp_value['name'],flags),val=htmlattr_sanitize_value_general(inp_value['value'],flags))
    elif isinstance(inp_value,dict) and 'parts' in inp_value:
        return ''.join([p for p in [htmlattr_sanitize_value_general(part,flags=flags) for part in inp_value['parts']] if not is_empty(p)])
    else:
        return htmlattr_sanitize_value_general('{f}'.format(f=inp_value))

def html_sanitize_tablecellcontents(inp_value,flags=[]):
    result = None
    if isinstance(inp_value,int) or isinstance(inp_value,float):
        return html_sanitize_tablecellcontents('{f}'.format(f=inp_value),flags)
    elif not inp_value:
        return ''
    result = html_sanitize_value_general(inp_value,[flag for flag in flags if flag!='format_syntax'])
    if 'format_syntax' in flags:
        result = '<pre>{content}</pre>'.format(content=sanitize_text_normalizelinebreaks(result)) # it's already done globally at the first line of html_sanitize_value_astext which should have been already called
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

def enchancement_plugin__combine_attributes_into_master_name_col__on_table(rows,column_specs,flags=[]):
    def is_column_id_for_attribute_column(col_id):
        return re.match(r'^.*?\b(?:attribute)(?:s)?\b\s*?(?:\s*?.*?)?\s*?$',re.sub(r'_',' ',col_id))
    def is_empty(s):
        if isinstance(s,int) or isinstance(s,float):
            return False
        elif not s:
            return True
        else:
            return False
    # def is_column_id_for_name_column(col_id):
    #     return re.match(r'^.*?\bname\s*?$',re.sub(r'_',' ',col_id))
    col_id_name = column_specs.index('name') if 'name' in column_specs else -1
    col_ids_atts = []
    for i,col in enumerate(column_specs):
        if is_column_id_for_attribute_column(col):
            col_ids_atts.append(i)
    is_active = ( not ('plugin_combine_attributes_already_called' in flags) ) and ( (col_id_name>=0) and (len(col_ids_atts)>0) )
    if is_active:
        columns = []
        if len(rows)>0:
            columns = [ col for col in rows[0] ]
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
                    col_att_data_matchingcol = columns[col_id_att] #  column_specs[col_id_att]
                    if not col_att_data_is_duplicate:
                        check_duplicates.append(col_att_data_fingerprint)
                    name_col_updated_parts.append({
                        'content': col_att_data_formatted,
                        'fingerprint': col_att_data_fingerprint,
                        'is_duplicate': col_att_data_is_duplicate,
                        'matching_col': col_att_data_matchingcol,
                        'data': col_att_data,
                    })

            name_col_upd_data = {'parts':[
                row[col_id_name]
            ]}
            name_col_updated_parts_excluding_duplicates = [p for p in name_col_updated_parts if not p['is_duplicate'] ]
            for def_add in name_col_updated_parts_excluding_duplicates:
                add_col_label = True
                if len(name_col_updated_parts_excluding_duplicates)==1:
                    add_col_label = False
                if def_add['matching_col']==def_add['data']:
                    add_col_label = False
                add_parts = []
                add_parts.append({'text':{'text':', with ','role':'sronly'},'role':'label'})
                if add_col_label:
                    add_parts.append({'text':def_add['matching_col'] + '\n','role':'label'})
                add_parts.append(def_add['content'])
                name_col_upd_data['parts'].append({'role':'label','text':{'role':'noshowdiff','parts':add_parts}})
            row[col_id_name] = name_col_upd_data
            row_filtered = [ col for i,col in enumerate(row) if not (i in row_exclusions) ]
            rows_upd.append(row_filtered)
        rows = rows_upd
        column_specs = [ col for i,col in enumerate(column_specs) if not (i in row_exclusions) ]

    return rows,column_specs,flags


def enchancement_plugin__add_diff_classes_per_row__on_row(row,flags,column_specs,other_cols_ref=[]):
    def did_col_change_deep_inspect(data):
        if isinstance(data,str):
            if '<<ADDED>>' in data:
                return True
            if '<<REMOVED>>' in data:
                return True
            return False
        elif isinstance(data,list):
            result = False
            for slice in data:
                result = result or did_col_change_deep_inspect(slice)
            return result
        elif isinstance(data,dict) and 'text' in data:
            if 'role' in data:
                if re.match(r'^\s*?(?:role-)?(?:added|removed).*?',data['role'],flags=re.I):
                    return True
            return did_col_change_deep_inspect(data['text'])
        elif isinstance(data,dict) and 'parts' in data:
            return did_col_change_deep_inspect(data['parts'])
        elif isinstance(data,dict) and 'name' in data and 'value' in data:
            return did_col_change_deep_inspect(data['value'])
        else:
            return did_col_change_deep_inspect('{f}'.format(f=data))
    is_active = ( not ('plugin_add_diff_classes_per_row_already_called' in flags) ) and ( ('flagdiff' in column_specs) )
    flags_added = []
    if is_active:
        classes_add = ''
        diffflag = row[column_specs.index('flagdiff')]
        was_row_added = re.match(r'^.*?(?:(?:add)|(?:insert)).*?',diffflag)
        was_row_removed = re.match(r'^.*?(?:(?:remove)|(?:delete)).*?',diffflag)
        was_row_changed = False
        was_row_moved = re.match(r'^.*?(?:(?:move)).*?',diffflag) and not re.match(r'^.*?(?:(?:remove)).*?',diffflag)
        was_row_movedfromhere = 'moved from' in diffflag
        # if was_row_moved:
        #     was_row_changed = True
        for col in other_cols_ref:
            # TODO: same comment as in "on_col" event
            # do we really need such inspections?
            # this might be complicted
            was_row_changed = was_row_changed or did_col_change_deep_inspect(col)
        if was_row_added:
            flags_added.append('format-cssclass-mdmdiff-added')
        if was_row_removed:
            flags_added.append('format-cssclass-mdmdiff-removed')
        if was_row_changed and not ( was_row_added or was_row_removed ):
            flags_added.append('format-cssclass-mdmdiff-diff')
        if was_row_moved and not ( was_row_added or was_row_removed or was_row_changed ):
            flags_added.append('format-cssclass-mdmdiff-moved')
            flags_added.append('format-cssclass-mdmdiff-ghost')
        if was_row_movedfromhere:
            flags_added.append('format-cssclass-mdmdiff-movedfrom')
    return row,flags+flags_added

def enchancement_plugin__add_diff_classes_per_row__on_col(col_data,col_index=None,flags=[],column_specs=[],other_cols_ref=[]):
    def did_col_change_deep_inspect(data):
        if isinstance(data,str):
            if '<<ADDED>>' in data:
                return True
            if '<<REMOVED>>' in data:
                return True
            return False
        elif isinstance(data,list):
            result = False
            for slice in data:
                result = result or did_col_change_deep_inspect(slice)
            return result
        elif isinstance(data,dict) and 'text' in data:
            if 'role' in data:
                if re.match(r'^\s*?(?:role-)?(?:added|removed).*?',data['role'],flags=re.I):
                    return True
            return did_col_change_deep_inspect(data['text'])
        elif isinstance(data,dict) and 'parts' in data:
            return did_col_change_deep_inspect(data['parts'])
        elif isinstance(data,dict) and 'name' in data and 'value' in data:
            return did_col_change_deep_inspect(data['value'])
        else:
            return did_col_change_deep_inspect('{f}'.format(f=data))
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
                # TODO: do we need this?
                # inspecting the whole row, every column, to see if something changed?
                # this can be complicated, as cell contents is not always plain text, it can be complicated structures
                # and checking this iteratively... uuufffhhh no
                # inspecting {'parts':[...,{'text':'...','role':'added|removed|role-added...'}]}
                # super complicated
                was_row_changed = was_row_changed or did_col_change_deep_inspect(col)
            was_row_changed = was_row_changed or was_row_moved # changing position is a change too
            if was_row_added or was_row_removed or was_row_changed:
                col_data = {'parts':[col_data,' (changed)']}
    return col_data,flags


enchancement_plugins = [
    {
        'name': 'combine_attributes_into_master_name_col',
        'enabled': True,
        # 'on_col': enchancement_plugin__combine_attributes_into_master_name_col__on_col,
        'on_table': enchancement_plugin__combine_attributes_into_master_name_col__on_table,
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
    
    try:

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
            col = html_sanitize_tablecellcontents(col,flags),
            added_css_classes = ' '.join(col_css_classes),
            otherattrs = ' data-columnid="{colid}"'.format(colid=sanitize_idfield( column_specs[col_index] ) if sanitize_idfield( column_specs[col_index] ) else '') if 'header' in flags else ''
        )
        return result_formatted
    
    except Exception as e:
        print('html markup: failed when processing column {c}'.format(c=col))
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

        if not('skip_plugin_enchancement' in flags):
            for plugin in enchancement_plugins:
                if plugin['enabled']:
                    if 'on_row' in plugin:
                        row_upd,flags_upd = plugin['on_row'](row,flags,column_specs,other_cols_ref=row)
                        row = row_upd
                        flags = list(set([]+flags+flags_upd))
        
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
        
        return result_formatted
    
    except Exception as e:
        print('html markup: failed when processing row {c}'.format(c='\t'.join(row)))
        raise e

def prep_htmlmarkup_section(section_data,column_specs_global,column_titles,flags=[]):

    try:

        column_specs = section_data['columns'] if 'columns' in section_data else column_specs_global

        row_first = [ row for row in [[(column_titles[col_title] if col_title in column_titles else col_title) for col_title in column_specs]] ]
        rows = []+row_first+section_data['data']

        column_specs_localcopy = column_specs

        table_name = section_data['title']

        table_id = section_data['id']

        ins_banner = ''
        if 'statistics' in section_data:
                ins_banner = '<div class="mdmreport-banner mdmreport-banner-table-details mdmreport-banner-table-details-statistics"><p>Statistics: </p>{body}</div>'.format( body = html_sanitize_tablecellcontents( section_data['statistics'], flags=['format_semicolon'] ) )

        if not('skip_plugin_enchancement' in flags):
            for plugin in enchancement_plugins:
                if plugin['enabled']:
                    if 'on_table' in plugin:
                        result_upd,column_specs_upd,flags_upd = plugin['on_table'](rows,column_specs_localcopy,flags)
                        rows = result_upd
                        column_specs_localcopy = column_specs_upd
                        flags = list(set([]+flags+flags_upd))
    
        return '{table_begin}{table_contents}{table_end}'.format(
            table_begin = report_html_template.TEMPLATE_HTML_TABLE_BEGIN.replace('{{TABLE_NAME}}',html_sanitize_text(table_name)).replace('{{TABLE_ID}}',sanitize_idfield(table_id)).replace('{{INS_TABBANNER}}',ins_banner),
            table_contents = ''.join( [ prep_htmlmarkup_row(row,column_specs=column_specs_localcopy,flags=[]+flags+(['row-header'] if i==0 else [])+['section-{sec_id}'.format(sec_id=sanitize_idfield(section_data['name']))]) for i,row in enumerate(rows) ] ),
            table_end = report_html_template.TEMPLATE_HTML_TABLE_END
        )
    
    except Exception as e:
        print('html markup: failed when processing section {c}'.format(c=section_data['name']))
        raise e




# and the main procedure - prepare overall html markup
# that's the meaningful entry point
# that's what this script does - gets input data from json and produces html

def produce_html(inp):

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
    


    result_column_headers_global = ( ( [ '{col}'.format(col=col) for col in inp['report_scheme']['columns'] ] if 'columns' in inp['report_scheme'] else [] ) if 'report_scheme' in inp else [] )
    result_column_headers_global_text_specs = (inp['report_scheme']['column_headers'] if 'column_headers' in inp['report_scheme'] else {}) if 'report_scheme' in inp else {}

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
        prep_htmlmarkup_section(section_data,result_column_headers_global,result_column_headers_global_text_specs) for section_data in report_data_sections
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
        '{{INS_REPORTTYPE}}', sanitize_idfield(result_ins_htmlmarkup_reporttype)
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





def entry_point(config={}):
    time_start = datetime.now()
    script_name = 'mdmtoolsap html report script'

    parser = argparse.ArgumentParser(
        description="Produce a summary of input file in html (read from json)",
        prog='mdmtoolsap --program report'
    )
    parser.add_argument(
        '--inpfile',
        help='JSON with File Data',
        type=str,
        required=True
    )
    parser.add_argument(
        '--output-format',
        help='Set output format: html or excel',
        type=str,
        required=False
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
        # input_map_filename = '{input_map_filename}'.format(input_map_filename=input_map_filename.resolve())
    # input_map_filename_specs = open(input_map_filename_specs_name, encoding="utf8")
    config_output_format = 'html'
    if args.output_format:
        config_output_format = args.output_format

    print('{script_name}: script started at {dt}'.format(dt=time_start,script_name=script_name))

    #print('{script_name}: reading {fname}'.format(fname=input_map_filename,script_name=script_name))
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

    result = None
    if config_output_format=='html':
        result = produce_html(inpfile_map_in_json)
    else:
        raise ValueError('report.py: unsupported output format: {fmt}'.format(fmt=config_output_format))
    
    result_fname = ( Path(input_map_filename).parents[0] / '{basename}{ext}'.format(basename=Path(input_map_filename).name,ext='.html') if Path(input_map_filename).is_file() else re.sub(r'^\s*?(.*?)\s*?$',lambda m: '{base}{added}'.format(base=m[1],added='.html'),'{path}'.format(path=input_map_filename)) )
    print('{script_name}: saving as "{fname}"'.format(fname=result_fname,script_name=script_name))
    with open(result_fname, "w") as outfile:
        outfile.write(result)

    time_finish = datetime.now()
    print('{script_name}: finished at {dt} (elapsed {duration})'.format(dt=time_finish,duration=time_finish-time_start,script_name=script_name))


if __name__ == '__main__':
    entry_point({'arglist_strict':True})
