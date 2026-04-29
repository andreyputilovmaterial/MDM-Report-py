from importlib import resources


from src import report_html_template as tmpl



def sanitize(s):
    return s.replace(r'"""',r'\"""')


OUTPUT_PATH = resources.files('src').joinpath('TEMPLATE_COMPILED','TEMPLATE.py')

with OUTPUT_PATH.open('w', encoding='utf-8') as f:
    f.write('\n\n')
    f.write('TEMPLATE_HTML_BEGIN = r"""\n'+sanitize(tmpl.TEMPLATE_HTML_BEGIN)+'\n"""\n\n')
    f.write('TEMPLATE_HTML_END = r"""\n'+sanitize(tmpl.TEMPLATE_HTML_END)+'\n"""\n\n')
    f.write('TEMPLATE_HTML_TABLE_BEGIN = r"""\n'+sanitize(tmpl.TEMPLATE_HTML_TABLE_BEGIN)+'\n"""\n\n')
    f.write('TEMPLATE_HTML_TABLE_END = r"""\n'+sanitize(tmpl.TEMPLATE_HTML_TABLE_END)+'\n"""\n\n')

