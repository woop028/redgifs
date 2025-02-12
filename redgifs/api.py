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

import requests

from .http import HTTP, ProxyAuth
from .enums import Order, Tags
from .utils import _to_web_url
from .parser import parse_creator, parse_search, parse_creators, parse_search_image
from .models import URL, GIF, CreatorResult, SearchResult, CreatorsResult

class API:
    """The API Instance to get information from the RedGifs API.

    .. note::

        If you are using this library in an asynchronous code,
        you should pass a session object which is an instance of
        :class:`aiohttp.ClientSession`.

    Parameters
    ----------
    session: Optional[:class:`requests.Session`]
        A session object that can be provided to do the requests.
        If not provided, a new session object is created.
        See above note too.
    proxy: Optional[:class:`str`]
        A valid proxy URL.
    proxy_auth: Optional[:class:`redgifs.ProxyAuth`]
        The proxy auth to provide if the proxy requires it.
    """

    def __init__(
        self,
        session: Optional[requests.Session] = None,
        *,
        proxy: Optional[str] = None,
        proxy_auth: Optional[ProxyAuth] = None
    ) -> None:
        self.http: HTTP = HTTP(session, proxy=proxy, proxy_auth=proxy_auth)

    def login(self, ip_address: str, user_agent: str, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        return self.http.login(ip_address, user_agent, username, password)

    def get_tags(self) -> List[Dict[str, Union[str, int]]]:
        """Get all available RedGifs Tags.
        
        Returns
        -------
        A list of dicts.
        """
        return (self.http.get_tags()['tags'])
    
    def get_gif(self, id: str) -> GIF:
        """
        Get details of a GIF with its ID.

        Parameters
        ----------
        id: :class:`str`
            The ID of the GIF.

        Returns
        -------
        :py:class:`GIF <redgifs.models.Gif>` - The GIF's info.
        """

        json: Dict[str, Any] = self.http.get_gif(id)['gif']
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

    def get_trending_tags(self) -> List[Dict[str, Union[str, int]]]:
        """Gets the trending searches on RedGifs.

        Returns
        -------
        ``List[Dict[str, Union[str, int]]]``
            A list of dicts containing the tag name and count::

                [
                    {
                        "name": "r/CaughtPublic",
                        "count": 2034
                    },
                    {
                        "name": "Vintage",
                        "count": 19051
                    },
                    ...
                ]
        """
        resp = self.http.get_trending_tags()['tags']
        return resp

    def fetch_tag_suggestions(self, query: str) -> List[str]:
        """Get tag suggestions from RedGifs.

        .. note::

            This is an API call. See :func:`~redgifs.Tags.search` for an internal lookup
            of available tags.

        Parameters
        ----------
        query: :class:`str`
            The tag name to look for.

        Returns
        -------
        ``List[str]``
            A list of tag names.
        """
        result = self.http.get_tag_suggestions(query)
        return [d['text'] for d in result]

    def search(
        self,
        search_text: Union[str, Tags],
        *,
        order: Order = Order.recent,
        count: int = 80,
        page: int = 1
    ) -> SearchResult:
        """
        Search for a GIF.

        Parameters
        ----------
        search_text: Union[:class:`str`, :class:`Tags`]
            The GIFs to search for. Can be a string or an instance of :class:`Tags`.
        order: Optional[:class:`Order`]
            The order of the GIFs to return.
        count: Optional[:class:`int`]
            The amount of GIFs to return.
        page: Optional[:class:`int`]
            The page number of the GIFs to return.

        Returns
        -------
        :py:class:`SearchResult <redgifs.models.SearchResult>` - The search result.
        """

        if isinstance(search_text, str):
            st = Tags.search(search_text)[0]
        elif isinstance(search_text, Tags):
            st = search_text.value
        resp = self.http.search(st, order, count, page)
        return parse_search(st, resp)

    search_gif = search

    def gifs_info(
            self,
            gifIds: Union[str, str],
        ) -> SearchResult:
        resp = self.http.gifs_info(gifIds)
        print(resp)


    def search_creators(
        self,
        *,
        page: int = 1,
        order: Order = Order.recent,
        verified: bool = False,
        tags: Optional[Union[List[Tags], List[str]]] = None
    ) -> CreatorsResult:
        """
        Search for RedGifs Creators.

        Parameters
        ----------
        page: Optional[:class:`int`]
            The number of page to return.
        order: Optional[:class:`Order`]
            The order of the creators to return.
        verified: Optional[:class:`bool`]
            Wheather to only return verified creators.
        tags: Optional[Union[List[:class:`Tags`], List[:class:`str`]]]
            A list of tags to look for.
            Narrows down the results to content creators that have contents with all the given tags.

        Returns
        -------
        :py:class:`CreatorsResult <redgifs.models.CreatorsResult>` - The search result.
        """
        resp = self.http.search_creators(page=page, order=order, verified=verified, tags=tags)
        return parse_creators(resp)

    def search_creator(self, username: str, *, page: int = 1, order: Order = Order.recent) -> CreatorResult:
        """
        Search for a RedGifs creator/user.

        Parameters
        ----------
        username: :class:`str`
            The username of the creator/user.
        page: :class:`int`
            The page number of GIFs.
            There is a total of 80 GIFs in one page.
        order: :class:`Order`
            The order to return creator/user's GIFs.

        Returns
        -------
        :py:class:`CreatorResult <redgifs.models.CreatorResult>` - The creator/user searched for.
        """
        resp = self.http.search_creator(username, page=page, order=order)
        return parse_creator(resp)

    search_user = search_creator

    def search_image(
        self,
        search_text: Union[str, Tags],
        *,
        order: Order = Order.trending,
        count: int = 80,
        page: int = 1
    ) -> SearchResult:
        """
        Search for images on Redgifs.

        Parameters
        ----------
        search_text: Union[:class:`str`, :class:`Tags`]
            The images to search for. Can be a string or an instance of :class:`Tags`.
        order: Optional[:class:`Order`]
            The order of the images to return.
        count: Optional[:class:`int`]
            The amount of images to return.
        page: Optional[:class:`int`]
            The page number of the images to return.

        Returns
        -------
        :py:class:`SearchResult <redgifs.models.SearchResult>` - The search result.
        """
        if isinstance(search_text, str):
            # We are not going to use Tags.search() here because it doesn't matter
            # whatever the search_text is, this API endpoints provides images nonetheless.
            st = search_text
        elif isinstance(search_text, Tags):
            st = search_text.value
        resp = self.http.search_image(st, order, count, page)
        return parse_search_image(st, resp)

    def download(self, url: str, fp: Union[str, bytes, os.PathLike[Any], io.BufferedIOBase]):
        """
        A friendly method to download a RedGifs media.

        Example:

        .. code-block:: python

            api = API()
            api.login()
            hd_url = api.search("query").gifs[0].urls.hd
            api.download(hd_url, "video.mp4")

        .. note::
            
            You should use this method to download any media from RedGifs
            because RedGifs does validation on User-Agents. If you try to download
            it by using any other means, it may give you a 403 error.

        Parameters
        ----------
        url: str
            A valid RedGifs URL.
        fp: Union[:class:`io.BufferedIOBase`, :class:`os.PathLike`]
            The file-like object to save this asset to or the filename
            to use. If a filename is passed then a file is created with that
            filename and used instead.
        """
        return self.http.download(url, fp)

    def close(self) -> None:
        """Closes the API session."""
        return self.http.close()
