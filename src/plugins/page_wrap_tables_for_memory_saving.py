# Page-level enhancement (any report): wrap tables so content is revealed on click.

import re
import json


def page_wrap_tables_for_memory_saving(ctx):
    result_formatted = ctx.result_formatted
    table_id = ctx.table_id
    try:
        TEMPLATE = r"""
<table class="mdmreport-table mdmreport-table-dummy mdmreport-table-preloaded-hidden-content" id="mdmreport_hidetablememorysaving_outer_{{ID}}"><tbody><tr></tr><tr class="mdmreport-record"><td class="mdmreport-contentcell mdmreport-contentcell-fullwidth">{{CONTENT}}</td></tr></tbody></table>
"""
        TEMPLATE_SCRIPT = r"""
<a href="#!" id="mdmreport_hidetablememorysaving_link_{{ID}}" class="mdmreport-memorysaving-hidetab-link" >Click to load contents</a>
<script>
(function(){
    var data = {{DATA}};
    const wrapperId = 'mdmreport_hidetablememorysaving_outer_{{ID}}';
    const linkId = 'mdmreport_hidetablememorysaving_link_{{ID}}';
    const wrapperEl = document.getElementById(wrapperId);
    const linkEl = document.getElementById(linkId);
    linkEl.addEventListener('click',function(event){
        data = data;
        /*  wrapperEl.innerHTML = data; */
        const el = document.createElement('div');
        el.innerHTML = data;
        wrapperEl.replaceWith(el);
        data = null;
        if(!!window.mdmreportMemorySavingPluginTriggerEvents) Promise.resolve().then(window.mdmreportMemorySavingPluginTriggerEvents)
        event.preventDefault();
        return false;
    });
})()
</script>
"""
        if not table_id:
            raise ValueError('table id not provided!')
        pattern_beginning = re.match(r'^(.*?)(<\s*?table\b)(.*)$', result_formatted, flags=re.I|re.M|re.DOTALL)
        pattern_ending = re.match(r'^(.*)(<\s*?/\s*?table\s*?>)(.*?)$', result_formatted, flags=re.I|re.M|re.DOTALL)
        if not pattern_beginning or not pattern_ending:
            raise AttributeError('pattern not found: <table> ... </table>')
        pattern_beginning = pattern_beginning.start(2)
        pattern_ending = pattern_ending.start(2) + len(pattern_ending.group(2))
        part_beginning = result_formatted[0:pattern_beginning]
        part_body = result_formatted[pattern_beginning:pattern_ending]
        part_ending = result_formatted[pattern_ending:]
        part_body_encoded = TEMPLATE.replace('{{CONTENT}}', TEMPLATE_SCRIPT).replace('{{ID}}', table_id).replace('{{DATA}}', json.dumps(part_body))
        result_formatted_upd = '' + part_beginning + part_body_encoded + part_ending
        ctx.result_formatted = result_formatted_upd
    except Exception as e:
        print('Error: HTML Report: failed when converting tables to collapsible to elaborate on memory saving: {e}'.format(e=e))
        ctx.result_formatted = result_formatted
