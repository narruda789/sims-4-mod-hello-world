# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\tutorials\tutorial.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 9808 bytes
from distributor.ops import OpenTutorial
from distributor.system import Distributor
from event_testing import tests_with_data
from interactions.utils.interaction_elements import XevtTriggeredElement
from relationships.relationship_tests import TunableRelationshipTest
from sims4.localization import TunableLocalizedString
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableTuple, TunableResourceKey, TunableList, TunableReference, TunableVariant, Tunable, TunableEnumEntry, HasTunableFactory, AutoFactoryInit, OptionalTunable
from sims4.tuning.tunable_base import ExportModes
import aspirations.aspiration_tests, enum, event_testing, gameplay_scenarios.scenario_tests, objects.object_tests, services, sims4, sims.sim_info_tests, statistics.skill_tests, world.world_tests

class TunableTutorialTestVariant(TunableVariant):

    def __init__(self, description='A tunable test supported for use as an objective.', **kwargs):
        (super().__init__)(statistic=event_testing.statistic_tests.StatThresholdTest.TunableFactory(), skill_tag=statistics.skill_tests.SkillTagThresholdTest.TunableFactory(), 
         trait=sims.sim_info_tests.TraitTest.TunableFactory(), 
         relationship=TunableRelationshipTest(), 
         object_purchase_test=objects.object_tests.ObjectPurchasedTest.TunableFactory(), 
         simoleon_value=event_testing.test_variants.TunableSimoleonsTest(), 
         event_ran=event_testing.test_variants.EventRanSuccessfullyTest.TunableFactory(), 
         familial_trigger_test=tests_with_data.TunableFamilyAspirationTriggerTest(), 
         situation_running_test=event_testing.test_variants.TunableSituationRunningTest(), 
         crafted_item=objects.object_tests.CraftedItemTest.TunableFactory(), 
         motive=event_testing.statistic_tests.MotiveThresholdTest.TunableFactory(), 
         collection_test=event_testing.test_variants.TunableCollectionThresholdTest(), 
         ran_away_action_test=tests_with_data.TunableParticipantRanAwayActionTest(), 
         ran_interaction_test=tests_with_data.TunableParticipantRanInteractionTest(), 
         started_interaction_test=tests_with_data.TunableParticipantStartedInteractionTest(), 
         unlock_earned=event_testing.test_variants.TunableUnlockedTest(), 
         simoleons_earned=tests_with_data.TunableSimoleonsEarnedTest(), 
         household_size=event_testing.test_variants.HouseholdSizeTest.TunableFactory(), 
         has_buff=sims.sim_info_tests.BuffTest.TunableFactory(), 
         selected_aspiration_test=aspirations.aspiration_tests.SelectedAspirationTest.TunableFactory(), 
         selected_aspiration_track_test=aspirations.aspiration_tests.SelectedAspirationTrackTest.TunableFactory(), 
         object_criteria=objects.object_tests.ObjectCriteriaTest.TunableFactory(), 
         location=world.world_tests.LocationTest.TunableFactory(), 
         buff_added=sims.sim_info_tests.BuffAddedTest.TunableFactory(), 
         has_career=event_testing.test_variants.HasCareerTestFactory.TunableFactory(), 
         career_promotion=event_testing.test_variants.CareerPromotedTest.TunableFactory(), 
         lot_owner=event_testing.test_variants.LotOwnerTest.TunableFactory(), 
         satisfaction_points=sims.sim_info_tests.SatisfactionPointTest.TunableFactory(), 
         scenario_goal_completed=gameplay_scenarios.scenario_tests.ScenarioGoalCompletedTest.TunableFactory(), 
         scenario_phase_triggered=gameplay_scenarios.scenario_tests.ScenarioPhaseTriggeredTest.TunableFactory(), 
         export_modes=ExportModes.ServerXML, 
         description=description, **kwargs)


class TutorialPlatformFilter(enum.Int):
    ALL_PLATFORMS = 0
    DESKTOP_ONLY = 1
    CONSOLE_ONLY = 2


class TunableTutorialSlideTuple(TunableTuple):

    def __init__(self, **kwargs):
        (super().__init__)(description='The text for this slide.', text=TunableLocalizedString(), 
         image=TunableResourceKey(description='\n                             The image for this slide.\n                             ',
  default=None,
  resource_types=(sims4.resources.CompoundTypes.IMAGE)), 
         platform_filter=TunableEnumEntry(description='\n                            The platforms on which this slide is shown.\n                            ',
  tunable_type=TutorialPlatformFilter,
  default=(TutorialPlatformFilter.ALL_PLATFORMS),
  export_modes=(ExportModes.ClientBinary)), 
         image_console=TunableResourceKey(description='\n                             The image for this slide on console.  If unset the Image will be used as a fallback.\n                             ',
  default=None,
  allow_none=True,
  resource_types=(sims4.resources.CompoundTypes.IMAGE),
  display_name='Image (Console)',
  export_modes=(ExportModes.ClientBinary)), 
         image_console_jp=TunableResourceKey(description='\n                             The image for this slide on console for the JP SKU.  Fallback order is: Image (Console), Image.\n                             ',
  default=None,
  allow_none=True,
  resource_types=(sims4.resources.CompoundTypes.IMAGE),
  display_name='Image (Console; JP)',
  export_modes=(ExportModes.ClientBinary)), **kwargs)


class TutorialCategory(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.TUTORIAL)):
    INSTANCE_TUNABLES = {'name': TunableLocalizedString(description='\n            Name of the tutorial category.\n            ',
               export_modes=(ExportModes.All))}


class Tutorial(metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.TUTORIAL)):
    INSTANCE_TUNABLES = {'name':TunableLocalizedString(description='\n            Name of the tutorial. i.e. if this is a tutorial about Build/Buy\n            you might put "Build Buy Mode"\n            ',
       export_modes=ExportModes.ClientBinary), 
     'category':TunableReference(description='\n            The tutorial category in which this tutorial belongs.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.TUTORIAL),
       class_restrictions=TutorialCategory,
       export_modes=ExportModes.ClientBinary), 
     'slides':TunableList(description='\n            These are the slides (images with a description) that create the\n            story for this tutorial. They will be shown in the order they are\n            provided, so the first slide in this list will be the first slide\n            of the tutorial.\n            ',
       tunable=TunableTutorialSlideTuple(),
       export_modes=ExportModes.ClientBinary), 
     'ui_sort_order':Tunable(description='\n            Order in which this tutorial is sorted against other tutorials in \n            its category in the UI. If two tutorials in a category share the \n            same sort order, undefined behavior will occur.\n            ',
       tunable_type=int,
       default=0,
       export_modes=ExportModes.ClientBinary)}


class TutorialOpenElement(XevtTriggeredElement, HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'tutorial': OptionalTunable(description='\n            If enabled, we open the tutorial selected here, otherwise we open the default tutorial.\n            ',
                   tunable=TunableReference(description='\n                The tutorial that we want to open.\n                ',
                   manager=(services.get_instance_manager(sims4.resources.Types.TUTORIAL)),
                   class_restrictions=Tutorial))}

    def _do_behavior(self):
        op = OpenTutorial(self.tutorial.guid64 if self.tutorial is not None else None)
        Distributor.instance().add_op_with_no_owner(op)
        return True