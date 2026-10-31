import pathlib
import tempfile
import unittest

from scripts.export_rag import export
from scripts.validate import ROOT


class ExportTest(unittest.TestCase):
    def test_main_is_closed(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                export(ROOT, pathlib.Path(d) / 'main.jsonl')
            self.assertFalse((pathlib.Path(d) / 'main.jsonl').exists())

    def test_research_is_deterministic(self):
        with tempfile.TemporaryDirectory() as d:
            first, second = pathlib.Path(d) / 'a', pathlib.Path(d) / 'b'
            count = export(ROOT, first, True)
            self.assertGreater(count, 0)
            self.assertEqual(len(first.read_text(encoding='utf-8').splitlines()), count)
            export(ROOT, second, True)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertIn(b'Research export', first.read_bytes())
