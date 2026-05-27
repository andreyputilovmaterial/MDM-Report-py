from importlib import resources


from src import report_html_template as tmpl

from datetime import datetime

def sanitize(s):
    return s.replace(r'"""',r'\"""')


dt = datetime.now()


OUTPUT_PATH = resources.files('src').joinpath('GENERATED','TEMPLATE.py')
OUTPUT_PATH_PACKAGE = resources.files('src').joinpath('GENERATED','__init__.py')

# create the directory first
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

# create the __init__.py
with OUTPUT_PATH_PACKAGE.open('w', encoding='utf-8') as f:
    f.write('\n\n')

with OUTPUT_PATH.open('w', encoding='utf-8') as f:
    f.write('\n\n')
    f.write(f'# AUTO-GENERATED\n# {dt}\n\n')
    f.write('TEMPLATE_HTML_BEGIN = r"""\n'+sanitize(tmpl.TEMPLATE_HTML_BEGIN)+'\n"""\n\n')
    f.write('TEMPLATE_HTML_END = r"""\n'+sanitize(tmpl.TEMPLATE_HTML_END)+'\n"""\n\n')
    f.write('TEMPLATE_HTML_TABLE_BEGIN = r"""\n'+sanitize(tmpl.TEMPLATE_HTML_TABLE_BEGIN)+'\n"""\n\n')
    f.write('TEMPLATE_HTML_TABLE_END = r"""\n'+sanitize(tmpl.TEMPLATE_HTML_TABLE_END)+'\n"""\n\n')

