from typing import Dict, Any, Optional, List

from loguru import logger

from mapadroid.data_handler.AbstractWorkerHolder import AbstractWorkerHolder
from mapadroid.data_handler.mitm_data.holder.LatestMitmDataHolder import LatestMitmDataHolder, LatestMitmDataHolderEntry
from mapadroid.utils.collections import Location


class PlayerData(AbstractWorkerHolder):
    def __init__(self, origin: str, application_args):
        super().__init__(origin)
        self.__application_args = application_args
        self._level: int = 0
        self._poke_stop_visits: int = 0
        self._injected: bool = False
        self._latest_data_holder: LatestMitmDataHolder = LatestMitmDataHolder(self._worker)
        # Cell IDs seen in the last GMO to be able to tell when a GMO of a different location has been received
        self.__last_cell_ids: List = []
        # Timestamp when the GMO last contained different cell IDs than the GMO before that
        self.__last_possibly_moved: int = 0

    # TODO: Move to MappingManager?
    async def set_injection_status(self, status: bool):
        self._injected = status

    async def get_injection_status(self) -> bool:
        return self._injected

    async def __set_level(self, level: int) -> None:
        if self._level != level:
            logger.info('set level {}', level)
            self._level = int(level)
        # TODO: Commit to DB

    async def get_level(self) -> int:
        return self._level

    async def __set_poke_stop_visits(self, visits: int) -> None:
        logger.debug2('set pokestops visited {}', visits)
        self._poke_stop_visits = visits
        # TODO: DB...

    async def get_poke_stop_visits(self) -> int:
        return self._poke_stop_visits

    async def gen_player_stats(self, data: dict) -> None:
        if 'inventory_delta' not in data:
            logger.debug2('gen_player_stats cannot generate new stats')
            return
        stats = data['inventory_delta'].get("inventory_items", None)
        if len(stats) > 0:
            for data_inventory in stats:
                player_stats = data_inventory['inventory_item_data']['player_stats']
                player_level = player_stats['level']
                if int(player_level) > 0:
                    logger.debug2('{{gen_player_stats}} saving new playerstats')
                    await self.__set_level(int(player_level))
                    await self.__set_poke_stop_visits(int(player_stats['poke_stop_visits']))
                    return

    async def get_specific_latest_data(self, key: str) -> LatestMitmDataHolderEntry:
        return self._latest_data_holder.get_latest(key)

    async def get_full_latest_data(self) -> Dict[str, LatestMitmDataHolderEntry]:
        return self._latest_data_holder.get_all()

    async def update_latest(self, key: str, value: Any, timestamp_received: Optional[int] = None,
                            timestamp_of_data_retrieval: Optional[int] = None,
                            location: Optional[Location] = None) -> None:
        self._latest_data_holder.update(key, value, timestamp_received, timestamp_of_data_retrieval, location)
        if key == "106":
            self.__parse_gmo_for_location(value, timestamp_received)

    async def get_last_possibly_moved(self) -> int:
        return self.__last_possibly_moved

    # TODO: Call it from within update_latest accordingly rather than externally...
    def __parse_gmo_for_location(self, gmo_payload: Dict, timestamp: int):
        cells = gmo_payload.get("cells", None)
        if not cells:
            return

        if bool(set(cells).intersection(self.__last_cell_ids)):
            self.__last_cell_ids = cells
            self.__last_possibly_moved = timestamp
        logger.debug4("Done __parse_gmo_for_location with {}", cells)
