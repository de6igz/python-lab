"""Serve the final artifact locally with external resources blocked by CSP."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse


class OfflineHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; worker-src 'self' blob:; connect-src 'self'")
        super().end_headers()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, default=Path('artifacts'))
    parser.add_argument('--port', type=int, default=8001)
    args = parser.parse_args()
    handler = partial(OfflineHandler, directory=str(args.directory.resolve()))
    ThreadingHTTPServer(('127.0.0.1', args.port), handler).serve_forever()
