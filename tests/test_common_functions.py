"""Tests for the pure sanitization/formatting helpers in ``common_functions``."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))

import common_functions as cf


class TestSanitizeHelpers(unittest.TestCase):
    def test_normalize_linebreaks(self):
        self.assertEqual(cf.sanitize_text_normalizelinebreaks('a\r\nb\rc'), 'a\nb\nc')

    def test_html_sanitize_text_escapes(self):
        self.assertEqual(cf.html_sanitize_text('<b>&'), '&lt;b&gt;&amp;')

    def test_html_sanitize_text_newlines_to_br(self):
        self.assertEqual(cf.html_sanitize_text('a\nb'), 'a<br />b')

    def test_html_sanitize_text_treats_deprecated_markers_as_plain_text(self):
        # The old <<ADDED>>/<<REMOVED>> text markers are deprecated; they must no
        # longer be rewritten into diff spans, just HTML-escaped like normal text.
        self.assertEqual(
            cf.html_sanitize_text('<<ADDED>>x<<ENDADDED>>'),
            '&lt;&lt;ADDED&gt;&gt;x&lt;&lt;ENDADDED&gt;&gt;',
        )

    def test_sanitize_cssfield(self):
        self.assertEqual(cf.sanitize_cssfield('My Column!'), 'My-Column')

    def test_sanitize_idfield(self):
        self.assertEqual(cf.sanitize_idfield('My.Column!'), 'My.Column')

    def test_extract_filename(self):
        self.assertEqual(cf.sanitize_text_extract_filename('/a/b/c.txt'), 'c.txt')
        self.assertEqual(cf.sanitize_text_extract_filename('C:\\a\\b.txt'), 'b.txt')

    def test_is_property_list(self):
        self.assertTrue(cf.is_property_list([{'name': 'a', 'value': 1}]))
        self.assertFalse(cf.is_property_list([{'name': 'a'}]))

    def test_sanitize_text_general_text(self):
        self.assertEqual(cf.sanitize_text_general({'text': 'hello'}), 'hello')

    def test_sanitize_text_general_property_list(self):
        self.assertEqual(cf.sanitize_text_general([{'name': 'a', 'value': 'x'}]), '[ a = "x" ]')

    def test_sanitize_text_general_scalar(self):
        self.assertEqual(cf.sanitize_text_general(42), '42')


class TestRichTextValues(unittest.TestCase):
    def test_html_sanitize_raw_string(self):
        self.assertEqual(cf.html_sanitize_value_general('Item name'), 'Item name')

    def test_html_sanitize_segment_text(self):
        self.assertEqual(cf.html_sanitize_value_general({'text': 'Item name'}), 'Item name')

    def test_html_sanitize_segment_with_role(self):
        self.assertEqual(
            cf.html_sanitize_value_general({'text': 'x', 'role': 'added'}),
            '<span class="mdmdiff-inlineoverlay-added">x</span>',
        )

    def test_html_sanitize_parts_with_context_and_added(self):
        value = {'parts': [{'role': 'context', 'text': 'Item name'}, {'role': 'added', 'text': ' (updated)'}]}
        self.assertEqual(
            cf.html_sanitize_value_general(value),
            'Item name<span class="mdmdiff-inlineoverlay-added"> (updated)</span>',
        )

    def test_html_sanitize_list_of_segments(self):
        value = [{'text': 'A'}, {'text': 'B', 'role': 'removed'}]
        self.assertEqual(
            cf.html_sanitize_value_general(value),
            'A<span class="mdmdiff-inlineoverlay-removed">B</span>',
        )

    def test_sanitize_text_general_flattens_rich_text(self):
        # Exact shape the diff tool emits for a side-by-side column header.
        value = {'parts': [{'role': 'context', 'text': 'Item name'}, {'text': ' (Left file)'}]}
        self.assertEqual(cf.sanitize_text_general(value), 'Item name (Left file)')


if __name__ == '__main__':
    unittest.main()
