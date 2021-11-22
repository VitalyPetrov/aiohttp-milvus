import aiohttp
import ujson
import yarl

from asyncio.exceptions import TimeoutError
from starlette.exceptions import HTTPException
from socket import AF_INET
from typing import List, Optional, Dict, Any

from src.conf import settings


class MilvusHttpClient:
    def __init__(self, base_url: str, socket_family: int = AF_INET):

        self.base_url: yarl.URL = yarl.URL(base_url)
        self.socket_family = socket_family
        self.session: aiohttp.ClientSession = self._get_session()

    def _get_session(self) -> aiohttp.ClientSession:
        return aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(),
            connector=aiohttp.TCPConnector(
                family=self.socket_family,
                limit_per_host=settings.milvus.connection_pool_size,
            ),
            json_serialize=ujson.dumps,
        )

    async def close_session(self) -> None:
        if self.session:
            await self.session.close()
            self.session = None

    async def get_item_vector(
        self, collection_nm: str, item_id: int
    ) -> List[float]:
        url = (
            self.base_url
            / f"collections/{collection_nm}/vectors"
            % {"ids": item_id}
        )

        try:
            async with self.session.get(url=url) as response:
                # Milvus API has a bad-formatted headers so
                # the default aiohttp decoder cant be used
                data = await response.json(content_type=None)
        except TimeoutError:
            HTTPException(
                status_code=503, detail="Milvus DB connection timeout"
            )

        if not data:
            return

        if data.get("code"):
            raise HTTPException(status_code=404, detail=data.get("message"))

        return data.get("vectors")[0].get("vector")

    async def get_similar_items(
        self,
        collection_nm: str,
        item_id: int,
        search_params: Optional[Dict[str, Any]] = None,
        vec: Optional[List[float]] = None,
        top_n: int = 10,
    ) -> List[int]:
        if not vec:
            vec = await self.get_item_vector(
                collection_nm=collection_nm, item_id=item_id
            )

        # specify query url and params
        url = self.base_url / f"collections/{collection_nm}/vectors"
        # we need to search one additional item in order to
        # ignore the item_id itself
        params = {"search": {"topk": top_n + 1, "vectors": [vec], "params": {}}}

        if search_params is not None:
            params["search"]["params"] = search_params
        #

        try:
            async with self.session.put(
                url=url, data=ujson.dumps(params)
            ) as response:
                # Milvus API has a bad-formatted headers so
                # the default aiohttp decoder cant
                data = await response.json(content_type=None)
        except TimeoutError:
            HTTPException(
                status_code=503, detail="Milvus DB connection timeout"
            )

        if not data:
            return

        if data.get("code"):
            raise HTTPException(status_code=404, detail=data.get("message"))

        records = data.get("result")[0]

        return [
            int(record["id"])
            for record in records
            if int(record["id"]) != item_id
        ]
