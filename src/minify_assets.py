
import sys # for error reporting to stderr
# import warnings



# STDOUT_COLOR_RED = "\033[91m"
STDOUT_COLOR_RED = "\033[31m"
STDOUT_COLOR_RESET = "\033[0m"
STDOUT_COLOR_GREEN = "\033[32m"




csscompressor = None
_csscompressor_import_error_warning_emitted = {'emitted':False}
try:
    import csscompressor
except ImportError:
    # print(f'{STDOUT_COLOR_RED}Can\'t import csscompressor: please install csscompressor package; CSS are not minified!{STDOUT_COLOR_RESET}',file=sys.stderr)
    csscompressor = None

jsmin = None
_rjsmin_import_error_warning_emitted = {'emitted':False}
try:
    from rjsmin import jsmin
except ImportError:
    # print(f'{STDOUT_COLOR_RED}Can\'t import rjsmin: please install rjsmin package; JS are not minified!{STDOUT_COLOR_RESET}',file=sys.stderr)
    jsmin = None


def minify_css(txt):
    if not csscompressor:
        if not _csscompressor_import_error_warning_emitted['emitted']:
            print(f'{STDOUT_COLOR_RED}Can\'t import csscompressor: please install csscompressor package; CSS are not minified!{STDOUT_COLOR_RESET}',file=sys.stderr)
            # warnings.warn(f'{STDOUT_COLOR_RED}Can\'t import csscompressor: please install csscompressor package; CSS are not minified!{STDOUT_COLOR_RESET}',ImportWarning)
            _csscompressor_import_error_warning_emitted['emitted'] = True
        return txt
    return csscompressor.compress(txt)

def minify_js(txt):
    if not jsmin:
        if not _rjsmin_import_error_warning_emitted['emitted']:
            print(f'{STDOUT_COLOR_RED}Can\'t import rjsmin: please install rjsmin package; JS are not minified!{STDOUT_COLOR_RESET}',file=sys.stderr)
            # warnings.warn(f'{STDOUT_COLOR_RED}Can\'t import rjsmin: please install rjsmin package; JS are not minified!{STDOUT_COLOR_RESET}',ImportWarning)
            _rjsmin_import_error_warning_emitted['emitted'] = True
        return txt
    return jsmin(txt)

