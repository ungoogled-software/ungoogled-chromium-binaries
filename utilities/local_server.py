#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Copyright (c) 2018 The ungoogled-chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

'''
Local webserver to view generated site
'''

import argparse
import http.server
import socketserver
import urllib.parse
from pathlib import Path

_PREFIX = 'ungoogled-chromium-binaries'

class BinariesHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        translated_path = Path(super().translate_path(path))
        translated_path = translated_path.relative_to(Path.cwd())
        try:
            translated_path = translated_path.relative_to(_PREFIX)
        except ValueError:
            pass
        if not translated_path.exists():
            translated_path = translated_path.with_name(translated_path.name + '.html')
        print('Attempting to read path:', translated_path)
        return str(translated_path.absolute())

def main():
    '''CLI Entrypoint'''
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', type=int, default='8086', help='Port to listen on on localhost')
    args = parser.parse_args()
    httpd = socketserver.TCPServer(('localhost', args.port), BinariesHTTPRequestHandler)

    print('Serving on localhost at port', args.port)
    httpd.serve_forever()

if __name__ == '__main__':
    main()
