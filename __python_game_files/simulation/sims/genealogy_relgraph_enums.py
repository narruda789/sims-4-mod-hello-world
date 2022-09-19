# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\genealogy_relgraph_enums.py
# Compiled at: 2022-02-09 13:21:47
# Size of source mod 2**32: 2163 bytes
import enum

class SimRelBitShift(enum.Int, export=False):
    SIMRELEBITSHIFT_MOTHER = 0
    SIMRELEBITSHIFT_FATHER = 1
    SIMRELEBITSHIFT_DAUGHTER = 2
    SIMRELEBITSHIFT_SON = 3
    SIMRELEBITSHIFT_WIFE = 4
    SIMRELEBITSHIFT_HUSBAND = 5
    SIMRELEBITSHIFT_FIANCEE = 6
    SIMRELEBITSHIFT_FIANCE = 7
    SIMRELEBITSHIFT_MAX = 7
    SIMRELEBITSHIFT_PREEXISTING = 31


class SimRelBitFlags(enum.IntFlags, export=False):
    SIMRELBITFLAG_NONE = 0
    SIMRELBITFLAG_MOTHER = 1 << SimRelBitShift.SIMRELEBITSHIFT_MOTHER
    SIMRELBITFLAG_FATHER = 1 << SimRelBitShift.SIMRELEBITSHIFT_FATHER
    SIMRELBITFLAG_DAUGHTER = 1 << SimRelBitShift.SIMRELEBITSHIFT_DAUGHTER
    SIMRELBITFLAG_SON = 1 << SimRelBitShift.SIMRELEBITSHIFT_SON
    SIMRELBITFLAG_WIFE = 1 << SimRelBitShift.SIMRELEBITSHIFT_WIFE
    SIMRELBITFLAG_HUSBAND = 1 << SimRelBitShift.SIMRELEBITSHIFT_HUSBAND
    SIMRELBITFLAG_FIANCEE = 1 << SimRelBitShift.SIMRELEBITSHIFT_FIANCEE
    SIMRELBITFLAG_FIANCE = 1 << SimRelBitShift.SIMRELEBITSHIFT_FIANCE
    SIMRELBITFLAG_PREEXISTING = 1 << SimRelBitShift.SIMRELEBITSHIFT_PREEXISTING
    SIMRELBITS_MALE = SIMRELBITFLAG_FATHER | SIMRELBITFLAG_SON | SIMRELBITFLAG_HUSBAND | SIMRELBITFLAG_FIANCE
    SIMRELBITS_FEMALE = SIMRELBITFLAG_MOTHER | SIMRELBITFLAG_DAUGHTER | SIMRELBITFLAG_WIFE | SIMRELBITFLAG_FIANCEE
    SIMRELBITS_CHILD = SIMRELBITFLAG_DAUGHTER | SIMRELBITFLAG_SON
    SIMRELBITS_PARENT = SIMRELBITFLAG_MOTHER | SIMRELBITFLAG_FATHER
    SIMRELBITS_SPOUSE = SIMRELBITFLAG_WIFE | SIMRELBITFLAG_HUSBAND
    SIMRELBITS_FIANCE = SIMRELBITFLAG_FIANCE | SIMRELBITFLAG_FIANCEE
    SIMRELBITS_ALL = SIMRELBITS_CHILD | SIMRELBITS_PARENT | SIMRELBITS_SPOUSE | SIMRELBITS_FIANCE