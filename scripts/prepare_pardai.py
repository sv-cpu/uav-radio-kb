"""Prepare immutable, local Markdown upload packages; no PardAI API calls."""
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys

from scripts.validate import ROOT, read_article, validate

VERSION = 1
REPOSITORY = 'sv-cpu/uav-radio-kb'


def canonical(obj):
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def prepare(root, as_of, research=False, previous=None):
    """Return (manifest, {package relative path: source bytes}); does not write."""
    errors = validate(root)
    if errors:
        raise ValueError('\n'.join(errors))
    if not isinstance(as_of, dt.date):
        raise ValueError('as_of must be a date')
    corpus_files = {}
    documents = []
    registries = {'sources_sha256': sha((root / 'sources.yaml').read_bytes()),
                  'formulas_sha256': sha((root / 'registries/formulas.yaml').read_bytes())}
    for path in sorted((root / 'docs').rglob('*.md')):
        if path.name.lower() == 'index.md':
            continue
        if path.is_symlink() or not path.resolve().is_relative_to((root / 'docs').resolve()):
            raise ValueError('symlinks are not accepted in the corpus')
        meta, body = read_article(path)
        if meta['status'] == 'deprecated':
            continue
        if not research:
            if meta['status'] != 'verified' or meta['rag']['include'] is not True:
                continue
            due = meta['review_due']
            if due is not None and dt.date.fromisoformat(due) < as_of:
                continue
            if meta['type'] == 'standard' and due is None:
                continue
            # A formula referenced by an admitted article must have documented checks.
            registry = json.loads((root / 'registries/formulas.yaml').read_text(encoding='utf-8'))
            formulas = {f['formula_id']: f for f in registry['formulas']}
            for fid in meta['formula_ids']:
                f = formulas[fid]
                if not str(f.get('verification', '')).startswith('source_and_numerical_checks_passed'):
                    raise ValueError('formula not verified: ' + fid)
                for field in ('implementation', 'tests', 'review_record'):
                    target = f.get(field)
                    if not isinstance(target, str) or not (root / target).resolve().is_relative_to(root.resolve()) or not (root / target).is_file():
                        raise ValueError('formula missing ' + field + ': ' + fid)
        # Reject multiple or absent H1. Index pages never become documents.
        headings = [line for line in body.splitlines() if line.startswith('# ')]
        if len(headings) != 1 or headings[0][2:].strip() != meta['title']:
            raise ValueError('article must have exactly one H1 matching title: ' + str(path))
        package_path = 'articles/' + meta['id'] + '.md'
        raw = path.read_bytes()
        corpus_files[package_path] = raw
        documents.append({'external_id': meta['id'], 'repository_path': path.relative_to(root).as_posix(),
                          'package_path': package_path, 'sha256': sha(raw), 'metadata': meta})
    documents.sort(key=lambda x: x['external_id'])
    config = {'schema_version': VERSION, 'repository': REPOSITORY, 'repository_revision': None,
              'library_id': None, 'mode': 'research' if research else 'main',
              'as_of': as_of.isoformat(), 'format': 'markdown-original-bytes', 'indices_excluded': True,
              'chunking': 'PardAI managed; configuration not supplied'}
    if previous is not None:
        oldconfig = previous.get('config', {})
        for field in ('schema_version', 'repository', 'mode', 'format'):
            if oldconfig.get(field) != config[field]:
                raise ValueError('incompatible previous manifest: ' + field)
        olddocs = previous.get('documents')
        if not isinstance(olddocs, list) or any(not isinstance(x, dict) or not isinstance(x.get('external_id'), str) for x in olddocs):
            raise ValueError('invalid previous manifest documents')
        old = {d['external_id']: d for d in olddocs}
        if len(old) != len(olddocs):
            raise ValueError('duplicate external ID in previous manifest')
    else:
        old = {}
    new = {d['external_id']: d for d in documents}
    registry_changed = previous is not None and previous.get('registries') != registries
    changes = {'added': sorted(new.keys() - old.keys()), 'removed': sorted(old.keys() - new.keys()),
               'renamed': sorted(i for i in new.keys() & old.keys() if old[i].get('repository_path') != new[i]['repository_path']),
               'changed': sorted(i for i in new.keys() & old.keys() if old[i].get('sha256') != new[i]['sha256'] or registry_changed),
               'registries_changed': registry_changed}
    manifest = {'config': config, 'registries': registries, 'documents': documents, 'changes': changes,
                'warning': 'Research only; unreviewed content' if research else None}
    return manifest, corpus_files


def write_package(build_dir, manifest, files):
    """Use content-addressed names and exclusive writes; never delete previous exports."""
    manifest_bytes = canonical(manifest)
    name = sha(manifest_bytes)
    parent = build_dir.resolve()
    mode_dir = parent / ('pardai-' + manifest['config']['mode'])
    package = mode_dir / name
    if mode_dir.is_symlink() or package.is_symlink():
        raise ValueError('package path must not be a symlink')
    package.mkdir(parents=True, exist_ok=True)
    expected = {**files, 'manifest.json': manifest_bytes}
    for item in package.rglob('*'):
        if item.is_symlink():
            raise ValueError('package must not contain symlinks: ' + str(item))
        relative = item.relative_to(package).as_posix()
        if item.is_file() and relative not in expected:
            raise ValueError('existing package has unexpected file: ' + str(item))
        if item.is_dir() and relative != 'articles':
            raise ValueError('existing package has unexpected directory: ' + str(item))
    for relative, payload in expected.items():
        target = package / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            with target.open('xb') as stream:
                stream.write(payload)
        except FileExistsError:
            if target.read_bytes() != payload:
                raise ValueError('existing package content differs: ' + str(target))
    return package


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--as-of', default=dt.date.today().isoformat(), help='Review validity date, YYYY-MM-DD')
    parser.add_argument('--research', action='store_true', help='Include drafts for isolated experiments only')
    parser.add_argument('--previous', type=Path, help='Previously applied manifest; used to report changes')
    args = parser.parse_args()
    try:
        date = dt.date.fromisoformat(args.as_of)
        previous = json.loads(args.previous.read_text(encoding='utf-8')) if args.previous else None
        manifest, files = prepare(ROOT, date, args.research, previous)
        dest = write_package(ROOT / 'build', manifest, files)
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f'{len(files)} Markdown files; mode={manifest["config"]["mode"]}; package={dest}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
