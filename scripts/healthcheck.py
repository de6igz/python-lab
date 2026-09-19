"""Проверка кода 200 и контрольной строки с ограниченными повторами."""
import argparse
import time
import urllib.error
import urllib.request


def check(url, marker='RESEARCH-SITE-3960-OK', attempts=5, delay=2):
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers={'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(request, timeout=15) as response:
                status = response.status
                body = response.read().decode('utf-8')
            if status != 200 or marker not in body:
                raise ValueError(f'healthcheck failed: HTTP {status}, marker_present={marker in body}')
            print(f'healthcheck OK: HTTP {status}, marker_present=True')
            return
        except (urllib.error.URLError, ValueError) as error:
            if attempt + 1 == attempts:
                raise SystemExit(str(error)) from error
            time.sleep(delay)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('--marker', default='RESEARCH-SITE-3960-OK')
    args = parser.parse_args()
    check(args.url, args.marker)
