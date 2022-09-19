# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\relationship_enums.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 2624 bytes
import enum

class RelationshipBitCullingPrevention(enum.Int):
    ALLOW_ALL = ...
    PLAYED_ONLY = ...
    PLAYED_AND_UNPLAYED = ...


class RelationshipDecayMetricKeys(enum.Int, export=False):
    RELS = ...
    RELS_WITH_DECAY = ...
    LONG_TERM_TRACKS = ...
    LONG_TERM_TRACKS_DECAYING = ...
    LONG_TERM_TRACKS_AT_CONVERGENCE = ...
    SHORT_TERM_TRACKS = ...
    SHORT_TERM_TRACKS_DECAYING = ...
    SHORT_TERM_TRACKS_AT_CONVERGENCE = ...


class RelationshipDirection(enum.Int):
    BIDIRECTIONAL = 0
    UNIDIRECTIONAL = 1


class SentimentSignType(enum.Int):
    INVALID = 0
    POSITIVE = 1
    NEGATIVE = 2


class SentimentDurationType(enum.Int):
    INVALID = 0
    LONG = 1
    SHORT = 2


class RelationshipTrackType(enum.Int, export=False):
    RELATIONSHIP = 0
    SENTIMENT = 1


class RelationshipType(enum.Int):
    NONE = 6
    PARENT = 7
    SIBLING = 8
    SPOUSE = 9
    FIANCE = 10
    DESCENDANT = 12
    GRANDPARENT = 13
    GRANDCHILD = 14
    SIBLINGS_CHILD = 15
    PARENTS_SIBLING = 16
    COUSIN = 17