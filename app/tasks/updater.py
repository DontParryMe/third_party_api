import asyncio

from ..core import logger


class BackgroundUpdater:
    def __init__(self, service, interval_seconds: int = 3600):
        self.service = service
        self.interval = interval_seconds
        self._stop_event = asyncio.Event()

    async def start(self):
        logger.get_logger(__name__).info("Background updater started")
        try:
            while not self._stop_event.is_set():
                try:
                    await self._run_once()
                except Exception as e:
                    logger.get_logger(__name__).error("Error in background updater", exc_info=e)

                try:
                    await asyncio.wait_for(self._stop_event.wait(), timeout=self.interval)
                except asyncio.TimeoutError:
                    continue

        except asyncio.CancelledError:
            logger.get_logger(__name__).info("Background updater cancelled")
            raise
        finally:
            logger.get_logger(__name__).info("Background updater stopped")

    async def stop(self):
        self._stop_event.set()

    async def _run_once(self):
        await self.service.update_data()
        logger.get_logger(__name__).info("Background updater finished one cycle")
