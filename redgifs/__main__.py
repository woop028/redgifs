"""
The MIT License (MIT)

Copyright (c) 2022-present scrazzz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import sys
import argparse
import platform
import importlib.metadata

import aiohttp
import requests
from yarl import URL

import redgifs

parser = argparse.ArgumentParser(prog='redgifs')
parser.add_argument('-dl', '--download', help='Download the GIF from given link', metavar='')
parser.add_argument('-l', '--list', help='Download GIFs from a list of URLs', metavar='')
parser.add_argument('-v', '--version', help='Show redgifs version info.', action='store_true')
args = parser.parse_args()

session = requests.Session()
client = redgifs.API(session=session)
client.login()

def show_version() -> None:
    entries = []

    entries.append('- Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(sys.version_info))
    version_info = redgifs.version_info
    entries.append('- redgifs v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(version_info))
    if version_info.releaselevel != 'final':
        version = importlib.metadata.version('redgifs')
        if version:
            entries.append(f'    - redgifs metadata: v{version}')
    
    entries.append(f'- aiohttp v{aiohttp.__version__}')
    uname = platform.uname()
    entries.append('- system info: {0.system} {0.release} {0.version}'.format(uname))
    print('\n'.join(entries))

def save_to_file(mp4_link) -> None:
    headers = client.http.headers
    r = session.get(mp4_link, headers=headers, stream=True)
    file_name = mp4_link.split('/')[3].split('?')[0]
    with open(file_name, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):
            if chunk:
                f.write(chunk)
    
    print(f'\nDownloaded: {file_name}')

def start_dl(url: str) -> None:
    yarl_url = URL(url)
    if 'redgifs' not in str(yarl_url.host):
        raise TypeError(f'"{url}" is an invalid redgifs URL')

    # Handle 'normal' URLs, i.e, a direct link from browser (eg: "https://redgifs.com/watch/deeznuts")
    if 'watch' in yarl_url.path:
        id = yarl_url.path.split('/')[-1]
        hd = client.get_gif(id).urls.hd
        print(f'Downloading {id}...')
        save_to_file(hd)

def main() -> None:
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.download:
        start_dl(args.download)

    if args.list:
        with open(args.list) as f:
            for url in f.readlines():
                start_dl(url)

    if args.version:
        show_version()

if __name__ == '__main__':
    main()