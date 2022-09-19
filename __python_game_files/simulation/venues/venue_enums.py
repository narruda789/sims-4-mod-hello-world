# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\venues\venue_enums.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 864 bytes
import enum

class VenueTypes(enum.Int):
    STANDARD = 0
    RESIDENTIAL = 1
    RENTAL = 2
    RESTAURANT = 3
    RETAIL = 4
    VET_CLINIC = 5
    UNIVERSITY_HOUSING = 6
    WEDDING = 7


class VenueFlags(enum.IntFlags):
    NONE = 0
    WATER_LOT_RECOMMENDED = 1
    VACATION_TARGET = 2
    SUPPRESSES_LOT_INFO_PANEL = 4


class TierBannerAppearanceState(enum.Int):
    INVALID = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3