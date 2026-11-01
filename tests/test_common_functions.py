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


if __name__ == '__main__':
    unittest.main()
