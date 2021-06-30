from typing import List, Optional, Dict, Tuple

from mapadroid.db.helper.TrsSpawnHelper import TrsSpawnHelper
from mapadroid.db.model import TrsSpawn, TrsEvent
from mapadroid.madmin.AbstractMadminRootEndpoint import AbstractMadminRootEndpoint
from mapadroid.madmin.functions import get_bound_params
from mapadroid.utils.collections import Location


class GetSpawnsEndpoint(AbstractMadminRootEndpoint):
    """
    "/get_spawns"
    """

    # TODO: Auth
    async def get(self):
        ne_lat, ne_lng, sw_lat, sw_lng, o_ne_lat, o_ne_lng, o_sw_lat, o_sw_lng = get_bound_params(self._request)
        timestamp: Optional[int] = self._request.query.get("timestamp")
        if timestamp:
            timestamp = int(timestamp)

        coords: Dict[str, List[Dict]] = {}
        data: Dict[int, Tuple[TrsSpawn, TrsEvent]] = \
            await TrsSpawnHelper.download_spawns(self._session,
                                                 ne_corner=Location(ne_lat, ne_lng), sw_corner=Location(sw_lat, sw_lng),
                                                 old_ne_corner=Location(o_ne_lat, o_ne_lng),
                                                 old_sw_corner=Location(o_sw_lat, o_sw_lng),
                                                 timestamp=timestamp)

        for (spawn_id, (spawn, event)) in data.items():
            if event.event_name not in coords:
                coords[event.event_name] = []
            coords[event.event_name].append({
                "id": spawn_id,
                "endtime": spawn.calc_endminsec,
                "lat": spawn.latitude,
                "lon": spawn.longitude,
                "spawndef": spawn.spawndef,
                "lastnonscan": spawn.last_non_scanned.strftime(
                    self._datetimeformat) if spawn.last_non_scanned else None,
                "lastscan": spawn.last_scanned.strftime(self._datetimeformat) if spawn.last_scanned else None,
                "first_detection": spawn.first_detection.strftime(self._datetimeformat),
                "event": event.event_name
            })

        cluster_spawns = []
        for spawn in coords:
            cluster_spawns.append({"EVENT": spawn, "Coords": coords[spawn]})

        return self._json_response(cluster_spawns)
