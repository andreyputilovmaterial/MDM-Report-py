"""Validate the committed example inputs/outputs of ``mdmreportpy``.

``tests/fixtures/*.mdd.json`` are example *inputs* (from ``mdmreadpy`` or the diff
tool); the matching ``*.mdd.html`` are the example *outputs* of this package. These
tests re-render each input through ``produce_html`` (a pure function; no Windows/COM
or browser needed) and check a self-contained page comes out.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import report_create  # noqa: E402

FIXTURES = ROOT / 'tests' / 'fixtures'

INPUTS = [
    'a1_v1.mdd.json',
    'a1_v2.mdd.json',
    'b1_today.mdd.json',
    'b1_tomorrow.mdd.json',
    'report.diff.a1_-v1-v2-.mdd.json',
    'report.diff.b1_-today-tomorrow-.mdd.json',
    'report.diff.report.diff.-a1_-b1_---v1-today---v2-tomorrow--.mdd.json',
]


def _html_name(json_name):
    return json_name[: -len('.json')] + '.html'


class TestReportExampleFixtures(unittest.TestCase):
    def test_every_input_has_a_matching_output(self):
        for name in INPUTS:
            self.assertTrue((FIXTURES / name).is_file(), name)
            self.assertTrue(
                (FIXTURES / _html_name(name)).is_file(), _html_name(name)
            )

    def test_every_input_renders_a_self_contained_html_page(self):
        for name in INPUTS:
            with self.subTest(name=name):
                report = json.loads((FIXTURES / name).read_text(encoding='utf-8'))
                html = report_create.produce_html(report, {'script_version': 'test'})
                self.assertIsInstance(html, str)
                self.assertIn('<html', html)
                self.assertIn('</html>', html)
                # The report always tags itself with a data-type CSS class.
                self.assertIn('mdmreportpage-type-', html)


if __name__ == '__main__':
    unittest.main()
