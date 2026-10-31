"""Начальная проверка метаданных. JSON front matter является подмножеством YAML 1.2."""
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TYPES = {'concept', 'procedure', 'calculation', 'reference', 'standard', 'equipment', 'field_case'}
STATUSES = {'draft', 'needs_review', 'verified', 'deprecated'}
SECTIONS = {'01-radio-fundamentals', '02-wave-propagation', '03-antennas', '04-radio-hardware', '05-control-links', '06-video-links', '07-telemetry', '08-calculations', '09-diagnostics', '10-interference', '11-standards', '12-field-cases', '13-equipment'}
REQUIRED = {'schema_version', 'id', 'title', 'language', 'section', 'type', 'summary', 'tags', 'aliases', 'status', 'created_at', 'updated_at', 'reviewed_at', 'review_due', 'verification', 'rag', 'related', 'sources', 'formula_ids'}


def read_article(path):
    raw = path.read_text(encoding='utf-8')
    parts = raw.split('---\n', 2)
    if len(parts) != 3 or parts[0] != '':
        raise ValueError('missing front matter delimiters')
    meta = json.loads(parts[1])
    if not isinstance(meta, dict):
        raise ValueError('front matter must be an object')
    return meta, parts[2].strip()


def validate(root=ROOT):
    errors, ids = [], set()
    source_text = (root / 'sources.yaml').read_text(encoding='utf-8')
    source_ids = set(re.findall(r'^\s*- id:\s*([\w-]+)\s*$', source_text, re.M))
    formula_data = json.loads((root / 'registries/formulas.yaml').read_text(encoding='utf-8'))
    formula_ids = {f['formula_id'] for f in formula_data['formulas']}
    for path in sorted((root / 'docs').rglob('*.md')):
        if path.name == 'index.md':
            continue
        try:
            meta, body = read_article(path)
            missing = REQUIRED - meta.keys()
            if missing:
                raise ValueError('missing fields: ' + ', '.join(sorted(missing)))
            identifier = meta['id']
            if not isinstance(identifier, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', identifier):
                raise ValueError('invalid id')
            if identifier in ids:
                raise ValueError('duplicate id: ' + identifier)
            ids.add(identifier)
            if meta['schema_version'] != 1 or meta['language'] != 'ru' or meta['type'] not in TYPES or meta['status'] not in STATUSES:
                raise ValueError('invalid schema version, language, type or status')
            if meta['section'] not in SECTIONS or path.parent.name != meta['section']:
                raise ValueError('invalid section or path')
            for field in ('title', 'summary'):
                if not isinstance(meta[field], str) or not meta[field].strip():
                    raise ValueError('empty ' + field)
            for field in ('tags', 'aliases', 'related', 'sources', 'formula_ids'):
                if not isinstance(meta[field], list) or not all(isinstance(x, str) and x for x in meta[field]):
                    raise ValueError('invalid ' + field)
            for field in ('created_at', 'updated_at', 'reviewed_at', 'review_due'):
                value = meta[field]
                if value is None and field in ('reviewed_at', 'review_due'):
                    continue
                if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                    raise ValueError('invalid date: ' + field)
                dt.date.fromisoformat(value)
            if not set(meta['sources']) <= source_ids:
                raise ValueError('unknown source')
            if not set(meta['formula_ids']) <= formula_ids:
                raise ValueError('unknown formula')
            verification, rag = meta['verification'], meta['rag']
            if not isinstance(verification, dict) or not isinstance(rag, dict) or type(rag.get('include')) is not bool:
                raise ValueError('invalid verification or rag')
            if rag['include'] and meta['status'] != 'verified':
                raise ValueError('unverified material cannot enter main RAG')
            if meta['status'] == 'verified':
                if any(verification.get(key) != 'passed' for key in ('sources', 'technical_review')):
                    raise ValueError('verified material requires passed checks')
                expected_formula_status = 'passed' if meta['formula_ids'] else 'not_applicable'
                if verification.get('formulas') != expected_formula_status:
                    raise ValueError('formula verification status does not match formula_ids')
                record_path = (root / verification['review_record']).resolve()
                if not record_path.is_relative_to(root.resolve()) or not record_path.is_file():
                    raise ValueError('missing or invalid review record')
                record = json.loads(record_path.read_text(encoding='utf-8'))
                entry = record['documents'].get(identifier, {})
                if entry.get('sha256') != hashlib.sha256(path.read_bytes()).hexdigest():
                    raise ValueError('review does not match article version')
                if entry.get('decision') != 'approved' or not record.get('reviewer') or record.get('date') != meta['reviewed_at']:
                    raise ValueError('invalid review decision, reviewer or date')
            if not body.startswith('# '):
                raise ValueError('missing article heading')
        except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
            errors.append(f'{path.relative_to(root).as_posix()}: {exc}')
    return errors


def main():
    errors = validate()
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print('Initial metadata checks passed; content, links and full schema not checked.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
