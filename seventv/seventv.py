from __future__ import annotations
import aiohttp
from typing import Literal
import re

class Emote:
    def __init__(self, id = None, name = None, owner_username = None, host_url = None):
        self.id = id
        self.name = name
        self.owner_username = owner_username
        self.host_url = host_url

    def __repr__(self):
        return '' \
            f'Emote(id: {self.id}, ' \
            f'name: {self.name}, ' \
            f'owner_username: {self.owner_username}, ' \
            f'host_url: {self.host_url})'
    
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "owner_username": self.owner_username,
            "host_url": self.host_url
        }

def create_emote_objects(response: dict) -> list[Emote]:
    if (response.get('errors', {})):
        raise Exception(response.get('errors', {})[0].get('message', {}))
    
    emote_objects = []
    emotes_data = response.get('data', {}).get('emotes')
    emote_items = emotes_data.get('items', [])

    for emote in emote_items:
        emote_id = emote.get('id')
        emote_name = emote.get('name')
        owner = emote.get('owner', {})
        owner_username = owner.get('username') if owner else None
        host = emote.get('host', {})
        host_url = host.get('url')

        emote_objects.append(Emote(emote_id, emote_name, owner_username, host_url))

    return emote_objects

class seventv:
    """The seventv instance that contains an aiohttp session and the methods for interacting with the API"""
    def __init__(self):
        self.endpoint = "https://7tv.io/v3/gql"
        self.session = aiohttp.ClientSession()

    async def close(self):
        await self.session.close()

    async def emote_search(self, 
                           searchterm: str = "", 
                           limit: int = 12,
                           page: int = 1,
                           case_sensitive: bool = False, 
                           animated: bool = False,
                           exact_match: bool = False, 
                           query: Literal["all", "url"] = "all",
                           ):
        """Search for emotes using a text string (searchterm)"""
        url = self.endpoint
        queries = {
        "all": 'query SearchEmotes($query: String!, $page: Int, $sort: Sort, $limit: Int, $filter: EmoteSearchFilter) {\n emotes(query: $query, page: $page, sort: $sort, limit: $limit, filter: $filter) {\nitems{\n id\n name\n owner{\n username\n }\n host{\n url}}\n}\n}',
        "url": 'query SearchEmotes($query: String!, $page: Int, $sort: Sort, $limit: Int, $filter: EmoteSearchFilter) {\n emotes(query: $query, page: $page, sort: $sort, limit: $limit, filter: $filter) {\nitems{host{\n url}}\n}\n}'
        }
        headers = {
            "Content-Type": "application/json"
        }
        payload = {
            "operationName": "SearchEmotes",
            "variables": {
                "query": searchterm,
                "limit": limit,
                "page": page,
                "sort": {
                    "value": "popularity",
                    "order": "DESCENDING"
                },
                "filter": {
                    "category": "TOP",
                    "exact_match": exact_match,
                    "case_sensitive": case_sensitive,
                    "ignore_tags": False,
                    "zero_width": False,
                    "animated": animated,
                    "aspect_ratio": ""
                }
            },
            "query": f"{queries.get(query)}"
        }
        async with self.session.post(url, json=payload, headers=headers) as response:
            response_data = await response.json()
            if response_data.get('errors', {}):
                raise seventvException(response_data.get('errors', {})[0].get('message', {}))
            emote_objects = create_emote_objects(response_data)
            return emote_objects

class seventvException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(f"That didn't work!\n{message}")