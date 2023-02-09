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

from __future__ import annotations

import io
import os
from typing import Any, Dict, List, Optional, Union

import aiohttp

from .http import AsyncHttp, ProxyAuth
from .enums import Tags, Order
from .utils import _to_web_url
from .parser import parse_search, parse_creator, parse_creators, parse_search_image
from .models import GIF, URL, CreatorResult, SearchResult, CreatorsResult

class API:
    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
        *,
        proxy: Optional[str] = None,
        proxy_auth: Optional[ProxyAuth] = None
    ) -> None:
        self.http: AsyncHttp = AsyncHttp(session, proxy=proxy, proxy_auth=proxy_auth)

    async def login(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        return (await self.http.login(username, password))

    async def get_tags(self) -> List[Dict[str, Union[str, int]]]:
        resp = await self.http.get_tags()
        return resp['tags']

    async def get_gif(self, id: str) -> GIF:
        json: Dict[str, Any] = (await self.http.get_gif(id))['gif']
        return GIF(
            id=json['id'],
            create_date=json['createDate'],
            has_audio=json['hasAudio'],
            width=json['width'],
            height=json['height'],
            likes=json['likes'],
            tags=json['tags'],
            verified=json['verified'],
            views=json['views'],
            duration=json['duration'],
            published=json['published'],
            urls=URL(
                sd=json['urls']['sd'],
                hd=json['urls']['hd'],
                poster=json['urls']['poster'],
                thumbnail=json['urls']['thumbnail'],
                vthumbnail=json['urls']['vthumbnail'],
                web_url=_to_web_url(json['id'])
            ),
            username=json['userName'],
            type=json['type'],
            avg_color=json['avgColor'],
        )

    async def get_trending_tags(self) -> List[Dict[str, Union[str, int]]]:
        result = (await self.http.get_trending_tags())['tags']
        return result

    async def fetch_tag_suggestions(self, query: str) -> List[str]:
        result = await self.http.get_tag_suggestions(query)
        return [d['text'] for d in result]

    async def search(self, search_text: Union[str, Tags], *, order: Order = Order.recent, count: int = 80, page: int = 1) -> SearchResult:
        if isinstance(search_text, str):
            st = Tags.search(search_text)[0]
        elif isinstance(search_text, Tags):
            st = search_text.value
        resp = await self.http.search(st, order, count, page)
        return parse_search(st, resp)

    search_gif = search

    async def search_creators(
        self,
        *,
        page: int = 1,
        order: Order = Order.recent,
        verified: bool = False,
        tags: Optional[Union[List[Tags], List[str]]] = None
    ) -> CreatorsResult:
        resp = await self.http.search_creators(page=page, order=order, verified=verified, tags=tags)
        return parse_creators(resp)

    async def search_creator(
        self,
        username: str,
        *,
        page: int = 1,
        order: Order = Order.recent
    ) -> CreatorResult:
        resp = await self.http.search_creator(username, page, order)
        return parse_creator(resp)

    search_user = search_creator

    async def search_image(
        self,
        search_text: Union[str, Tags],
        *,
        order: Order = Order.trending,
        count: int = 80,
        page: int = 1
    ) -> SearchResult:
        if isinstance(search_text, str):
            # We are not going to use Tags.search() here because it doesn't matter
            # whatever the search_text is, this API endpoints provides images nonetheless.
            st = search_text
        elif isinstance(search_text, Tags):
            st = search_text.value
        resp = await self.http.search_image(st, order, count, page)
        return parse_search_image(st, resp)

    async def download(self, url: str, fp: Union[str, bytes, os.PathLike[Any], io.BufferedIOBase]) -> int:
        return (await self.http.download(url, fp))

    async def close(self) -> None:
        return (await self.http.close())
