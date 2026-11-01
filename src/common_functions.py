# Shared text/HTML sanitization and formatting helpers.
#
# Pure functions with no package state. Used by ``report_create`` and by the
# backend plugins under ``plugins/``.

import re
import json
import html


def is_property_list(data):
    try:
        if isinstance(data,list) and ([(True if ('name' in dict.keys(item) and 'value' in dict.keys(item)) else False) for item in data].count(True)==len(data)):
            return True
        return False
    except:
        return False

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
    if 'format-escapequotes-htmlentity' in flags:
        result = result.replace('"','&quot;')
    special_pattern = '<<KEYWORD>>'
    special_pattern = html.escape(special_pattern)
    
    # TODO: remove deprecated code
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

def html_sanitize_htmlattribute(s,flags=None):
    flags = (flags or []) + ['format-escapequotes-htmlentity'] # ['format-escapequotes-htmlentity','format-html-linebreaksallowed']
    return html_sanitize_text(html_sanitize_value_general(s,flags),flags)

def html_sanitize_text_date(s):
    #return '<<DATE:{d}>>'.format(d=s)
    return {'parts':[{'text':s,'role':'date'}]}

def sanitize_idfield(s):
    return re.sub(r'-+','-',re.sub(r'^-*','',re.sub(r'-*$','',re.sub(r'[^\w\-\.]','-',s))))

def sanitize_cssfield(s):
    return re.sub(r'-+','-',re.sub(r'^-*','',re.sub(r'-*$','',re.sub(r'[^\w\-]','-',s))))

def sanitize_text_extract_filename(s):
    return re.sub(r'^.*[/\\](.*?)\s*?$',lambda m: m[1],'{sstr}'.format(sstr=s))



def html_sanitize_value_astext(inp_value,flags=[]):
    return html_sanitize_text(inp_value,flags)

# def html_sanitize_value_asproperties(inp_value,flags=[]):
#     # removing css classes for property coloring - reduced memory consumption a lot; AP 10/12/2024
#     # unsuppress to have properties colored
#     # ins_partbegin = '<span class="mdmreport-prop-fieldname">'
#     # ins_partconjunction =  '</span> = "<span class="mdmreport-prop-fieldvalue">'
#     # ins_partend = '</span>"'
#     ins_partbegin = ''
#     ins_partconjunction =  ' = "'
#     ins_partend = '"'
#     if 'format_semicolon' in flags:
#         ins_partbegin = ''
#         ins_partconjunction =  ': '
#         ins_partend = ''
#     result = '{part_begin}{part_iterate}{part_end}'.format(
#         part_begin = '<p class="mdmreport-prop-row">',
#         part_iterate = ', </p><p class="mdmreport-prop-row">'.join([
#             '{ins_partbegin}{fieldname}{ins_partconjunction}{fieldvalue}{ins_partend}'.format(
#                 fieldname = html_sanitize_text(row['name']),
#                 fieldvalue = html_sanitize_value_general(row['value'],[]+flags+['format-escapequotes-vbsstyle']),
#                 ins_partbegin = ins_partbegin,
#                 ins_partconjunction = ins_partconjunction,
#                 ins_partend = ins_partend
#             ) for row in inp_value
#         ]),
#         part_end = '</p>'
#     )
#     return result

def html_sanitize_value_asproperties(inp_value,flags=[]):
    def _err(msg):
        raise Exception(f'Error: html_sanitize_value_asproperties: {msg}')
    def make_outer_txt(
        inp_value,
        patterns,
        make_row_txt,
        flags,
    ):
        pattern_global_begin, pattern_global_end, pattern_junction_outer, *patterns_rest = patterns
        txt = ''
        txt += pattern_global_begin
        items = [row for row in inp_value] # sorry we need for the look ahead for the counter to know which is last
        for i,row in enumerate(items):
            txt_thisrow = ''
            is_first = i==0
            is_last = i==len(items)-1
            if not is_last:
                txt_thisrow += pattern_junction_outer
            txt_thisrow += make_row_txt(row,(is_first,is_last),patterns_rest,flags)
            txt += txt_thisrow
        txt += pattern_global_end
        return txt
    def make_row_txt(
        inp_value,
        first_or_last,
        patterns,
        # make_propname_txt,
        # make_propvalue_txt,
        flags,
    ):
        fieldname = html_sanitize_text(inp_value['name'])
        fieldvalue = html_sanitize_value_general(inp_value['value'],[]+flags+['format-escapequotes-vbsstyle'])
        fieldrole = inp_value.get('role',None)
        fieldflag = f'role-{fieldrole}' if fieldrole else ''
        is_first, is_last = first_or_last
        pattern_junction_inner, pattern_row_begin, pattern_row_prop_begin, pattern_row_prop_end, pattern_row_propvalue_conjunction, pattern_row_value_begin, pattern_row_value_end, pattern_row_end = patterns
        txt = ''
        txt += pattern_row_begin
        txt += pattern_row_prop_begin
        txt += fieldname
        txt += pattern_row_prop_end
        txt += pattern_row_propvalue_conjunction
        txt += pattern_row_value_begin
        txt += fieldvalue
        txt += pattern_row_value_end
        txt += ( pattern_junction_inner if not is_last else '' )
        txt += pattern_row_end
        if (fieldflag=='role-time') or (fieldflag=='role-date') or (fieldflag=='role-datetime'):
            txt =  f'<span class="mdmreport-role-date" data-role="date">{txt}</span>'
        elif fieldflag=='role-added':
            txt = f'<span class="mdmdiff-inlineoverlay-added">{txt}</span>'
        elif fieldflag=='role-removed':
            txt = f'<span class="mdmdiff-inlineoverlay-removed">{txt}</span>'
        elif fieldflag=='role-source_added':
            txt = f'<span class="mdmdiff-inlineoverlay-underlying-added">{txt}</span>'
        elif fieldflag=='role-source_removed':
            txt = f'<span class="mdmdiff-inlineoverlay-underlying-removed">{txt}</span>'
        elif fieldflag=='role-sronly':
            txt = f'<span class="mdmreport-sronly">{txt}</span>'
        elif fieldflag=='role-label':
            txt = f'<span class="mdmreport-label-pseudo" data-added="{txt}"></span>'
        elif fieldflag=='role-ellipsis':
            # TODO: ellipsis?
            txt = txt
        return txt
    # removing css classes for property coloring - reduced memory consumption a lot; AP 10/12/2024
    format_option_colorsytxhlight = False
    format_option_syntax = "customproperties" if 'format_semicolon' not in flags else 'semicolon'
    pattern_global_begin = None
    pattern_global_end = None
    pattern_junction_outer = None
    pattern_junction_inner = None
    pattern_row_begin = None
    pattern_row_prop_begin = None
    pattern_row_prop_end = None
    pattern_row_propvalue_conjunction = None
    pattern_row_value_begin = None
    pattern_row_value_end = None
    pattern_row_end = None
    if format_option_syntax=='customproperties':
        pattern_global_begin = ''
        pattern_global_end = ''
        pattern_junction_outer = ''
        pattern_junction_inner = ', '
        pattern_row_begin = '<p class="mdmreport-prop-row">'
        pattern_row_prop_begin = ''+('<span class="mdmreport-prop-fieldname">' if format_option_colorsytxhlight else '')+''
        pattern_row_prop_end = ''+('</span>' if format_option_colorsytxhlight else '')+''
        pattern_row_propvalue_conjunction = ' = '
        pattern_row_value_begin = '"'+('<span class="mdmreport-prop-fieldvalue">' if format_option_colorsytxhlight else '')+''
        pattern_row_value_end = ''+('</span>' if format_option_colorsytxhlight else '')+'"'
        pattern_row_end = '</p>'
    elif format_option_syntax=='semicolon':
        pattern_global_begin = ''
        pattern_global_end = ''
        pattern_junction_outer = ''
        pattern_junction_inner = ''
        pattern_row_begin = '<p class="mdmreport-prop-row">'
        pattern_row_prop_begin = ''+('<span class="mdmreport-prop-fieldname">' if format_option_colorsytxhlight else '')+''
        pattern_row_prop_end = ''+('</span>' if format_option_colorsytxhlight else '')+''
        pattern_row_propvalue_conjunction = ': '
        pattern_row_value_begin = ''+('<span class="mdmreport-prop-fieldvalue">' if format_option_colorsytxhlight else '')+''
        pattern_row_value_end = ''+('</span>' if format_option_colorsytxhlight else '')+''
        pattern_row_end = '</p>'
    else:
        return  _err(f'unknown format spec: format_option_syntax == "{format_option_syntax}"')
    return make_outer_txt(
        inp_value,
        (
            pattern_global_begin,
            pattern_global_end,
            pattern_junction_outer,
            pattern_junction_inner,
            pattern_row_begin,
            pattern_row_prop_begin,
            pattern_row_prop_end,
            pattern_row_propvalue_conjunction,
            pattern_row_value_begin,
            pattern_row_value_end,
            pattern_row_end,
            ),
        make_row_txt,
        # lambda inp_value, first_or_last, patterns: make_row_txt(inp_value, first_or_last, patterns, make_propname_txt, make_propvalue_txt),
        flags,
    )

def html_sanitize_value_general(inp_value,flags=[]):
    # it's recursive!
    if isinstance(inp_value,dict) and 'role' in inp_value and inp_value['role']:
        flag_add = 'role-{cssclasspart}'.format(cssclasspart=re.sub(r'^\s*?(?:role-\s*?)?','',f"{inp_value['role']}"))
        if not (flag_add in flags):
            return html_sanitize_value_general({**inp_value,**{'role':None}},flags=[]+flags+[flag_add])
    for flag in flags:
        if (flag=='role-time') or (flag=='role-date') or (flag=='role-datetime'):
            return '<span class="mdmreport-role-date" data-role="date">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-added':
            return '<span class="mdmdiff-inlineoverlay-added">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-removed':
            return '<span class="mdmdiff-inlineoverlay-removed">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-source_added':
            return '<span class="mdmdiff-inlineoverlay-underlying-added">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-source_removed':
            return '<span class="mdmdiff-inlineoverlay-underlying-removed">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-sronly':
            return '<span class="mdmreport-sronly">{d}</span>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-label':
            # return '<label>{d}</label>'.format(d=html_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
            return '<span class="mdmreport-label-pseudo" data-added="{f}"></span>'.format(f=htmlattr_sanitize_value_general(inp_value,flags=list(set(flags)-set([flag]))))
        elif flag=='role-ellipsis':
            _payload = html_sanitize_htmlattribute(inp_value,flags=list(set(flags)-set([flag])))
            return '<span class="mdmreport-txt-ellipsis" title="Click to expand file" data-role="ellipsis" data-ellipsis="{d}"><span class="mdmreport-txt-ellipsis-1">...</span><span class="mdmreport-txt-ellipsis-2"><span class="mdmreport-txt-ellipsis-br"></span><span class="mdmreport-txt-ellipsis-mainline"> @@ +{n} characters @@</span><span class="mdmreport-txt-ellipsis-br"></span></span><span class="mdmreport-txt-ellipsis-3">...</span></span>'.format(d=_payload,n=len(_payload))
    result = None
    if   isinstance(inp_value,int) or isinstance(inp_value,float):
        result = html_sanitize_value_general('{f}'.format(f=inp_value),flags) 
    elif not inp_value:
        result = ''
    elif is_property_list(inp_value):
        result = html_sanitize_value_asproperties(inp_value,flags)
    elif isinstance(inp_value,list):
        flag_role_add = []
        result = ''.join(html_sanitize_value_general(piece,(flags or [])+flag_role_add) for piece in inp_value)
    elif isinstance(inp_value,dict) and 'parts' in dict.keys(inp_value):
        flag_role_add = ['role-{cssclasspart}'.format(cssclasspart=re.sub(r'^\s*?(?:role-\s*?)?','',f"{inp_value['role']}"))] if 'role' in inp_value and inp_value['role'] else []
        result = html_sanitize_value_general(inp_value['parts'],(flags or [])+flag_role_add)
        # result = ''.join( html_sanitize_value_general(part['text'],[]+flags+(['role-{cssclasspart}'.format(cssclasspart=re.sub(r'^\s*?(?:role-\s*?)?','',part['role']))] if 'role' in part else [])) if isinstance(part,dict) and 'text' in dict.keys(part) else html_sanitize_value_general(part,flags) for part in inp_value['parts'] )
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
        # TODO: do we need to handle other roles here? Maybe bring it to a dedicated fn?
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
        # return ''.join([p for p in [htmlattr_sanitize_value_general(part,flags=flags) for part in inp_value['parts']] if not is_empty(p)])
        flag_role_add = ['role-{cssclasspart}'.format(cssclasspart=re.sub(r'^\s*?(?:role-\s*?)?','',inp_value['role']))] if 'role' in inp_value and inp_value['role'] else []
        return htmlattr_sanitize_value_general(inp_value['parts'],(flags or []) + flag_role_add)
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


def sanitize_text_general(inp_value,flags=[]):
    def is_property_list(input):
        try:
            if isinstance(input,list) and ([(True if ('name' in dict.keys(item) and 'value' in dict.keys(item)) else False) for item in input].count(True)==len(input)):
                return True
            return False
        except:
            return False
    def is_diff_segment_dict(input):
        if isinstance(input,dict):
            has_payload_textfield = 'text' in input
            has_payload_partsfield = 'parts' in input and isinstance(input['parts'],list)
            has_payload = has_payload_textfield or has_payload_partsfield
            has_conflicting_payloads = has_payload_textfield and has_payload_partsfield
            all_keys = input.keys()
            nonstd_keys = set(all_keys) - {'text','parts','role'}
            if has_payload and not has_conflicting_payloads and (len(nonstd_keys)==0):
                return True
        return False
    def is_empty(input):
        if input==0:
            return False
        elif is_diff_segment_dict(input):
            if not input:
                return True
            if 'text' in input and not is_empty(input['text']):
                return False
            if 'parts' in input and not is_empty(input['parts']):
                return False
            return True
        elif isinstance(input,dict):
            return not input
        elif is_property_list(input):
            if not input:
                return True
            result = True
            for piece in input:
                result = result and is_empty(piece['value'])
            return result
        elif isinstance(input,list):
            if not input:
                return True
            result = True
            for piece in input:
                result = result and is_empty(piece)
            return result
        else:
            # attention
            # empty list, empty dict evaluates to empty
            return not input
    if is_empty(inp_value):
        return ''
    elif is_property_list(inp_value):
        def esc(s):
            return f'{s}'.replace('"','""')
        return '[ '+', '.join([f'{record["name"]} = "{esc(record["value"])}"' for record in inp_value])+' ]'
    elif is_diff_segment_dict(inp_value) and 'text' in inp_value:
        return sanitize_text_general(inp_value['text'])
    elif is_diff_segment_dict(inp_value) and 'parts' in inp_value:
        return sanitize_text_general(inp_value['parts'])
    elif isinstance(inp_value,list):
        return ''.join([sanitize_text_general(s) for s in inp_value])
    else:
        return f'{inp_value}'
