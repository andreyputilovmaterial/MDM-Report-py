
from importlib import resources

from .report_html_make_js_plugin_code import make_syntax as make_plugin_html
from .minify_assets import minify_js, minify_css





TEMPLATE_HTML_CSS_NORMALIZECSS = resources.files("src.templates").joinpath("normalize.css").read_text('utf-8')
# TEMPLATE_HTML_CSS_NORMALIZECSS = minify_css(TEMPLATE_HTML_CSS_NORMALIZECSS)

TEMPLATE_HTML_STYLES = resources.files("src.templates").joinpath("common.css").read_text('utf-8')
TEMPLATE_HTML_STYLES = minify_css(TEMPLATE_HTML_STYLES)

TEMPLATE_HTML_STYLES_TABLE = resources.files("src.templates").joinpath("mdmreporttable.css").read_text('utf-8')
TEMPLATE_HTML_STYLES_TABLE = minify_css(TEMPLATE_HTML_STYLES_TABLE)

TEMPLATE_HTML_COPYBANNER = resources.files("src.templates").joinpath("copybanner.html").read_text('utf-8')

TEMPLATE_HTML_TABLE_BEGIN = resources.files("src.templates").joinpath("table_begin.html").read_text('utf-8')

TEMPLATE_HTML_TABLE_END = resources.files("src.templates").joinpath("table_end.html").read_text('utf-8')

TEMPLATE_HTML_BEGIN = resources.files("src.templates").joinpath("html_begin.html").read_text('utf-8')

TEMPLATE_HTML_END = resources.files("src.templates").joinpath("html_end.html").read_text('utf-8')



# plugins
PLUGIN_BEAUTIFYDATES_JS = resources.files("src.templates.plugins.beautifydates").joinpath("script.js").read_text('utf-8')
PLUGIN_BEAUTIFYDATES_JS = minify_js(PLUGIN_BEAUTIFYDATES_JS)
PLUGIN_BEAUTIFYDATES_CSS = resources.files("src.templates.plugins.beautifydates").joinpath("script.css").read_text('utf-8')
PLUGIN_BEAUTIFYDATES_CSS = minify_css(PLUGIN_BEAUTIFYDATES_CSS)

# plugins
PLUGIN_ALIGNCOLWIDTHS_JS = resources.files("src.templates.plugins.aligncolwidths").joinpath("script.js").read_text('utf-8')
PLUGIN_ALIGNCOLWIDTHS_JS = minify_js(PLUGIN_ALIGNCOLWIDTHS_JS)
PLUGIN_ALIGNCOLWIDTHS_CSS = resources.files("src.templates.plugins.aligncolwidths").joinpath("script.css").read_text('utf-8')
PLUGIN_ALIGNCOLWIDTHS_CSS = minify_css(PLUGIN_ALIGNCOLWIDTHS_CSS)

# plugins
PLUGIN_EXPANDABLE_JS = resources.files("src.templates.plugins.expandable").joinpath("script.js").read_text('utf-8')
PLUGIN_EXPANDABLE_JS = minify_js(PLUGIN_EXPANDABLE_JS)
PLUGIN_EXPANDABLE_CSS = resources.files("src.templates.plugins.expandable").joinpath("script.css").read_text('utf-8')
PLUGIN_EXPANDABLE_CSS = minify_css(PLUGIN_EXPANDABLE_CSS)

# plugins
PLUGIN_SHOWHIDECOLUMNS_JS = resources.files("src.templates.plugins.showhidecolumns").joinpath("script.js").read_text('utf-8')
PLUGIN_SHOWHIDECOLUMNS_JS = minify_js(PLUGIN_SHOWHIDECOLUMNS_JS)
PLUGIN_SHOWHIDECOLUMNS_CSS = resources.files("src.templates.plugins.showhidecolumns").joinpath("script.css").read_text('utf-8')
PLUGIN_SHOWHIDECOLUMNS_CSS = minify_css(PLUGIN_SHOWHIDECOLUMNS_CSS)

# plugins
PLUGIN_JIRA_JS = resources.files("src.templates.plugins.jira").joinpath("script.js").read_text('utf-8')
PLUGIN_JIRA_JS = minify_js(PLUGIN_JIRA_JS)
PLUGIN_JIRA_CSS = resources.files("src.templates.plugins.jira").joinpath("script.css").read_text('utf-8')
PLUGIN_JIRA_CSS = minify_css(PLUGIN_JIRA_CSS)

# plugins
PLUGIN_COLUMNFILTERING_JS = resources.files("src.templates.plugins.columnfiltering").joinpath("script.js").read_text('utf-8')
PLUGIN_COLUMNFILTERING_JS = minify_js(PLUGIN_COLUMNFILTERING_JS)
PLUGIN_COLUMNFILTERING_CSS = resources.files("src.templates.plugins.columnfiltering").joinpath("script.css").read_text('utf-8')
PLUGIN_COLUMNFILTERING_CSS = minify_css(PLUGIN_COLUMNFILTERING_CSS)

# plugins
PLUGIN_SHOWHIDESECTIONS_JS = resources.files("src.templates.plugins.showhidesections").joinpath("script.js").read_text('utf-8')
PLUGIN_SHOWHIDESECTIONS_JS = minify_js(PLUGIN_SHOWHIDESECTIONS_JS)
PLUGIN_SHOWHIDESECTIONS_CSS = resources.files("src.templates.plugins.showhidesections").joinpath("script.css").read_text('utf-8')
PLUGIN_SHOWHIDESECTIONS_CSS = minify_css(PLUGIN_SHOWHIDESECTIONS_CSS)

# plugins
PLUGIN_FORMATPREOUTPUTS_JS = resources.files("src.templates.plugins.format_pre_outputs").joinpath("script.js").read_text('utf-8')
PLUGIN_FORMATPREOUTPUTS_JS = minify_js(PLUGIN_FORMATPREOUTPUTS_JS)
PLUGIN_FORMATPREOUTPUTS_CSS = resources.files("src.templates.plugins.format_pre_outputs").joinpath("script.css").read_text('utf-8')
PLUGIN_FORMATPREOUTPUTS_CSS = minify_css(PLUGIN_FORMATPREOUTPUTS_CSS)

# plugins
PLUGIN_VALIDATEMDDLABELISSUES_JS = resources.files("src.templates.plugins.validatemddlabelissues").joinpath("script.js").read_text('utf-8')
PLUGIN_VALIDATEMDDLABELISSUES_JS = minify_js(PLUGIN_VALIDATEMDDLABELISSUES_JS)
PLUGIN_VALIDATEMDDLABELISSUES_CSS = resources.files("src.templates.plugins.validatemddlabelissues").joinpath("script.css").read_text('utf-8')
PLUGIN_VALIDATEMDDLABELISSUES_CSS = minify_css(PLUGIN_VALIDATEMDDLABELISSUES_CSS)

# plugins
PLUGIN_DIFFONDIFFSHOWALLROWS_JS = resources.files("src.templates.plugins.diffondiffshowallrows").joinpath("script.js").read_text('utf-8')
PLUGIN_DIFFONDIFFSHOWALLROWS_JS = minify_js(PLUGIN_DIFFONDIFFSHOWALLROWS_JS)
PLUGIN_DIFFONDIFFSHOWALLROWS_CSS = resources.files("src.templates.plugins.diffondiffshowallrows").joinpath("script.css").read_text('utf-8')
PLUGIN_DIFFONDIFFSHOWALLROWS_CSS = minify_css(PLUGIN_DIFFONDIFFSHOWALLROWS_CSS)



# plugin common code (launcher)
PLUGINS_COMMON_JS = resources.files("src.templates").joinpath("common.js").read_text('utf-8')
PLUGINS_COMMON_JS = minify_js(PLUGINS_COMMON_JS)



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
        'name': 'formatpreoutputs',
        'description': 'Splitting pre outputs into individual lines with detailed css classes and control elements to switch to next and prev',
        'css': PLUGIN_FORMATPREOUTPUTS_CSS,
        'js': PLUGIN_FORMATPREOUTPUTS_JS,
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


TEMPLATE_HTML_SCRIPTS = ''.join([
    make_plugin_html(plugin) for plugin in plugins
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
    
