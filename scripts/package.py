"""Assemble a readable report and a self-contained handoff ZIP."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def report():
    parts = ['# Отчёт: генераторы статических сайтов\n\nАртём Солопов · Задание 1 · T2 и P3\n\n'
             'Статус: локальная часть выполнена; публикация на хостингах и сдача в Moodle отложены.\n']
    for name in ['report.md', 'research.md', 'pipeline.md', 'deployment.md', 'generated/results.md', 'licenses.md']:
        text = (ROOT / 'docs' / name).read_text()
        base = Path('docs') / Path(name).parent
        def fix(match):
            url = match.group(1)
            if '://' in url or url.startswith('#'):
                return match.group(0)
            return '](' + str(base / url) + ')'
        parts.append(re.sub(r'\]\(([^)]+)\)', fix, text))
    parts.append('# Приложение: полный workflow\n\n```yaml\n' +
                 (ROOT / '.github/workflows/site.yml').read_text() + '\n```')
    for path in sorted((ROOT / 'evidence').glob('*.log')):
        parts.append('## ' + path.name + '\n\n```text\n' + path.read_text() + '\n```')
    (ROOT / 'REPORT.md').write_text('\n\n---\n\n'.join(parts))


def archive():
    report()
    output = ROOT / 'artifacts'
    output.mkdir(exist_ok=True)
    target = output / 'assignment-3960.zip'
    files = []
    for name in ['.github', 'data', 'docs', 'scripts', 'tests', 'evidence', 'artifacts/site']:
        files.extend(p for p in (ROOT / name).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    for name in ['.gitignore', '.python-version', 'Makefile', 'README.md', 'REPORT.md',
                 'requirements.in', 'requirements.txt', 'mkdocs.yml',
                 'LICENSE-CODE', 'LICENSE-CONTENT', 'LICENSE-DATA']:
        files.append(ROOT / name)
    with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as package:
        for path in sorted(files):
            package.write(path, path.relative_to(ROOT))
    with zipfile.ZipFile(target) as package:
        assert package.testzip() is None
        assert 'artifacts/site/index.html' in package.namelist()
        assert 'REPORT.md' in package.namelist()
        assert not any('.task-3960' in p or '.work/' in p or '/.git/' in p for p in package.namelist())
    manifest = {'zip': target.name, 'files': len(files), 'bytes': target.stat().st_size,
                'sha256': hashlib.sha256(target.read_bytes()).hexdigest(),
                'site_bytes': sum(p.stat().st_size for p in (output / 'site').rglob('*') if p.is_file())}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    report() if args.report_only else archive()
