"""Повторяемые измерения P3 и намеренные отрицательные проверки."""
from pathlib import Path
import csv
import json
import os
import platform
import shutil
import statistics
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'evidence'
WORK = ROOT / '.work'


def command(args, expected=0, env=None):
    start = time.perf_counter()
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, env=env)
    elapsed = time.perf_counter() - start
    if (expected == 0 and result.returncode != 0) or (expected != 0 and result.returncode == 0):
        raise RuntimeError(result.stdout + result.stderr)
    return result, elapsed


def main():
    EVIDENCE.mkdir(exist_ok=True)
    WORK.mkdir(exist_ok=True)
    measurements = []
    with tempfile.TemporaryDirectory(prefix='verify-', dir=WORK) as folder:
        folder = Path(folder)
        output, cache = folder / 'output', folder / 'cache'
        base = [sys.executable, 'scripts/experiment.py', '--output', str(output), '--cache', str(cache)]
        cold, warm = [], []
        for i in range(5):
            if cache.exists():
                shutil.rmtree(cache)
            first, t1 = command(base)
            old = json.loads(first.stdout)
            second, t2 = command(base)
            repeat = json.loads(second.stdout)
            assert not old['cache_hit'] and repeat['cache_hit'] and old['rows'] == repeat['rows']
            cold.append(t1)
            warm.append(t2)
            measurements.extend([dict(metric='experiment_cold', run=i+1, seconds=t1), dict(metric='experiment_cached', run=i+1, seconds=t2)])
        original_svg = (output / 'chart.svg').read_bytes()
        changed = folder / 'changed.csv'
        with (ROOT / 'data/timings.csv').open(newline='') as stream:
            inputs = list(csv.DictReader(stream))
        previous_seconds = float(inputs[-1]['seconds'])
        inputs[-1]['seconds'] = str(previous_seconds + 1.0)
        with changed.open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=['workers', 'run', 'seconds'])
            writer.writeheader()
            writer.writerows(inputs)
        result, duration = command(base + ['--data', str(changed)])
        updated = json.loads(result.stdout)
        assert not updated['cache_hit'] and updated['cache_key'] != old['cache_key']
        assert updated['rows'] != old['rows'] and (output / 'chart.svg').read_bytes() != original_svg
        mutation = {'original': old, 'changed': updated, 'changed_seconds': duration,
                    'change': f"workers={inputs[-1]['workers']}, run={inputs[-1]['run']}, seconds: {previous_seconds} -> {inputs[-1]['seconds']}", 'svg_changed': True}
        (EVIDENCE / 'data-change.json').write_text(json.dumps(mutation, indent=2) + '\n')
        (cache / updated['cache_key'] / 'result.json').write_text('corrupted')
        repaired, _ = command(base + ['--data', str(changed)])
        assert not json.loads(repaired.stdout)['cache_hit']
        bad = folder / 'bad.csv'
        bad.write_text('workers,run,seconds\n1,1,-1\n')
        failed, _ = command(base + ['--data', str(bad)], expected=1)
        (EVIDENCE / 'failure-invalid-data.log').write_text(failed.stdout + failed.stderr)
        # Isolated negative site avoids modifying user-authored documentation.
        source = folder / 'docs'
        source.mkdir()
        config = folder / 'mkdocs.yml'
        config.write_text(f'site_name: Negative test\ndocs_dir: {source}\nsite_dir: {folder / "site"}\nvalidation:\n  links:\n    not_found: warn\n    anchors: warn\n')
        for name, content in [('missing-link', '# Test\n[broken](absent.md)\n'), ('missing-anchor', '# Test\n[broken](#absent)\n')]:
            (source / 'index.md').write_text(content)
            failure, _ = command([sys.executable, '-m', 'mkdocs', 'build', '--strict', '-f', str(config)], expected=1)
            (EVIDENCE / f'failure-{name}.log').write_text(failure.stdout + failure.stderr)
        (source / 'index.md').write_text('# Test\n[working](#test)\n')
        fixed, _ = command([sys.executable, '-m', 'mkdocs', 'build', '--strict', '-f', str(config)])
        (EVIDENCE / 'negative-fixtures-fixed.log').write_text(fixed.stdout + fixed.stderr)
    tests, _ = command([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'])
    (EVIDENCE / 'tests.log').write_text(tests.stdout + tests.stderr)
    exp, _ = command([sys.executable, 'scripts/experiment.py'])
    for i in range(3):
        build, duration = command([sys.executable, '-m', 'mkdocs', 'build', '--strict', '--site-dir', str(WORK / 'site')])
        measurements.append(dict(metric='mkdocs_strict_build', run=i+1, seconds=duration))
        (EVIDENCE / 'build.log').write_text(build.stdout + build.stderr)
    audit, _ = command([sys.executable, 'scripts/audit_site.py', str(WORK / 'site')])
    (EVIDENCE / 'audit.log').write_text(audit.stdout + audit.stderr)
    with (EVIDENCE / 'measurements.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['metric', 'run', 'seconds'])
        writer.writeheader()
        writer.writerows(measurements)
    summary = {'python': platform.python_version(), 'platform': platform.platform(),
               'experiment_cold_median_s': statistics.median(cold),
               'experiment_cached_median_s': statistics.median(warm),
               'speedup': statistics.median(cold) / statistics.median(warm),
               'mkdocs_median_s': statistics.median(m['seconds'] for m in measurements if m['metric'] == 'mkdocs_strict_build'),
               'site_bytes': sum(p.stat().st_size for p in (WORK / 'site').rglob('*') if p.is_file()),
               'results_html_bytes': (WORK / 'site/generated/results.html').stat().st_size,
               'all_checks_passed': True}
    (EVIDENCE / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
