import json
import pathlib
import shutil
import tempfile
import unittest

from scripts.validate import ROOT, validate


class ValidationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        for name in ('docs', 'registries', 'reports'):
            shutil.copytree(ROOT / name, self.root / name)
        shutil.copy(ROOT / 'sources.yaml', self.root)
        self.path = self.root / 'docs/01-radio-fundamentals/frequency-wavelength.md'

    def tearDown(self):
        self.temp.cleanup()

    def change(self, field, value):
        text = self.path.read_text(encoding='utf-8')
        _, header, body = text.split('---\n', 2)
        data = json.loads(header)
        data[field] = value
        self.path.write_text('---\n' + json.dumps(data, ensure_ascii=False) + '\n---\n' + body, encoding='utf-8')

    def test_current_articles(self):
        self.assertEqual(validate(self.root), [])

    def test_unknown_source(self):
        self.change('sources', ['not-a-source'])
        self.assertTrue(any('unknown source' in e for e in validate(self.root)))

    def test_invalid_date(self):
        self.change('updated_at', '2026-02-30')
        self.assertTrue(validate(self.root))

    def test_draft_cannot_be_included(self):
        self.change('status', 'draft')
        self.change('rag', {'include': True})
        self.assertTrue(any('unverified' in e for e in validate(self.root)))

    def test_duplicate_id(self):
        self.change('id', 'calc-wavelength-example')
        self.assertTrue(any('duplicate id' in e for e in validate(self.root)))

    def test_changed_article_invalidates_review(self):
        with self.path.open('a', encoding='utf-8') as stream:
            stream.write('\nChanged after review.\n')
        self.assertTrue(any('review does not match' in e for e in validate(self.root)))
