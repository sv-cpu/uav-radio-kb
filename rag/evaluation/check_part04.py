"""Простая воспроизводимая оценка полнотекстового поиска для части 4, без embeddings."""
import collections
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
QUESTIONS = Path(__file__).with_name('part04-questions.json')


def terms(text):
    words = re.findall(r'[a-zа-яё0-9]+', text.lower())
    return [w[:5] if re.fullmatch(r'[а-яё]{6,}', w) else w for w in words if len(w) > 1]


def run():
    corpus = [json.loads(line) for line in (ROOT / 'build/research.jsonl').read_text(encoding='utf-8').splitlines()]
    questions = json.loads(QUESTIONS.read_text(encoding='utf-8'))
    docs = [(d['document_id'], collections.Counter(terms(d['title'] + ' ' + d['text']))) for d in corpus]
    df = collections.Counter(word for _, counts in docs for word in counts)
    report = []
    for q in questions:
        query = set(terms(q['question']))
        scores = [(sum((1 + math.log(counts[w])) * (math.log((len(docs)+1)/(df[w]+1))+1)
                       for w in query if counts[w]), ident) for ident, counts in docs]
        results = [ident for score, ident in sorted(scores, key=lambda x: (-x[0], x[1])) if score > 0][:5]
        hit = None if not q['expected'] else bool(set(results) & set(q['expected']))
        report.append({'id': q['id'], 'top5': results, 'hit': hit, 'insufficient': q['insufficient']})
    answered = [r for r in report if r['hit'] is not None and not r['insufficient']]
    count = sum(r['hit'] for r in answered)
    print(json.dumps({'configuration': 'whole-document TF-IDF-like lexical search; Russian first 5 characters; all research articles; no semantic model',
                      'question_count': len(report), 'answerable': len(answered), 'top5_hits': count, 'results': report},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(run())
