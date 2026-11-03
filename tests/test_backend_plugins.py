"""Tests for the backend enhancement plugins and their contract.

These run without any external runtime (no MDD/COM, no browser).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.plugins import (
    enhancement_plugins,
    run_plugins,
    PluginContext,
    HOOK_TABLE_BEFORE,
    HOOK_ROW_BEFORE,
    HOOK_COL_BEFORE,
    HOOK_COL_AFTER,
    HOOK_ROW_AFTER,
    HOOK_TABLE_AFTER,
)
from src.plugins import mdd_combine_attributes as combine_mod
from src.plugins import diff_add_classes as diff_mod
from src.plugins import page_wrap_tables_for_memory_saving as wrap_mod
from src.plugins import mdd_validate_labels as validate_mod


class TestRegistry(unittest.TestCase):
    def test_expected_names_in_order(self):
        names = [p['name'] for p in enhancement_plugins]
        self.assertEqual(names, [
            'mdd_combine_attributes',
            'diff_add_classes',
            'page_wrap_tables_for_memory_saving',
            'mdd_validate_labels',
        ])

    def test_all_plugins_have_hooks(self):
        for p in enhancement_plugins:
            self.assertTrue(p.get('enabled'))
            self.assertTrue(p.get('hooks'))


class TestDispatcher(unittest.TestCase):
    def _make_plugin(self):
        return {
            'name': 'x',
            'enabled': True,
            'hooks': {HOOK_ROW_AFTER: lambda ctx: ctx.flags.append('ran')},
        }

    def test_runs_handler(self):
        ctx = PluginContext(flags=[])
        run_plugins([self._make_plugin()], HOOK_ROW_AFTER, ctx)
        self.assertIn('ran', ctx.flags)

    def test_disable_plugin_flag_skips(self):
        ctx = PluginContext(flags=[':disable-plugin:x'])
        run_plugins([self._make_plugin()], HOOK_ROW_AFTER, ctx)
        self.assertNotIn('ran', ctx.flags)

    def test_disabled_plugin_skips(self):
        plugin = self._make_plugin()
        plugin['enabled'] = False
        ctx = PluginContext(flags=[])
        run_plugins([plugin], HOOK_ROW_AFTER, ctx)
        self.assertNotIn('ran', ctx.flags)

    def test_global_skip_flag(self):
        ctx = PluginContext(flags=['skip_plugin_enhancement'])
        run_plugins([self._make_plugin()], HOOK_ROW_AFTER, ctx)
        self.assertNotIn('ran', ctx.flags)

    def test_missing_hook_is_ignored(self):
        ctx = PluginContext(flags=[])
        run_plugins([self._make_plugin()], HOOK_ROW_BEFORE, ctx)
        self.assertNotIn('ran', ctx.flags)


class TestMddCombineAttributes(unittest.TestCase):
    def test_combines_attribute_column_into_name(self):
        rows = [
            ['name', 'attribute'],
            ['Q1', 'att1'],
        ]
        column_specs = ['name', 'attribute']
        ctx = PluginContext(flags=[], column_specs=column_specs, rows=rows)
        combine_mod.mdd_combine_attributes(ctx)
        self.assertEqual(ctx.column_specs, ['name'])
        self.assertEqual(len(ctx.rows[1]), 1)
        self.assertIn('parts', ctx.rows[1][0])

    def test_noop_without_attribute_column(self):
        rows = [['name'], ['Q1']]
        column_specs = ['name']
        ctx = PluginContext(flags=[], column_specs=column_specs, rows=rows)
        combine_mod.mdd_combine_attributes(ctx)
        self.assertEqual(ctx.column_specs, ['name'])
        self.assertEqual(ctx.rows, rows)


class TestDiffAddClasses(unittest.TestCase):
    def test_row_before_adds_added_class(self):
        row = ['add', 'x']
        column_specs = ['flagdiff', 'col']
        ctx = PluginContext(flags=[], column_specs=column_specs, row=row, other_cols_ref=row)
        diff_mod.diff_add_classes_on_row_before(ctx)
        self.assertIn('format-cssclass-mdmdiff-added', ctx.flags)

    def test_col_before_marks_changed_flagdiff(self):
        row = ['add', 'x']
        column_specs = ['flagdiff', 'col']
        ctx = PluginContext(flags=[], column_specs=column_specs, col='add', col_index=0, other_cols_ref=row)
        diff_mod.diff_add_classes_on_col_before(ctx)
        self.assertEqual(ctx.col, {'parts': ['add', ' (changed)']})


class TestPageWrapTables(unittest.TestCase):
    def test_wraps_table(self):
        html = '<div><table id="t1">x</table></div>'
        ctx = PluginContext(flags=[], column_specs=[], result_formatted=html, table_id='t1')
        wrap_mod.page_wrap_tables_for_memory_saving(ctx)
        self.assertIn('mdmreport_hidetablememorysaving_outer_t1', ctx.result_formatted)

    def test_missing_table_id_returns_unchanged(self):
        html = '<table>x</table>'
        ctx = PluginContext(flags=[], column_specs=[], result_formatted=html, table_id='')
        wrap_mod.page_wrap_tables_for_memory_saving(ctx)
        self.assertEqual(ctx.result_formatted, html)

class TestMddValidateLabels(unittest.TestCase):
    def test_valid_label_unchanged(self):
        html = '<td>Question one</td>'
        ctx = PluginContext(flags=[], column_specs=['label'], col_index=0, result_formatted=html)
        validate_mod.mdd_validate_labels(ctx)
        self.assertEqual(ctx.result_formatted, html)

    def test_xml_incompatible_label_flagged(self):
        html = '<td>a &lt; b</td>'
        ctx = PluginContext(flags=[], column_specs=['label'], col_index=0, result_formatted=html)
        validate_mod.mdd_validate_labels(ctx)
        self.assertIn('mdmrep-plgn-labelxmlerr', ctx.result_formatted)


class TestEndToEnd(unittest.TestCase):
    def _fixture(self):
        return {
            'report_type': 'MDD',
            'source_file': '/tmp/test.mdd',
            'report_datetime_utc': '2026-01-01T00:00:00Z',
            'source_file_metadata': [],
            'report_scheme': {
                'columns': ['name', 'attribute', 'label'],
                'column_headers': {'name': 'Name', 'attribute': 'Attribute', 'label': 'Label'},
                'flags': [],
            },
            'sections': [
                {
                    'name': 'Section1',
                    'title': 'Section 1',
                    'columns': ['name', 'attribute', 'label'],
                    'content': [
                        {'name': 'Q1', 'attribute': 'att1', 'label': 'Question one'},
                    ],
                }
            ],
        }

    def test_produce_html_includes_plugin_effects(self):
        from src import report_create
        html_out = report_create.produce_html(self._fixture(), config={'script_version': 'test'})
        self.assertIn('mdmreport_hidetablememorysaving_outer', html_out)
        self.assertIn('<table', html_out)

    def test_produce_html_defaults_missing_script_version_to_question_mark(self):
        from src import report_create
        # An empty config must not crash, and the version falls back to '?'.
        html_out = report_create.produce_html(self._fixture(), config={})
        self.assertIn('<html', html_out)
        self.assertIn('data-script-version="?"', html_out)

    def test_disable_plugin(self):
        from src import report_create
        html_out = report_create.produce_html(
            self._fixture(),
            config={'script_version': 'test', 'plugins_to_disable': ['page_wrap_tables_for_memory_saving']},
        )
        self.assertNotIn('mdmreport_hidetablememorysaving_outer', html_out)


if __name__ == '__main__':
    unittest.main()
