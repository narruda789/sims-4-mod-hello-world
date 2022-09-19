# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\gsi_utils.py
# Compiled at: 2018-03-26 14:38:10
# Size of source mod 2**32: 1162 bytes
from sims4.tuning.instances import TunedInstanceMetaclass
import sims

def format_object_name(obj):
    if not isinstance(type(obj), TunedInstanceMetaclass):
        return str(obj)
    if isinstance(obj, sims.sim.Sim):
        return obj.full_name
    name = type(obj).__name__
    obj_str = str(obj)
    if name in obj_str:
        return name
    return '{0} ({1})'.format(name, obj_str)


def format_object_list_names(items):
    return ', '.join((format_object_name(item) for item in items))


def format_enum_name(enum_val):
    return str(enum_val).split('.')[(-1)]


def parse_filter_to_list(filter):
    filter_list = None
    if filter is not None:
        filter_list = filter.split(',')
    return filter_list