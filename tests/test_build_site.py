"""Проверки сборки обзорного HTML-сайта."""
import pathlib
import tempfile
import unittest

from scripts.build_site import build, parse_plan
from scripts.markdown_html import markdown_to_html, rewrite_md_href
from scripts.validate import ROOT


class MarkdownTest(unittest.TestCase):
    def test_basic_formatting(self):
        html = markdown_to_html('# Title\n\nParagraph with **bold** and `code`.\n')
        self.assertIn('<h1>Title</h1>', html)
        self.assertIn('<strong>bold</strong>', html)
        self.assertIn('<code>code</code>', html)

    def test_table_and_link_rewrite(self):
        md = '| A | B |\n|---|---|\n| 1 | [x](foo.md) |\n'
        html = markdown_to_html(md)
        self.assertIn('<table>', html)
        self.assertIn('href="foo.html"', html)
        self.assertEqual(rewrite_md_href('../02-wave-propagation/index.md'),
                         '../02-wave-propagation/index.html')


class SiteBuildTest(unittest.TestCase):
    def test_plan_has_sixty_six(self):
        self.assertEqual(len(parse_plan(ROOT)), 66)

    def test_build_creates_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / 'site'
            count = build(ROOT, out, base_url='/uav-radio-kb')
            self.assertGreaterEqual(count, 20)
            index = (out / 'index.html').read_text(encoding='utf-8')
            self.assertIn('/uav-radio-kb/assets/site.css', index)
            self.assertIn('/uav-radio-kb/01-radio-fundamentals/index.html', index)
            article = out / '01-radio-fundamentals' / 'frequency-wavelength.html'
            self.assertTrue(article.is_file())
            text = article.read_text(encoding='utf-8')
            self.assertIn('проверено', text)
            self.assertIn('Частота и длина волны', text)
            self.assertTrue((out / '.nojekyll').is_file())
            self.assertTrue((out / 'plan.html').is_file())
            empty = (out / '06-video-links' / 'index.html').read_text(encoding='utf-8')
            self.assertIn('пока нет подготовленных статей', empty)


if __name__ == '__main__':
    unittest.main()
