# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\business\business_tuning.py
# Compiled at: 2020-01-22 21:16:42
# Size of source mod 2**32: 2924 bytes
from business.business_enums import BusinessType, BusinessEmployeeType
from sims4.tuning.tunable_base import ExportModes, EnumBinaryExportType
from sims4.tuning.tunable import TunableMapping, TunableEnumEntry, TunableReference, Tunable, TunableTuple
from vfx import PlayEffect
import services, sims4.resources

class BusinessTuning:
    BUSINESS_TYPE_TO_BUSINESS_DATA_MAP = TunableMapping(description='\n        A mapping of business types to the business tuning for that type.\n        ',
      key_type=TunableEnumEntry(description='\n            The business type to map to reference to business tuning.\n            ',
      tunable_type=BusinessType,
      default=(BusinessType.INVALID),
      invalid_enums=(
     BusinessType.INVALID,),
      binary_type=(EnumBinaryExportType.EnumUint32)),
      key_name='Business Type',
      value_type=TunableReference(description='\n            A reference to the Business tuning that corresponds to the tuned Business Type.\n            ',
      manager=(services.get_instance_manager(sims4.resources.Types.BUSINESS)),
      pack_safe=True),
      value_name='Business Tuning',
      tuple_name='BusinessTypeDataMap',
      export_modes=(ExportModes.All))
    LEGACY_RETAIL_ADDITIONAL_SLOT_EMPLOYEE_TYPE = TunableEnumEntry(description='\n            Set the default employee type that gain the additional employee\n            slot when loading legacy retail saves.\n            ',
      tunable_type=BusinessEmployeeType,
      default=(BusinessEmployeeType.INVALID),
      invalid_enums=(
     BusinessEmployeeType.INVALID,))


class TunableStarRatingVfxMapping(TunableMapping):

    def __init__(self, **kwargs):
        (super().__init__)(key_name='Customer Star Rating', 
         key_type=Tunable(description='\n                The current star rating for the customer.\n                ',
  tunable_type=int,
  default=1), 
         value_name='Star VFX', 
         value_type=TunableTuple(description='\n                The various VFX to play for this star rating.\n                ',
  initial_vfx=PlayEffect.TunableFactory(description='\n                    VFX to play when the star rating is first applied to the customer.\n                    '),
  rating_change_vfx=PlayEffect.TunableFactory(description='\n                    VFX to play when a typical star rating change occurs.\n                    ')), **kwargs)