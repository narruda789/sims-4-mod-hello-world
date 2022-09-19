# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\clubs\club_telemetry.py
# Compiled at: 2015-10-15 14:37:48
# Size of source mod 2**32: 1061 bytes
import sims4.telemetry
TELEMETRY_GROUP_CLUBS = 'CLUB'
TELEMETRY_HOOK_CLUB_JOIN = 'CLBJ'
TELEMETRY_HOOK_CLUB_QUIT = 'CLBQ'
TELEMETRY_HOOK_CLUB_CREATE = 'CLBC'
TELEMETRY_HOOK_CLUB_BUCKSEARNED = 'CLBE'
TELEMETRY_HOOK_CLUB_PERKPURCHASED = 'CLPP'
TELEMETRY_HOOK_CLUB_OVERVIEW = 'CLOV'
TELEMETRY_HOOK_CLUB_COUNT = 'CLCT'
TELEMETRY_FIELD_CLUB_ID = 'clid'
TELEMETRY_FIELD_CLUB_BUCKSAMOUNT = 'clba'
TELEMETRY_FIELD_CLUB_PERKID = 'clpi'
TELEMETRY_FIELD_CLUB_PERKCOST = 'clps'
TELEMETRY_FIELD_CLUB_TOTALCLUBS = 'cltc'
TELEMETRY_FILED_CLUB_PCS = 'clpc'
TELEMETRY_FIELD_CLUB_NPCS = 'clnp'
TELEMETRY_FIELD_CLUB_NUMRULES = 'clnr'
TELEMETRY_FIELD_CLUB_HANGOUTVENUE = 'venu'
TELEMETRY_FIELD_CLUB_HANGOUTLOT = 'hlid'
TELEMETRY_FIELD_CLUB_HANGOUTSETTING = 'clhs'
TELEMETRY_FIELD_CLUB_AMOUNTEARNED = 'clae'
TELEMETRY_FIELD_CLUB_TOTALAMOUNTEARNED = 'clba'
club_telemetry_writer = sims4.telemetry.TelemetryWriter(TELEMETRY_GROUP_CLUBS)