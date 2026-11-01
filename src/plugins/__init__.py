# Backend enhancement plugins.
#
# Each plugin registers handlers for one or more hook points (control points)
# exposed by the renderer. The dispatcher (base.run_plugins) invokes the
# handlers, which mutate a PluginContext in place.

import re

from .base import (
    PluginContext,
    run_plugins,
    HOOK_TABLE_BEFORE,
    HOOK_ROW_BEFORE,
    HOOK_COL_BEFORE,
    HOOK_COL_AFTER,
    HOOK_ROW_AFTER,
    HOOK_TABLE_AFTER,
)
from . import (
    mdd_combine_attributes,
    diff_add_classes,
    page_wrap_tables_for_memory_saving,
    mdd_validate_labels,
)


enhancement_plugins = [
    {
        'name': 'mdd_combine_attributes',
        'description': 'Combine MDD attribute columns into the master name column',
        'enabled': True,
        'hooks': {HOOK_TABLE_BEFORE: mdd_combine_attributes.mdd_combine_attributes},
    },
    {
        'name': 'diff_add_classes',
        'description': 'Add diff CSS classes (added/removed/changed/moved) to rows and cells',
        'enabled': True,
        'hooks': {
            HOOK_ROW_BEFORE: diff_add_classes.diff_add_classes_on_row_before,
            HOOK_COL_BEFORE: diff_add_classes.diff_add_classes_on_col_before,
        },
    },
    {
        'name': 'page_wrap_tables_for_memory_saving',
        'description': 'Wrap tables so content is revealed on click (memory saving)',
        'enabled': True,
        'hooks': {HOOK_TABLE_AFTER: page_wrap_tables_for_memory_saving.page_wrap_tables_for_memory_saving},
    },
    {
        'name': 'mdd_validate_labels',
        'description': 'Validate MDD label XML and highlight issues',
        'enabled': True,
        'hooks': {HOOK_COL_AFTER: mdd_validate_labels.mdd_validate_labels},
    },
]

try:
    assert all(re.match(r'^\w[\w\-/]*\w$', plugin.get('name')) for plugin in enhancement_plugins), 'Plugins do not pass validation for plugin name, please check'
except Exception as e:
    raise Exception(f'Plugins do not pass validation for plugin name, please check: {e}') from e
