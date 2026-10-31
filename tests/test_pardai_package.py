import datetime as dt
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.prepare_pardai import prepare, write_package


class PardaiPackageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'docs/01-radio-fundamentals').mkdir(parents=True)
        (self.root / 'registries').mkdir()
        (self.root / 'reports').mkdir()
        (self.root / 'sources.yaml').write_text('sources:\n  - id: sample\n', encoding='utf-8')
        (self.root / 'registries/formulas.yaml').write_text('{"formulas": []}', encoding='utf-8')
        self.today = dt.date(2026, 10, 31)
        self.meta = {'schema_version': 1, 'id': 'sample-article', 'title': '1.1 Тест', 'language': 'ru',
                     'section': '01-radio-fundamentals', 'type': 'concept', 'summary': 'Тест.', 'tags': ['rf'],
                     'aliases': [], 'status': 'verified', 'created_at': '2026-10-01', 'updated_at': '2026-10-01',
                     'reviewed_at': '2026-10-01', 'review_due': None,
                     'verification': {'sources': 'passed', 'formulas': 'not_applicable', 'technical_review': 'passed',
                                      'review_record': 'reports/review.json'},
                     'rag': {'include': True}, 'related': [], 'sources': ['sample'], 'formula_ids': []}
        self.path = self.root / 'docs/01-radio-fundamentals/article.md'
        self.save()
        (self.path.parent / 'index.md').write_text('# Навигация\n', encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def save(self, body='# 1.1 Тест\n\n## Раздел\nДанные.\n'):
        raw = ('---\n' + json.dumps(self.meta, ensure_ascii=False) + '\n---\n' + body).encode('utf-8')
        self.path.write_bytes(raw)
        review = {'reviewer': 'Test reviewer', 'date': '2026-10-01', 'documents': {
            self.meta['id']: {'sha256': hashlib.sha256(raw).hexdigest(), 'decision': 'approved'}}}
        (self.root / 'reports/review.json').write_text(json.dumps(review), encoding='utf-8')

    def test_approved_article_is_exact_and_index_excluded(self):
        manifest, files = prepare(self.root, self.today)
        self.assertEqual(list(files), ['articles/sample-article.md'])
        self.assertEqual(files['articles/sample-article.md'], self.path.read_bytes())
        self.assertEqual(manifest['documents'][0]['metadata']['tags'], ['rf'])
        self.assertEqual(manifest['documents'][0]['external_id'], 'sample-article')
        dest = write_package(self.root / 'build', manifest, files)
        self.assertEqual(dest, write_package(self.root / 'build', manifest, files))
        self.assertEqual((dest / 'articles/sample-article.md').read_bytes(), self.path.read_bytes())

    def test_existing_package_with_extra_file_is_rejected(self):
        manifest, files = prepare(self.root, self.today)
        dest = write_package(self.root / 'build', manifest, files)
        (dest / 'articles/index.md').write_text('# injected', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'unexpected file'):
            write_package(self.root / 'build', manifest, files)

    def test_draft_disabled_and_expired_are_not_admitted(self):
        self.meta['rag']['include'] = False
        self.save()
        self.assertEqual(prepare(self.root, self.today)[1], {})
        self.meta['status'] = 'draft'
        self.save()
        self.assertEqual(prepare(self.root, self.today)[1], {})
        research, files = prepare(self.root, self.today, research=True)
        self.assertEqual(len(files), 1)
        self.assertEqual(research['config']['mode'], 'research')
        self.meta['status'] = 'verified'
        self.meta['rag']['include'] = True
        self.meta['review_due'] = '2026-10-30'
        self.save()
        self.assertEqual(prepare(self.root, self.today)[1], {})

    def test_rename_modify_delete_and_registry_change(self):
        old, _ = prepare(self.root, self.today)
        self.path = self.path.rename(self.path.with_name('renamed.md'))
        renamed, _ = prepare(self.root, self.today, previous=old)
        self.assertEqual(renamed['changes']['renamed'], ['sample-article'])
        self.assertEqual(renamed['changes']['changed'], [])
        self.save('# 1.1 Тест\n\n## Раздел\nНовые данные.\n')
        updated, _ = prepare(self.root, self.today, previous=renamed)
        self.assertEqual(updated['changes']['changed'], ['sample-article'])
        (self.root / 'sources.yaml').write_text('sources:\n  - id: sample\n# changed\n', encoding='utf-8')
        registry, _ = prepare(self.root, self.today, previous=updated)
        self.assertTrue(registry['changes']['registries_changed'])
        self.assertEqual(registry['changes']['changed'], ['sample-article'])
        self.path.unlink()
        removed, _ = prepare(self.root, self.today, previous=registry)
        self.assertEqual(removed['changes']['removed'], ['sample-article'])

    def test_main_rejects_research_baseline(self):
        prior, _ = prepare(self.root, self.today, research=True)
        with self.assertRaises(ValueError):
            prepare(self.root, self.today, previous=prior)

    def test_review_hash_and_heading_are_required(self):
        with self.path.open('a', encoding='utf-8') as f:
            f.write('Changed after review')
        with self.assertRaises(ValueError):
            prepare(self.root, self.today)
        self.save('# Wrong heading\n')
        with self.assertRaises(ValueError):
            prepare(self.root, self.today)

    def test_standard_requires_scope_and_review_due(self):
        self.meta['type'] = 'standard'
        self.save()
        with self.assertRaises(ValueError):
            prepare(self.root, self.today)
        self.meta.update(jurisdiction='RU', standard_id='test-1')
        self.save()
        self.assertEqual(prepare(self.root, self.today)[1], {})
        self.meta['review_due'] = '2026-12-31'
        self.save()
        self.assertEqual(len(prepare(self.root, self.today)[1]), 1)

    def test_duplicate_front_matter_key_is_error(self):
        self.path.write_text('---\n{"id":"a","id":"b"}\n---\n# Test\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'duplicate metadata key'):
            prepare(self.root, self.today)
