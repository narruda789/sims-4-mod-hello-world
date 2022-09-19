# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\routing\portals\buildbuy_telemetry.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 1151 bytes
import sims4.log, telemetry_helper
from sims4.telemetry import TelemetryWriter
TELEMETRY_GROUP_BUILD_BUY = 'BDBY'
TELEMETRY_HOOK_OPENABLE_WINDOW = 'WOPN'
TELEMETRY_OBJECT_DEF_ID = 'owid'
TELEMETRY_OPENABLE_WINDOW_COUNT = 'nmow'
buildbuy_telemetry_writer = TelemetryWriter(TELEMETRY_GROUP_BUILD_BUY)
logger = sims4.log.Logger('PortalTelemetry', default_owner='yecao')

def write_portal_telemetry(hook_tag, obj_def_id, routable_window_count):
    logger.debug('{}: {}: {} successfully generated portal', hook_tag, obj_def_id, routable_window_count)
    with telemetry_helper.begin_hook(buildbuy_telemetry_writer, hook_tag) as (hook):
        hook.write_int(TELEMETRY_OBJECT_DEF_ID, obj_def_id)
        hook.write_int(TELEMETRY_OPENABLE_WINDOW_COUNT, routable_window_count)