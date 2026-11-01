# Plugin contract and dispatcher.
#
# A "control point" is a named hook in the renderer (report_create.py) where a
# plugin may attach. Plugins are registered in plugins/__init__.py and mutate a
# PluginContext in place; they return nothing.

# Hook points (control points) exposed by the renderer.
HOOK_TABLE_BEFORE = 'on_table_before'
HOOK_ROW_BEFORE = 'on_row_before'
HOOK_COL_BEFORE = 'on_col_before'
HOOK_COL_AFTER = 'on_col_after'
HOOK_ROW_AFTER = 'on_row_after'
HOOK_TABLE_AFTER = 'on_table_after'

HOOK_POINTS = (
    HOOK_TABLE_BEFORE,
    HOOK_ROW_BEFORE,
    HOOK_COL_BEFORE,
    HOOK_COL_AFTER,
    HOOK_ROW_AFTER,
    HOOK_TABLE_AFTER,
)


class PluginContext:
    """Mutable state passed through the plugin hooks at one control point.

    Fields (populated per hook; unset fields are None):

        flags            list   active flags (incl. 'skip_plugin_enhancement' and ':disable-plugin:<name>')
        column_specs     list   column ids for the current table
        rows             list   table rows (table hooks)
        table_id         str    current table id (table hooks)
        row              list   current row (row/col hooks)
        other_cols_ref   list   reference to the whole current row (row/col hooks)
        col              any    current cell data (col hooks)
        col_index        int    current column index (col hooks)
        result_formatted str    rendered HTML (after hooks)
    """

    def __init__(self, flags=None, column_specs=None, **kwargs):
        self.flags = list(flags or [])
        self.column_specs = list(column_specs or [])
        self.rows = kwargs.get('rows')
        self.table_id = kwargs.get('table_id')
        self.row = kwargs.get('row')
        self.other_cols_ref = kwargs.get('other_cols_ref')
        self.col = kwargs.get('col')
        self.col_index = kwargs.get('col_index')
        self.result_formatted = kwargs.get('result_formatted')


def run_plugins(plugins, hook, ctx):
    """Run every enabled plugin that registers ``hook``, in registration order.

    Each handler mutates ``ctx`` in place and returns nothing. A plugin is
    skipped when the global 'skip_plugin_enhancement' flag is set, when it is
    disabled, or when ':disable-plugin:<name>' is present in ctx.flags.
    """
    if 'skip_plugin_enhancement' in ctx.flags:
        return ctx
    for plugin in plugins:
        if not plugin.get('enabled'):
            continue
        if f':disable-plugin:{plugin["name"]}' in ctx.flags:
            continue
        handler = plugin.get('hooks', {}).get(hook)
        if handler is not None:
            handler(ctx)
    return ctx
