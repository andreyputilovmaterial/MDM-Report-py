
from importlib import resources

from .report_html_make_js_plugin_code import make_syntax as make_plugin_html





TEMPLATE_HTML_CSS_NORMALIZECSS = resources.files("src.templates").joinpath("normalize.css").read_text()

TEMPLATE_HTML_STYLES = resources.files("src.templates").joinpath("common.css").read_text()

TEMPLATE_HTML_STYLES_TABLE = resources.files("src.templates").joinpath("mdmreporttable.css").read_text()

TEMPLATE_HTML_COPYBANNER = resources.files("src.templates").joinpath("copybanner.html").read_text()

TEMPLATE_HTML_TABLE_BEGIN = resources.files("src.templates").joinpath("table_begin.html").read_text()

TEMPLATE_HTML_TABLE_END = resources.files("src.templates").joinpath("table_end.html").read_text()

TEMPLATE_HTML_BEGIN = resources.files("src.templates").joinpath("html_begin.html").read_text()

TEMPLATE_HTML_END = resources.files("src.templates").joinpath("html_end.html").read_text()



# plugins
PLUGIN_BEAUTIFYDATES_JS = resources.files("src.templates.plugins.beautifydates").joinpath("script.js").read_text()
PLUGIN_BEAUTIFYDATES_CSS = resources.files("src.templates.plugins.beautifydates").joinpath("script.css").read_text()

# plugins
PLUGIN_ALIGNCOLWIDTHS_JS = resources.files("src.templates.plugins.aligncolwidths").joinpath("script.js").read_text()
PLUGIN_ALIGNCOLWIDTHS_CSS = resources.files("src.templates.plugins.aligncolwidths").joinpath("script.css").read_text()

# plugins
PLUGIN_EXPANDABLE_JS = resources.files("src.templates.plugins.expandable").joinpath("script.js").read_text()
PLUGIN_EXPANDABLE_CSS = resources.files("src.templates.plugins.expandable").joinpath("script.css").read_text()

# plugins
PLUGIN_SHOWHIDECOLUMNS_JS = resources.files("src.templates.plugins.showhidecolumns").joinpath("script.js").read_text()
PLUGIN_SHOWHIDECOLUMNS_CSS = resources.files("src.templates.plugins.showhidecolumns").joinpath("script.css").read_text()

# # plugins
# PLUGIN_MEMORYSAVINGS_JS = resources.files("src.templates.plugins.memorysavings").joinpath("script.js").read_text()
# PLUGIN_MEMORYSAVINGS_CSS = resources.files("src.templates.plugins.memorysavings").joinpath("script.css").read_text()

# plugins
PLUGIN_JIRA_JS = resources.files("src.templates.plugins.jira").joinpath("script.js").read_text()
PLUGIN_JIRA_CSS = resources.files("src.templates.plugins.jira").joinpath("script.css").read_text()

# plugins
PLUGIN_COLUMNFILTERING_JS = resources.files("src.templates.plugins.columnfiltering").joinpath("script.js").read_text()
PLUGIN_COLUMNFILTERING_CSS = resources.files("src.templates.plugins.columnfiltering").joinpath("script.css").read_text()

# plugins
PLUGIN_SHOWHIDESECTIONS_JS = resources.files("src.templates.plugins.showhidesections").joinpath("script.js").read_text()
PLUGIN_SHOWHIDESECTIONS_CSS = resources.files("src.templates.plugins.showhidesections").joinpath("script.css").read_text()

# plugins
PLUGIN_COLORDIFFROWS_JS = resources.files("src.templates.plugins.colordiffrows").joinpath("script.js").read_text()
PLUGIN_COLORDIFFROWS_CSS = resources.files("src.templates.plugins.colordiffrows").joinpath("script.css").read_text()

# plugins
PLUGIN_VALIDATEMDDLABELISSUES_JS = resources.files("src.templates.plugins.validatemddlabelissues").joinpath("script.js").read_text()
PLUGIN_VALIDATEMDDLABELISSUES_CSS = resources.files("src.templates.plugins.validatemddlabelissues").joinpath("script.css").read_text()

# plugins
PLUGIN_DIFFONDIFFSHOWALLROWS_JS = resources.files("src.templates.plugins.diffondiffshowallrows").joinpath("script.js").read_text()
PLUGIN_DIFFONDIFFSHOWALLROWS_CSS = resources.files("src.templates.plugins.diffondiffshowallrows").joinpath("script.css").read_text()



# plugin common code (launcher)
PLUGINS_COMMON_JS = resources.files("src.templates").joinpath("common.js").read_text()



# plugins
plugins = [
    {
        'name': 'beaufitydates',
        'description': 'Format dates',
        'css': PLUGIN_BEAUTIFYDATES_CSS,
        'js': PLUGIN_BEAUTIFYDATES_JS,
    },
    {
        'name': 'aligncolwidths',
        'description': 'Try to calculate better col widths and adjust',
        'css': PLUGIN_ALIGNCOLWIDTHS_CSS,
        'js': PLUGIN_ALIGNCOLWIDTHS_JS,
    },
    {
        'name': 'expandable',
        'description': 'Expandable blocks, usually in "context" diff segments',
        'css': PLUGIN_EXPANDABLE_CSS,
        'js': PLUGIN_EXPANDABLE_JS,
    },
    {
        'name': 'showhidecolumns',
        'description': 'Show/hide columns',
        'css': PLUGIN_SHOWHIDECOLUMNS_CSS,
        'js': PLUGIN_SHOWHIDECOLUMNS_JS,
    },
    # {
    #     'name': 'memorysavings',
    #     'description': 'Auto-click on hidden sections to reveal; sections were previously hidden to reduce piece loaded into memory',
    #     'css': PLUGIN_MEMORYSAVINGS_CSS,
    #     'js': PLUGIN_MEMORYSAVINGS_JS,
    # },
    {
        'name': 'jira',
        'description': 'Jira - related ticket lookup',
        'css': PLUGIN_JIRA_CSS,
        'js': PLUGIN_JIRA_JS,
    },
    {
        'name': 'columnfiltering',
        'description': 'Those check boxes to toggle columns',
        'css': PLUGIN_COLUMNFILTERING_CSS,
        'js': PLUGIN_COLUMNFILTERING_JS,
    },
    {
        'name': 'showhidesections',
        'description': 'TOC - functionality to show/hide sections by clicking in TOC',
        'css': PLUGIN_SHOWHIDESECTIONS_CSS,
        'js': PLUGIN_SHOWHIDESECTIONS_JS,
    },
    {
        'name': 'colordiffrows',
        'description': 'Add css styles to rows',
        'css': PLUGIN_COLORDIFFROWS_CSS,
        'js': PLUGIN_COLORDIFFROWS_JS,
    },
    {
        'name': 'validatemddlabelissues',
        'description': 'Validate MDD label issues, that are in fact xml parsing issues - just helping to highlight problematic rows',
        'css': PLUGIN_VALIDATEMDDLABELISSUES_CSS,
        'js': PLUGIN_VALIDATEMDDLABELISSUES_JS,
    },
    {
        'name': 'diffondiffshowallrows',
        'description': 'Helper switch that allows to show all rows in "diff on diff" mode',
        'css': PLUGIN_DIFFONDIFFSHOWALLROWS_CSS,
        'js': PLUGIN_DIFFONDIFFSHOWALLROWS_JS,
    },
    
    {
        'name': 'common',
        'description': 'Common code (launcher)',
        'css': '',
        'js': PLUGINS_COMMON_JS,
    },
]


TEMPLATE_HTML_SCRIPTS = ''.join([make_plugin_html(plugin) for plugin in plugins
])




TEMPLATE_HTML_BEGIN = TEMPLATE_HTML_BEGIN.replace(
        '{{ADD_ASSETS}}', f'{TEMPLATE_HTML_SCRIPTS}'
    ).replace(
        '{{TEMPLATE_HTML_CSS_NORMALIZECSS}}', f'<style>{TEMPLATE_HTML_CSS_NORMALIZECSS}</style>'
    ).replace(
        '{{TEMPLATE_HTML_STYLES}}', f'<style>{TEMPLATE_HTML_STYLES}</style>'
    ).replace(
        '{{TEMPLATE_HTML_STYLES_TABLE}}', f'<style>{TEMPLATE_HTML_STYLES_TABLE}</style>'
    )


TEMPLATE_HTML_END = TEMPLATE_HTML_END.replace(
        '{{TEMPLATE_HTML_COPYBANNER}}', TEMPLATE_HTML_COPYBANNER
    )
    
