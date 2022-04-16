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

from typing import List, Optional, Union

import requests

from .enums import Order, Tags
from .http import HTTP
from .parser import parse_search, parse_creators
from .models import SearchResult, CreatorsResult

class API:
    """The API Instance to get information from RedGifs API."""
    def __init__(self, session: Optional[requests.Session] = None) -> None:
        self.http: HTTP = HTTP(session)

    def get_tags(self):
        """Get all available RedGifs Tags."""
        return (self.http.get_tags())
    
    def get_gif(self, id: str):
        """
        Get details of a GIF with its ID.

        Parameters
        ----------
        id: str
            The ID of the GIF.
        """
        resp = self.http.get_gif(id)
        return resp

    def search(self, search_text: Union[str, Tags], *, order: Order = Order.recent, count: int = 80, page: int = 1) -> SearchResult:
        """
        Search for a GIF.

        Parameters
        ----------
        search_text: Union[str, :class:`Tags`]
            The GIFs to search for. Can be a string or an instance of :class:`Tags`.
        
        order: Optional[:class:`Order`]
            The order of the GIFs to return.
        
        count: Optional[int]
            The amount of GIFs to return.
        
        page: Optional[int]
            The page number of the GIFs to return.
        """

        if isinstance(search_text, str):
            st = Tags.search(search_text)
        elif isinstance(search_text, Tags):
            st = search_text.value
        resp = self.http.search(st, order, count, page)
        return parse_search(st, resp)

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
        page: Optional[int]
            The number of page to return.

        order: Optional[:class:`Order`]
            The order of the creators to return.

        verified: Optional[bool]
            Wheather to only return verified creators.

        tags: Optional[Union[List[Tags], List[str]]]
            A list of tags to look for.
            Narrows down the results to content creators that have contents with all those tags.
        """
        resp = self.http.search_creators(page=page, order=order, verified=verified, tags=tags)
        return parse_creators(resp)

    def close(self) -> None:
        """
        Closes the session.
        """
        return self.http.close()
