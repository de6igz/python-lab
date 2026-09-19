"""Детерминированный эксперимент и проверяемый кэш, без внешних библиотек."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
SEED = 3960
REPLICATES = 20000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_data(path):
    groups = {}
    seen = set()
    with Path(path).open(newline='', encoding='utf-8') as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ['workers', 'run', 'seconds']:
            raise ValueError('CSV header must be workers,run,seconds')
        for row in reader:
            workers, run, seconds = int(row['workers']), int(row['run']), float(row['seconds'])
            if workers < 1 or run < 1 or not math.isfinite(seconds) or seconds <= 0:
                raise ValueError('workers/run must be positive; seconds must be finite and positive')
            if (workers, run) in seen:
                raise ValueError('duplicate workers/run pair')
            seen.add((workers, run))
            groups.setdefault(workers, []).append(seconds)
    if 1 not in groups or len(groups) < 2 or any(len(v) < 2 for v in groups.values()):
        raise ValueError('need baseline workers=1 and at least two groups with two runs each')
    return groups


def compute(groups):
    rng = random.Random(SEED)
    baseline = statistics.mean(groups[1])
    results = []
    for workers, values in sorted(groups.items()):
        samples = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(REPLICATES))
        mean = statistics.mean(values)
        results.append(dict(workers=workers, n=len(values), mean=mean,
                            low=samples[int(.025 * REPLICATES)],
                            high=samples[int(.975 * REPLICATES)],
                            speedup=baseline / mean, efficiency=baseline / mean / workers))
    return results


def graph(rows):
    colors = ['#0f766e', '#127c85', '#2a6f97', '#6d5cae']
    bars = []
    for i, r in enumerate(rows):
        x = 100 + i * 135
        h = 215 * r['mean'] / max(v['mean'] for v in rows)
        bars.append(f'<rect x="{x}" y="{290-h:.2f}" width="72" height="{h:.2f}" rx="6" fill="{colors[i % 4]}"/>'
                    f'<text x="{x+36}" y="{278-h:.2f}" text-anchor="middle">{r["mean"]:.2f} с</text>'
                    f'<text x="{x+36}" y="318" text-anchor="middle">{r["workers"]}</text>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 370" role="img" aria-labelledby="title desc">'
            '<title id="title">Среднее время обработки</title><desc id="desc">Время снижается при увеличении числа потоков; отдача уменьшается.</desc>'
            '<rect width="700" height="370" fill="#f5f8fa" rx="16"/><g font-family="sans-serif" font-size="17" fill="#17324d">'
            '<text x="35" y="32">Среднее время, секунды · учебные данные</text>'
            + ''.join(bars) + '<text x="350" y="353" text-anchor="middle">Число рабочих потоков</text></g></svg>')


def provenance():
    commit = os.getenv('GITHUB_SHA')
    if not commit:
        p = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True)
        commit = p.stdout.strip() if p.returncode == 0 else 'uncommitted'
    dirty = subprocess.run(['git', 'status', '--porcelain'], cwd=ROOT, capture_output=True, text=True)
    return commit, bool(dirty.stdout.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', type=Path, default=ROOT / 'data/timings.csv')
    parser.add_argument('--output', type=Path, default=ROOT / 'docs/generated')
    parser.add_argument('--cache', type=Path, default=ROOT / '.work/cache')
    args = parser.parse_args()
    start = time.perf_counter()
    groups = read_data(args.data)
    inputs = {'data_sha256': sha(args.data), 'code_sha256': sha(__file__),
              'requirements_sha256': sha(ROOT / 'requirements.txt'),
              'python': platform.python_version(), 'seed': SEED, 'replicates': REPLICATES}
    key = hashlib.sha256(json.dumps(inputs, sort_keys=True).encode()).hexdigest()
    cache = args.cache / key
    cache.mkdir(parents=True, exist_ok=True)
    artifact = cache / 'result.json'
    checksum = cache / 'result.sha256'
    hit = artifact.exists() and checksum.exists() and sha(artifact) == checksum.read_text().strip()
    if hit:
        rows = json.loads(artifact.read_text())
    else:
        rows = compute(groups)
        artifact.write_text(json.dumps(rows, indent=2) + '\n')
        checksum.write_text(sha(artifact) + '\n')
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / 'chart.svg').write_text(graph(rows), encoding='utf-8')
    with (args.output / 'summary.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    commit, dirty = provenance()
    stamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    metadata = dict(inputs, cache_key=key, cache_hit=hit, commit=commit, dirty=dirty,
                    built_at=stamp, dataset_version='sha256:' + inputs['data_sha256'],
                    artifacts={name: sha(args.output / name) for name in ['chart.svg', 'summary.csv']})
    (args.output / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    table = '\n'.join(f'| {r["workers"]} | {r["n"]} | {r["mean"]:.3f} | [{r["low"]:.3f}; {r["high"]:.3f}] | {r["speedup"]:.3f} | {r["efficiency"]:.3f} |' for r in rows)
    page = f'''# Результаты эксперимента

!!! warning "Происхождение данных"
    Синтетический учебный набор, 20 наблюдений. Эти числа не являются замером реальной системы.

## Методика

Для каждой группы рассчитываем среднее время и процентильный 95% bootstrap-интервал
по {REPLICATES} выборкам с возвращением, seed={SEED}. Интервал относится к среднему времени,
а не к ускорению. При пяти наблюдениях в группе неопределённость оценена лишь приближённо.

<div class="formula" id="eq-speedup"><math xmlns="http://www.w3.org/1998/Math/MathML" display="block"><mrow><mi>S</mi><mo>(</mo><mi>p</mi><mo>)</mo><mo>=</mo><mfrac><msub><mover><mi>t</mi><mo>¯</mo></mover><mn>1</mn></msub><msub><mover><mi>t</mi><mo>¯</mo></mover><mi>p</mi></msub></mfrac></mrow></math><span>(1)</span></div>

Ускорение определено в [формуле (1)](#eq-speedup), эффективность равна S(p)/p.
Формула — нативный MathML; загрузка MathJax, шрифтов или CDN не требуется.

## График и таблица

![Среднее время обработки по числу потоков](chart.svg)

| Потоки | n | Среднее, с | 95% CI, с | Ускорение | Эффективность |
| --- | --- | --- | --- | --- | --- |
{table}

В учебном наборе ускорение растёт медленнее числа потоков, а эффективность падает.
Это согласуется с наличием последовательной части и накладных расходов, но не устанавливает
их причин и не подтверждает закон Амдала на реальных измерениях.

## Артефакты и версия

- [Таблица CSV](summary.csv)
- [Метаданные JSON](metadata.json)
- Коммит: `{commit}`; незакоммиченные изменения: `{dirty}`.
- Дата сборки UTC: `{stamp}`.
- Версия данных SHA-256: `{inputs['data_sha256']}`.
- Ключ кэша: `{key}`; попадание: `{hit}`.

[Как повторить эксперимент](../pipeline.md) · [Исследование способов публикации](../research.md)
'''
    (args.output / 'results.md').write_text(page, encoding='utf-8')
    print(json.dumps(dict(cache_hit=hit, elapsed_seconds=time.perf_counter()-start, cache_key=key, rows=rows)))


if __name__ == '__main__':
    main()
