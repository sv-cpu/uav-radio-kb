"""Research-only whole-document export; main export deliberately fails closed."""
import argparse
import hashlib
import json
import pathlib
import sys

from scripts.validate import ROOT, read_article, validate


def export(root, output, research=False):
    errors = validate(root)
    if errors:
        raise ValueError('\n'.join(errors))
    if not research:
        raise ValueError('Main export is unavailable until review-record validation and chunk schema are implemented')
    records = []
    for path in sorted((root / 'docs').rglob('*.md')):
        if path.name == 'index.md':
            continue
        meta, body = read_article(path)
        if meta['status'] == 'deprecated':
            continue
        record = {'schema_version': 1, 'document_id': meta['id'], 'chunk_id': meta['id'] + ':whole',
                  'title': meta['title'], 'section': meta['section'], 'language': meta['language'],
                  'type': meta['type'], 'text': body, 'tags': meta['tags'], 'source_ids': meta['sources'],
                  'formula_ids': meta['formula_ids'], 'status': meta['status'], 'verification': meta['verification'],
                  'updated_at': meta['updated_at'], 'repository_path': path.relative_to(root).as_posix(),
                  'content_hash': hashlib.sha256(body.encode('utf-8')).hexdigest(),
                  'warning': 'Research export: content is not verified; do not use as main RAG corpus.'}
        records.append(json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(',', ':')))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(''.join(line + '\n' for line in records), encoding='utf-8', newline='\n')
    return len(records)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--research', action='store_true')
    parser.add_argument('--output', type=pathlib.Path, default=ROOT / 'build/research.jsonl')
    args = parser.parse_args()
    try:
        count = export(ROOT, args.output, args.research)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f'Exported {count} research documents to {args.output}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
