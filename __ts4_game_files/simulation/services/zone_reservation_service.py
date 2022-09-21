# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\services\zone_reservation_service.py
# Compiled at: 2021-04-02 19:35:11
# Size of source mod 2**32: 3138 bytes
from _weakrefset import WeakSet
from collections import defaultdict
import sims4
from sims4.service_manager import Service
logger = sims4.log.Logger('Zone Reservation', default_owner='rrodgers')

class ZoneReservationService(Service):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)
        self._reserved_zones = defaultdict(WeakSet)

    def start(self):
        return True

    def on_zone_load(self):
        pass

    def on_zone_unload(self):
        pass

    def stop(self):
        pass

    def is_reserved(self, zone_id):
        reservations = self._reserved_zones.get(zone_id, None)
        return bool(reservations and len(reservations))

    def reserve_zone(self, reserver, zone_id):
        current_reservations = self._reserved_zones.get(zone_id, None)
        if current_reservations:
            if reserver in current_reservations:
                logger.warn('Zone with id {} is being reserved by {} which already has a reservation for it.', zone_id, reserver)
                return
        self._reserved_zones[zone_id].add(reserver)

    def unreserve_zone(self, reserver, zone_id):
        current_reservations = self._reserved_zones.get(zone_id, None)
        if not current_reservations:
            logger.warn("Trying to unreserve a zone that isn't reserved")
            return
        if reserver not in current_reservations:
            logger.warn('{} is trying to unreserve a zone ({}) but no reservation was found', reserver, zone_id)
            return
        current_reservations.remove(reserver)
        if not current_reservations:
            del self._reserved_zones[zone_id]