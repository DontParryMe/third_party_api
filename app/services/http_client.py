import aiohttp
import ssl
import certifi
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Any, Dict, Optional
from ..core import logger


class HTTPClient:
    def __init__(self, base_url: str, timeout: int = 5, default_headers: Optional[Dict[str, str]] = None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.default_headers = default_headers or {}
        self._logger = logger.get_logger("HTTPClient")
        self.ssl_context = ssl.create_default_context(cafile=certifi.where())

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=5),
        retry=(retry_if_exception_type(aiohttp.ClientResponseError) | retry_if_exception_type(aiohttp.ClientError)),
        reraise=True,
    )
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int | float] = None,
    ) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        final_headers = {**self.default_headers, **(headers or {})}
        _timeout = timeout or self.timeout

        try:
            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(
                headers=final_headers, timeout=aiohttp.ClientTimeout(total=_timeout), connector=connector
            ) as session:
                async with session.get(url, params=params) as response:
                    if response.status >= 400:
                        text = await response.text()
                        self._logger.warning(f"GET {url} failed: {response.status} - {text}")
                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=response.status,
                            message=text,
                            headers=response.headers,
                        )

                    self._logger.info(f"GET {url} success: {response.status}")
                    return await response.json()

        except aiohttp.ClientError as e:
            self._logger.warning(f"GET {url} encountered client error: {e}")
            raise
