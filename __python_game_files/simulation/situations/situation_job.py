# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\situations\situation_job.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 68204 bytes
import collections, random
from event_testing.resolver import DoubleSimResolver
from filters.location_based_filter_terms import TunableLocationBasedFilterTermsSnippet
from filters.tunable import TunableSimFilter
from interactions import ParticipantType
from interactions.utils.localization_tokens import LocalizationTokens
from interactions.utils.loot import WeightedSingleSimLootActions, LootActions
from interactions.utils.success_chance import SuccessChance
from interactions.utils.tunable import SetGoodbyeNotificationElement
from rewards.reward import Reward
from sims.outfits.outfit_enums import OutfitChangeReason, DefaultOutfitPriority, BodyType
from sims.outfits.outfit_generator import TunableOutfitGeneratorReference
from sims4.localization import TunableLocalizedString, TunableLocalizedStringFactory
from sims4.random import weighted_random_item
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import TunableInterval, TunableList, TunableResourceKey, TunableReference, Tunable, TunableMapping, TunableSet, TunableEnumEntry, TunableTuple, HasDependentTunableReference, OptionalTunable, TunableSimMinute, AutoFactoryInit, HasTunableSingletonFactory, TunableRange, TunableEnumWithFilter, TunableVariant, TunablePercent
from sims4.tuning.tunable_base import ExportModes, GroupNames, FilterTag
from singletons import DEFAULT
from situations.bouncer.bouncer_types import BouncerRequestPriority
from situations.situation_types import SituationMedal
from statistics.statistic_ops import TunableStatisticChange
from tag import Tag, SPAWN_PREFIX
from ui.ui_dialog_notification import TunableUiDialogNotificationSnippet
from venues.venue_object_test import TunableVenueObject
from world.spawn_actions import TunableSpawnActionVariant
from world.spawn_point import SpawnPointOption
import clock, enum, event_testing.test_variants, event_testing.tests_with_data, interactions.base.super_interaction, objects.object_tests, services, sims4.log, sims4.resources, situations.situation_types
logger = sims4.log.Logger('Situations')
AutoPopulateInterval = collections.namedtuple('AutoPopulateInterval', ['min', 'max'])

class JobChurnOperation(enum.Int, export=False):
    DO_NOTHING = 0
    ADD_SIM = 1
    REMOVE_SIM = 2


class JobLootTargetChoice(enum.Int):
    RANDOM_SIM = 0
    ALL_SIMS_IN_JOB = 2


class SituationJobChurn(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'min_duration':TunableSimMinute(description='\n                Minimum amount of time a sim in this job will stay before they\n                might be churned out.\n                ',
       default=60), 
     'auto_populate_by_time_of_day':TunableMapping(description="\n                Each entry in the map has two columns.\n                The first column is the hour of the day (0-24) \n                that this entry begins to control the number of sims in the job.\n                The second column is the minimum and maximum desired number\n                of sims.\n                The entry with starting hour that is closest to, but before\n                the current hour will be chosen.\n                \n                Given this tuning: \n                    beginning_hour        desired_population\n                    6                     1-3\n                    10                    3-5\n                    14                    5-7\n                    20                    7-9\n                    \n                if the hour is 11, beginning_hour will be 10 and desired is 3-5.\n                if the hour is 19, beginning_hour will be 14 and desired is 5-7.\n                if the hour is 23, beginning_hour will be 20 and desired is 7-9.\n                if the hour is 2, beginning_hour will be 20 and desired is 7-9. (uses 20 tuning because it is not 6 yet)\n                \n                The entries will be automatically sorted by time on load, so you\n                don't have to put them in order (but that would be nutty)\n                ",
       key_type=Tunable(tunable_type=int,
       default=0),
       value_type=TunableInterval(tunable_type=int,
       default_lower=0,
       default_upper=0),
       key_name='beginning_hour',
       value_name='desired_population'), 
     'chance_to_add_or_remove_sim':TunableRange(description='\n                Periodically the churn system will re-evaluate the number of sims\n                currently in the job. If the number of sims is above or below\n                the range it will add/remove one sim as appropriate. \n                If the number of sims is within the tuned\n                range it will roll the dice to determine what it should do:\n                    nothing\n                    add a sim\n                    remove a sim\n                    \n                The chance tuned here (1-100) is the chance that it will do\n                something (add/remove), as opposed to nothing. \n                \n                When it is going to do something, the determination of \n                whether to add or remove is roughly 50/50 with additional\n                checks to stay within the range of desired sims and respect the\n                min duration.\n                ',
       tunable_type=int,
       default=20,
       minimum=0,
       maximum=100)}

    def get_auto_populate_interval(self, time_of_day=None):
        if not self.auto_populate_by_time_of_day:
            return AutoPopulateInterval(min=0, max=0)
        if time_of_day is None:
            time_of_day = services.time_service().sim_now
        auto_populate = []
        for beginning_hour, interval in self.auto_populate_by_time_of_day.items():
            auto_populate.append((beginning_hour, interval))

        auto_populate.sort(key=(lambda entry: entry[0]))
        hour_of_day = time_of_day.hour()
        entry = auto_populate[(-1)]
        interval = AutoPopulateInterval(min=(entry[1].lower_bound), max=(entry[1].upper_bound))
        for entry in auto_populate:
            if entry[0] <= hour_of_day:
                interval = AutoPopulateInterval(min=(entry[1].lower_bound), max=(entry[1].upper_bound))
            else:
                break

        return interval


class SituationJobShifts(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'shift_times_and_staffing': TunableMapping(description='\n                Each entry in the map has two columns.\n                The first column is the hour of the day (0-24) \n                that this shift starts.\n                The second column is the number of sims in that shift.\n                The entry with starting hour that is closest to, but before\n                the current hour will be chosen.\n                \n                Given this tuning: \n                    beginning_hour        staffing\n                    2                     0\n                    6                     1\n                    14                    2\n                    20                    2\n                    \n                2am is a shift change that sends everybody home\n                6am is a shift change that brings in 1 employee\n                2pm is a shift change that sends the current employee home and brings in 2 new ones.\n                8pm is a shift change that sends the 2 employees home and brings in 2 new ones. \n                \n                The entries will be automatically sorted by time at runtime.\n                ',
                                   key_type=Tunable(tunable_type=int,
                                   default=0),
                                   value_type=Tunable(tunable_type=int,
                                   default=0),
                                   key_name='beginning_hour',
                                   value_name='staffing')}

    def get_sorted_shift_times(self):
        staffing = []
        for beginning_hour, number in self.shift_times_and_staffing.items():
            staffing.append((beginning_hour, number))

        staffing.sort(key=(lambda entry: entry[0]))
        return staffing

    def get_shift_staffing(self, time_of_day=None):
        if not self.shift_times_and_staffing:
            return 0
        if time_of_day is None:
            time_of_day = services.time_service().sim_now
        staffing_times = self.get_sorted_shift_times()
        hour_of_day = time_of_day.hour()
        entry = staffing_times[(-1)]
        number_of_sims = entry[1]
        for entry in staffing_times:
            if entry[0] <= hour_of_day:
                number_of_sims = entry[1]
            else:
                break

        return number_of_sims

    def get_time_span_to_next_shift_time(self):
        if not self.shift_times_and_staffing:
            return
        sorted_times = self.get_sorted_shift_times()
        next_shift_hour = sorted_times[0][0]
        now = services.time_service().sim_now
        now_hour = now.hour()
        for shift_hour, _ in sorted_times:
            if shift_hour > now_hour:
                next_shift_hour = shift_hour
                break

        time_span_until = clock.time_until_hour_of_day(now, next_shift_hour)
        return time_span_until


class SituationJobReward(HasTunableSingletonFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'reward':Reward.TunableReference(description='\n                Reward to give when completing this job. Actor is the sim with the job.\n                Target, if any, is determined by the loot_target field.\n                ',
       allow_none=True), 
     'loot':TunableList(description='\n                List of loots to give when completing this job. Actor is the sim with the job.\n                Target, if any, is determined by the loot_target field.\n                ',
       tunable=LootActions.TunableReference()), 
     'loot_target':OptionalTunable(description='\n                If enabled then we will use the tuned situation job to pick a target\n                sim (or sims) in the owning situation with that job to be the target\n                of the loot operation. The loot_target_choice field will determine\n                wheter we apply the loot to a single target (chosen at random) or all\n                the sims in the given job.\n                ',
       tunable=TunableReference(description='\n                    The situation job that will be used to find a sim in the\n                    owning situation to be the target sim.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)))), 
     'loot_target_choice':TunableEnumEntry(description='\n                Behavior of how loot is distributed if there are multiple target sims.\n                ',
       tunable_type=JobLootTargetChoice,
       default=JobLootTargetChoice.RANDOM_SIM)}

    def _apply_loot(self, sim, situation):
        if self.loot_target_choice == JobLootTargetChoice.RANDOM_SIM:
            target_sim_info = None
            if self.loot_target is not None:
                possible_sims = list(situation.all_sims_in_job_gen(self.loot_target))
                if possible_sims:
                    target_sim_info = random.choice(possible_sims)
                if target_sim_info is None:
                    return
            resolver = DoubleSimResolver(sim.sim_info, target_sim_info)
            for loot_entry in self.loot:
                if loot_entry is not None:
                    loot_entry.apply_to_resolver(resolver)

        else:
            if self.loot_target_choice == JobLootTargetChoice.ALL_SIMS_IN_JOB and self.loot_target is not None:
                for target_sim_info in situation.all_sims_in_job_gen(self.loot_target):
                    resolver = DoubleSimResolver(sim.sim_info, target_sim_info)
                    for loot_entry in self.loot:
                        if loot_entry is not None:
                            loot_entry.apply_to_resolver(resolver)

    def _apply_reward(self, sim):
        self.reward.give_reward(sim.sim_info)

    def apply(self, sim, situation):
        if self.loot is not None:
            self._apply_loot(sim, situation)
        if self.reward is not None:
            self._apply_reward(sim)


class SituationJob(HasDependentTunableReference, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)):
    _job_to_weighted_spawn_action_list = None

    @staticmethod
    def _cache_job_to_spawn_action_map(*args):
        if SituationJob._job_to_weighted_spawn_action_list is not None:
            return
        SituationJob._job_to_weighted_spawn_action_list = {}
        for alt_behavior in SituationJob.ALTERNATIVE_SPAWN_BEHAVIOR.alternative_spawn_behaviors:
            if not alt_behavior.spawn_action_list:
                continue
            for job in alt_behavior.whitelist:
                if job not in SituationJob._job_to_weighted_spawn_action_list:
                    SituationJob._job_to_weighted_spawn_action_list[job] = []
                weighted_spawn_action_list = SituationJob._job_to_weighted_spawn_action_list[job]
                for action in alt_behavior.spawn_action_list:
                    weighted_action = (
                     action.weight, action.spawn_action)
                    weighted_spawn_action_list.append(weighted_action)

    CHANGE_OUTFIT_INTERACTION = interactions.base.super_interaction.SuperInteraction.TunableReference(description='\n        A reference that should be tuned to an interaction that will just set\n        sim to their default outfit.\n        ')
    BLACKLIST_FROM_ALL_JOBS_TAG = TunableEnumEntry(description='\n        The tag that is used to blacklist sims from all job types.\n        ',
      tunable_type=Tag,
      default=(Tag.INVALID))
    ALTERNATIVE_SPAWN_BEHAVIOR = TunableTuple(chance_of_using_instance_spawn_action=TunablePercent(description='\n            The percent chance to use the instance defined spawn_action as \n            opposed to an alternative spawn action defined here.\n            ',
      default=90),
      alternative_spawn_behaviors=TunableList(description='\n            A list of (whitelist, spawn_action_list) pairs. The whitelist \n            defines which situation jobs are allowed to run spawn actions from \n            the spawn action list.\n            ',
      tunable=TunableTuple(whitelist=TunableList(description='\n                    The situation jobs which are allowed to run spawn actions\n                    from the spawn action list.\n                    ',
      tunable=TunableReference(description='\n                        A situation job.\n                        ',
      manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_JOB)),
      pack_safe=True)),
      spawn_action_list=TunableList(description='\n                    The list of (spawn_action, weight) pairs.\n                    ',
      tunable=TunableTuple(spawn_action=TunableSpawnActionVariant(description='\n                            A spawn action.\n                            ',
      list_pack_safe=True),
      weight=Tunable(description='\n                            The chance that this spawn action will be chosen\n                            relative to other alternative spawn actions that\n                            are available for a given situation job.\n                            ',
      tunable_type=float,
      default=1)))),
      callback=_cache_job_to_spawn_action_map))
    INSTANCE_TUNABLES = {'display_name':TunableLocalizedString(description='\n                Localized name of this job. This name is displayed in the situation\n                creation UI where the player is making selection of sims that belong\n                to a specific job. E.g. "Guest", "Bride or Groom", "Bartender".\n                \n                Whenever you add a display name, evaluate whether your design \n                needs or calls out for a tooltip_name.\n                ',
       allow_none=True,
       tuning_group=GroupNames.UI), 
     'tooltip_name':TunableLocalizedStringFactory(description='\n                Localized name of this job that is displayed when the player hovers\n                on the sim while the situation is in progress. If this field is absent, \n                there will be no tooltip on the sim.\n                \n                This helps distinguish the cases where we want to display "Bride or Groom" \n                in the situation creation UI but only "Bride" or "Groom" on the \n                sim\'s tooltip when the player is playing with the situation.\n                ',
       allow_none=True,
       tuning_group=GroupNames.UI), 
     'user_facing_sim_headline_display_override':Tunable(description="\n                If checked then the sim headline will be displayed on sims with\n                this job even if that sim isn't part of a user facing\n                situation.\n                \n                Ex: Active Careers where we want to show the jobs of patients,\n                co-workers, and the like but they aren't actually part of the\n                user facing active career sitaution.\n                ",
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.UI), 
     'tooltip_name_text_tokens':LocalizationTokens.TunableFactory(description="\n                Localization tokens to be passed into 'tooltip_name'.\n                For example, you could use a participant or you could also pass\n                in statistic and commodity values\n                ",
       tuning_group=GroupNames.UI), 
     'icon':TunableResourceKey(description='\n                Icon to be displayed for the job of the Sim\n                ',
       resource_types=sims4.resources.CompoundTypes.IMAGE,
       default=None,
       allow_none=True,
       tuning_group=GroupNames.UI), 
     'job_description':TunableLocalizedString(description='\n                Localized description of this job\n                ',
       allow_none=True,
       tuning_group=GroupNames.UI), 
     'sim_auto_invite':TunableInterval(description="\n                On situation start it will select a random number of sims in this interval.\n                It will automatically add npcs to the situation so that it has at least\n                that many sims in this job including those the player\n                invites/hires. If the player invites/hires more than the auto\n                invite number, no npcs will be automatically added.\n                \n                Auto invite sims are considered to be invited, so they will be\n                spawned for invite only situations too. For player initiated\n                situations you probably want to set this 0. It is really meant\n                for commercial venues.\n                \n                You can use Churn tuning on this job if you want the number of\n                sims to vary over time. Churn tuning will override this one.\n                \n                For example, an ambient bar situation would have a high auto\n                invite number for the customer job because we want many sims in\n                the bar but the player doesn't invite or hire anybody for an\n                ambient situation.\n                \n                A date would have 0 for this for all jobs because the situation\n                would never spawn anybody to fill jobs, the player would have\n                to invite them all.\n                ",
       tunable_type=int,
       default_lower=0,
       default_upper=0,
       minimum=0,
       tuning_group=GroupNames.SIM_AUTO_INVITE), 
     'sim_auto_invite_allow_instanced_sim':Tunable(description='\n                If checked will allow instanced sims to be assigned this job\n                to fulfill auto invite spots instead of forcing the spawning\n                of new sims.\n                \n                NOTE: YOU PROBABLY WANT TO LEAVE THIS AS UNCHECKED.  PLEASE\n                CONSULT A GPE IF YOU PLAN ON TUNING IT.\n                ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SIM_AUTO_INVITE), 
     'accept_looking_for_more_work':Tunable(description='\n                If checked will allow instanced Sims to be assigned this job\n                if those Sims have declared themselves to be looking for new\n                work.  This will overrule any exclusivity rules in place.\n                \n                NOTE: YOU PROBABLY WANT TO LEAVE THIS AS UNCHECKED.  PLEASE\n                CONSULT A GPE IF YOU PLAN ON TUNING IT.\n                ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SIM_AUTO_INVITE), 
     'sim_auto_invite_allow_priority':TunableEnumEntry(description="\n                The Bouncer Request Priority that will be used to auto invite\n                Sims into this situation.\n                \n                Event Auto Fill: This should only be used for user facing\n                situations.\n                \n                Venue Required: Use this for Venue Employees that you want to\n                make sure stay on the lot and don't get pulled into club\n                gatherings or festivals.\n                \n                Background High: Use this for important background events such\n                as Club Gatherings or Festivals.\n                \n                Background Medium: Use this for regular on lot background\n                activities such as bar patrons.\n                \n                Background Low: Use this for regular open street background\n                activities such as walkbys.\n                ",
       tunable_type=BouncerRequestPriority,
       default=BouncerRequestPriority.EVENT_AUTO_FILL,
       invalid_enums=(
      BouncerRequestPriority.GAME_BREAKER,
      BouncerRequestPriority.EVENT_DEFAULT_JOB,
      BouncerRequestPriority.EVENT_VIP,
      BouncerRequestPriority.EVENT_HOSTING),
       tuning_group=GroupNames.SIM_AUTO_INVITE), 
     'sim_auto_invite_use_common_blacklists_on_instanced_sims':Tunable(description='\n                If checked and auto invite allows the usage of instanced Sims\n                we will allow apply the common blacklists when selecting Sims\n                to fill these roles.\n                ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SIM_AUTO_INVITE), 
     'sim_count':TunableInterval(description='\n                The number of Sims the player is allowed to invite or hire for\n                this job.  The lower bound is the required number of sims, the\n                upper bound is the maximum.\n                \n                This only affects what the player can do in the Plan an Event UI.\n                It has no affect while the situation is running.\n                ',
       tunable_type=int,
       default_lower=1,
       default_upper=1,
       minimum=0), 
     'churn':OptionalTunable(description='!!!DEPRECATED!!!\n                Please use zone director functionality to provide the same\n                results.\n            \n                If enabled, produces churn or turnover\n                in the sims holding this job. Periodically sims in the job will leave\n                the lot and other sims will come to fill the job. \n                \n                When a situation is first started it will automatically invite a\n                number of sims appropriate for the time of day. This supercedes\n                sim_auto_invite.\n                \n                This is primarily for commercial venue customers.\n                This is NOT compatible with Sim Shifts.\n                ',
       tunable=SituationJobChurn.TunableFactory(),
       display_name='Sim Churn',
       tuning_group=GroupNames.DEPRECATED), 
     'sim_shifts':OptionalTunable(description='!!!DEPRECATED!!!\n                Please use zone director functionality to provide the same\n                results.\n                \n                If enabled, creates shifts of\n                sims who replace the sims currently in the job.\n                \n                When a situation is first started it will automatically invite a\n                number of sims appropriate for the time of day. This supercedes\n                sim_auto_invite.\n                \n                This is primarily intended for commercial venue employees.\n                This is NOT compatible with Sim Churn.\n                ',
       tunable=SituationJobShifts.TunableFactory(),
       tuning_group=GroupNames.DEPRECATED), 
     'goal_scoring':Tunable(description='\n                The score for completing a goal\n                ',
       tunable_type=int,
       default=1,
       tuning_group=GroupNames.SCORING), 
     'interaction_scoring':TunableList(description='\n                Test for interactions run. Each test can have a separate score.\n                ',
       tunable=TunableTuple(description='\n                    Each affordance that satisfies the test will receive the\n                    same score.\n                    ',
       score=Tunable(description='\n                        Score for passing the test.\n                        ',
       tunable_type=int,
       default=1),
       affordance_list=event_testing.tests_with_data.TunableParticipantRanInteractionTest(locked_args={'participant':ParticipantType.Actor, 
      'tooltip':None, 
      'running_time':None}),
       role_tags=OptionalTunable(description='\n                        If enabled then we will require that the target of the\n                        interaction being scored is a sim and that sim\n                        meets the criteria of the black and whitelists.\n                        ',
       tunable=TunableTuple(whitelist=OptionalTunable(description='\n                                If enabled then we will make sure that the\n                                target sim has at least one of the tags\n                                in the role tags.\n                                ',
       tunable=TunableSet(description='\n                                    The set of role tags that we will check\n                                    against the role tags of the sim.\n                                    ',
       tunable=TunableEnumEntry(description='\n                                        A single role tag to check against.\n                                        ',
       tunable_type=Tag,
       default=(Tag.INVALID),
       pack_safe=True))),
       blacklist=TunableSet(description='\n                                A set of tags that we will not apply the score\n                                if the target sim has one of them.\n                                ',
       tunable=TunableEnumEntry(description='\n                                    A single role tag to check against.\n                                    ',
       tunable_type=Tag,
       default=(Tag.INVALID),
       pack_safe=True))))),
       tuning_group=GroupNames.SCORING), 
     'crafted_object_scoring':TunableList(description='\n                Test for objects crafted. Each test can have a separate score.\n                ',
       tunable=TunableTuple(description='\n                    Test for objects crafted. Each test can have a separate\n                    score.\n                    ',
       score=Tunable(description='\n                        Score for passing the test.\n                        ',
       tunable_type=int,
       default=1),
       object_list=objects.object_tests.CraftedItemTest.TunableFactory(description='\n                        A test to see if the crafted item should give score.\n                        ',
       locked_args={'tooltip': None})),
       tuning_group=GroupNames.SCORING), 
     'rewards':TunableMapping(description='\n                Rewards given to the sim in this job when situation reaches specific medals.\n                ',
       key_type=TunableEnumEntry(SituationMedal, (SituationMedal.TIN), description='\n                    Medal to achieve to get the corresponding benefits.\n                    '),
       value_type=SituationJobReward.TunableFactory(description='\n                    Reward and LootAction benefits for accomplishing the medal.\n                    '),
       key_name='medal',
       value_name='benefit',
       tuning_group=GroupNames.SCORING), 
     'give_rewards_to_npc':Tunable(description='\n                If true we will give this reward to NPCs instead of only to\n                selectable sims.\n                ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SCORING), 
     'filter':TunableReference(manager=services.get_instance_manager(sims4.resources.Types.SIM_FILTER),
       class_restrictions=TunableSimFilter,
       tuning_group=GroupNames.SIM_FILTER), 
     'location_based_filter_terms':TunableList(description='\n                A set of filter terms, based on the current location, that\n                augment the tuned filter. This allows for location-based\n                variations.\n                ',
       tunable=TunableLocationBasedFilterTermsSnippet(pack_safe=True),
       tuning_group=GroupNames.SIM_FILTER), 
     'tags':TunableSet(description='\n                Designer tagging for making the game more fun.\n                ',
       tunable=TunableEnumEntry(tunable_type=Tag,
       default=(Tag.INVALID))), 
     'job_uniform':OptionalTunable(description='\n                If enabled, when a Sim is assigned this situation job, that Sim\n                will switch into their outfit based on the Outfit Category.\n                \n                If the Outfit Category is SITUATION, then an outfit will be\n                generated based on the passed in tags and the Sim will switch\n                into that outfit.\n                ',
       tunable=TunableTuple(description='\n                    ',
       outfit_change_reason=TunableEnumEntry(description='\n                        An enum that represents a reason for outfit change for\n                        the outfit system.\n                        \n                        An outfit change reason is really a series of tests\n                        that are run to determine which outfit category that\n                        we want to switch into.\n                        \n                        In order to do this, add a new OutfitChangeReason entry\n                        in outfit-enums module.\n                        \n                        Then go into\n                        ClothingChangeTunables->Clothing Reasons To Outfits\n                        and add a new entry to the map.\n                        \n                        Set this entry to your new enum entry.\n                        \n                        Then you can add new elements to the list of tests and\n                        outfit categories that you want it to change the sim\n                        into.\n                        ',
       tunable_type=OutfitChangeReason,
       default=(OutfitChangeReason.Invalid)),
       outfit_change_priority=TunableEnumEntry(description='\n                        The outfit change priority.  Higher priority outfit\n                        changes will override lower priority outfit changes.\n                        ',
       tunable_type=DefaultOutfitPriority,
       default=(DefaultOutfitPriority.NoPriority)),
       playable_sims_change_outfits=Tunable(description='\n                        If checked, Playable Sims will change outfit when the job is set for the Sim. This\n                        should be checked on things like user facing events,\n                        but not Venue Background Event Jobs.\n                        ',
       tunable_type=bool,
       default=True),
       zone_custom_outfit=Tunable(description='\n                        If checked, we would request the current zone to give a\n                        special outfit for this job.\n                        ',
       tunable_type=bool,
       default=False),
       use_sold_fashion_outfit=Tunable(description='\n                        If checked, we would request a fashion outfit \n                        that was recently sold as a situation outfit for this job.\n                        ',
       tunable_type=bool,
       default=False),
       situation_outfit_generators=OptionalTunable(description="\n                        If enabled, the situation will use the outfit tags\n                        specified to generate an outfit for the sim's\n                        SITUATION outfit category.  If generating an outfit\n                        make sure to set outfit change reason to something that\n                        will put the sim into the SITUATION outfit category or\n                        you will not have the results that you expect.\n                        ",
       tunable=TunableList(description='\n                            Only one of these items is picked randomly to \n                            select the outfit tags within this list.\n                            E.g. If you want to host a costume party where the \n                            guests show up in either octopus costume or a shark \n                            costume, we would have two sets of tuning that can \n                            specify exclusive tags for the specific costumes. \n                            Thus we avoid accidentally generating a sharktopus \n                            costume.\n                            \n                            If you want your guests to always show up in \n                            sharktopus costumes then tune only one set of tags \n                            that enlist all the outfit tags that are associated \n                            with either shark or octopus.\n                            \n                            If some tags are only compatible with adults, and \n                            no outfit with that tag exists for children you\n                            should add an outfit test for that set of tags\n                            so that only adults can pick out of that item\n                            on the list.\n                            ',
       tunable=TunableTuple(description='\n                                Set of outfit generator and tests that will \n                                be run on the sim to validate if the generator \n                                is valid for this outfit.\n                                ',
       generator=TunableOutfitGeneratorReference(pack_safe=True),
       tests=event_testing.tests.TunableTestSet(description='\n                                    Test set the sim will need to pass to be \n                                    able to wear the outfit correspnding to the \n                                    tuned tags.\n                                    '))))),
       disabled_name='no_uniform',
       enabled_name='uniform_specified'), 
     'apply_weather_based_uniform':Tunable(description='\n                If set (default), will apply weather based uniform.\n                Only applied if no job_uniform tuned.\n                ',
       tunable_type=bool,
       default=True), 
     'can_be_hired':Tunable(description='\n                This job can be hired.\n                ',
       tunable_type=bool,
       default=True), 
     'hire_cost':Tunable(description='\n                The cost to hire a Sim for this job in Simoleons.\n                ',
       tunable_type=int,
       default=0), 
     'help_tooltip':OptionalTunable(description='\n            If enabled, this Job will have a Help Icon in the Situation Creation UI that will display this tooltip on\n            hover.\n            ',
       tunable=TunableLocalizedString(description='\n                The tooltip to show when the player hovers over the Help Icon for this Job.\n                '),
       tuning_group=GroupNames.UI), 
     'game_breaker':Tunable(description='\n                If True then this job must be filled by a sim\n                or the game will be broken. This is for the grim reaper and\n                the social worker.\n                ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SPECIAL_CASES,
       tuning_filter=FilterTag.EXPERT_MODE), 
     'elevated_importance':Tunable(description='\n                If True, then filling this job with a Sim will be done before\n                filling similar jobs in this situation. This will matter when\n                starting a situation on another lot, when inviting a large number\n                of Sims, visiting commercial venues, or when at the cap on NPCs.\n                \n                Examples:\n                Wedding Situation: the Bethrothed Sims should be spawned before any guests.\n                Birthday Party: the Sims whose birthday it is should be spawned first.\n                Bar Venue: the Bartender should be spawned before the barflies.\n                \n                ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SPECIAL_CASES,
       tuning_filter=FilterTag.EXPERT_MODE), 
     'no_show_action':TunableEnumEntry(situations.situation_types.JobHolderNoShowAction, default=situations.situation_types.JobHolderNoShowAction.DO_NOTHING, description="\n                                The action to take if no sim shows up to fill this job.\n                                \n                                Examples: \n                                If your usual maid doesn't show up, you want another one (REPLACE_THEM).\n                                If one of your party guests doesn't show up, you don't care (DO_NOTHING)\n                                If the President of the United States doesn't show up for the inauguration, you are hosed (END_SITUATION)\n                                ",
       tuning_group=GroupNames.SPECIAL_CASES), 
     'died_or_left_action':TunableEnumEntry(situations.situation_types.JobHolderDiedOrLeftAction, default=situations.situation_types.JobHolderDiedOrLeftAction.DO_NOTHING, description="\n                                    The action to take if a sim in this job dies or leaves the lot.\n                                    \n                                    Examples: \n                                    If the bartender leaves the ambient bar situation, you need a new one (REPLACE_THEM)\n                                    If your creepy uncle leaves the wedding, you don't care (DO_NOTHING)\n                                    If your maid dies cleaning the iron maiden, you are out of luck for today (END_SITUATION).\n                                    \n                                    NB: Do not use REPLACE_THEM if you are using Sim Churn for this job.\n                                    ",
       tuning_group=GroupNames.SPECIAL_CASES), 
     'sim_spawner_tags':TunableList(description="\n            A list of tags that represent where to spawn Sims for this Job when they come onto the lot.\n            NOTE: Sims spawn either randomly or in order of valid tags see 'Use Random Sim Spawner Tag'\n            ",
       tunable=TunableEnumEntry(tunable_type=Tag,
       default=(Tag.INVALID))), 
     'use_random_sim_spawner_tag':Tunable(description='\n            If checked, the spawned sim will randomly select a spawn location out of all valid spawn locations.\n            If unchecked, the sim will pick the first valid sim spawner tag in the order of tuning.\n            ie if Tag[0] has valid location use one of those otherwise -> Tag[1] -> etc\n            ',
       tunable_type=bool,
       default=True), 
     'spawn_at_lot':Tunable(description="\n            If checked we will spawn this sim at spawn points that are linked\n            to this lot.  Otherwise we will ignore that and spawn them at any\n            lot's tags.\n            ",
       tunable_type=bool,
       default=True), 
     'sim_spawn_action':TunableSpawnActionVariant(description='\n            Define the methods to show the Sim after spawning on the lot.\n            '), 
     'sim_spawner_leave_option':TunableEnumEntry(description="\n            This, in conjunction with Sim Spawner Leave Saved Tags, controls\n            which spawn point the Sim chosen for this job will leave to.\n\n            SPAWN_ANY_POINT_WITH_CONSTRAINT_TAGS: Randomly choose a spawn point\n            with a tag tuned on the leave interaction's Spawn Point Constraint.\n\n            SPAWN_SAME_POINT: Use the same spawn point the the Sim spawned in\n            from.\n            \n            SPAWN_ANY_POINT_WITH_SAVED_TAGS: Randomly choose a spawn point with\n            the saved tags.\n            \n            SPAWN_DIFFERENT_POINT_WITH_SAVED_TAGS: Choose the spawn point with\n            the saved tags that is furthest from the spawn point the Sim\n            spawned in from.\n            ",
       tunable_type=SpawnPointOption,
       default=SpawnPointOption.SPAWN_SAME_POINT), 
     'sim_spawner_leave_saved_tags':OptionalTunable(description='\n            This, in conjunction with Sim Spawner Leave Option, controls which\n            spawn point the Sim chosen for this job will leave to. The default\n            behavior is to use the same tags as Sim Spawner Tags.\n            ',
       tunable=TunableList(description='\n                The saved tags to store on the Sim to help the Sim decide\n\t\t\t\twhich spawn point to leave to.\n                ',
       tunable=TunableEnumWithFilter(tunable_type=Tag,
       default=(Tag.INVALID),
       filter_prefixes=SPAWN_PREFIX)),
       disabled_name='use_sim_spawner_tags',
       enabled_name='use_custom_spawner_tags'), 
     'emotional_setup':TunableList(description='\n                Apply the WeightedSingleSimLootActions on the sim that is assigned this job. These are applied\n                only on NPC sims since the tuning is forcing changes to emotions.\n                \n                E.g. an angry mob at the bar, flirty guests at a wedding party.\n                ',
       tunable=TunableTuple(single_sim_loot_actions=(WeightedSingleSimLootActions.TunableReference()),
       weight=Tunable(int, 1, description='Accompanying weight of the loot.')),
       tuning_group=GroupNames.ON_CREATION), 
     'commodities':TunableList(description='\n                Update the commodities on the sim that is assigned this job. These are applied only on\n                NPC sims since the tuning is forcing changes to statistics that have player facing effects.\n             \n                E.g. The students arrive at the lecture hall with the bored and sleepy commodities.\n                ',
       tunable=TunableStatisticChange(locked_args={'subject':ParticipantType.Actor,  'advertise':False, 
      'chance':SuccessChance.ONE, 
      'tests':None}),
       tuning_group=GroupNames.ON_CREATION), 
     'ignore_on_creation_restrictions':Tunable(description="\n            The On Creation tunables (Emotional Setup and Commodities) will only\n            be applied if the Sim is in no other Situations and is actively being\n            created for this Situation/Job. In some cases, like Diners at Restaurants, \n            we want to ignore these restrictions so Commodity and Emotional changes are \n            made when this Situation Job is applied.\n            \n            NOTE: On Creation tunables are still only applied to NPC Sims. This\n            restriction can not be ignored. Also, please consult your GPE partner\n            before you tick this box. It can lead to some very bad bugs if multiple\n            situations are trying to mess with a Sim's emotions/commodities.\n            ",
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.ON_CREATION), 
     'requirement_text':TunableLocalizedString(description='\n                A string that will be displayed in the sim picker for this\n                job in the situation window.\n                ',
       allow_none=True), 
     'goodbye_notification':TunableVariant(description='\n                The "goodbye" notification that will be set on Sims with this\n                situation job. This notification will be displayed when the\n                Sim leaves the lot (unless it gets overridden later).\n                Examples: the visitor job sets the "goodbye" notification to\n                something so the player knows when visitors leave; the party\n                guest roles use "No Notification", because we don\'t want 20-odd\n                notifications when a party ends; the leave lot jobs use "Use\n                Previous Notification" because we want leaving Sims to display\n                whatever notification was set earlier.\n                ',
       notification=TunableUiDialogNotificationSnippet(),
       locked_args={'no_notification':None, 
      'never_use_notification_no_matter_what':SetGoodbyeNotificationElement.NEVER_USE_NOTIFICATION_NO_MATTER_WHAT, 
      'use_previous_notification':DEFAULT},
       default='no_notification'), 
     'additional_filter_for_user_selection':TunableReference(description="\n                An additional filter that will run for the situation job if\n                there should be specific additional requirements for selecting\n                specific sims for the role rather than hiring them.\n                \n                Will be or'd with any filters in additional filter list for user selection\n                \n                ",
       manager=services.get_instance_manager(sims4.resources.Types.SIM_FILTER),
       allow_none=True,
       needs_tuning=True), 
     'additional_filter_list_for_user_selection':TunableList(description="\n                List of additional filters that will run for the situation job if\n                there should be specific additional requirements for selecting\n                specific sims for the role rather than hiring them.\n                Sims only need to pass one of the filters.\n                \n                Will be or'd with any filter in additional filter for user selection\n                ",
       tunable=TunableReference(description='\n                    An additional filter that will run for the situation job if\n                    there should be specific additional requirements for selecting\n                    specific sims for the role rather than hiring them.\n                    ',
       manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)))), 
     'recommended_objects':TunableList(description='\n                A list of objects that are recommended to be on a lot to get\n                the most out of this job\n                ',
       tunable=TunableVenueObject(description="\n                        Specify object tag(s) that should be on this lot.\n                        Allows you to group objects, i.e. weight bench,\n                        treadmill, and basketball goals are tagged as\n                        'exercise objects.'\n                        "),
       export_modes=ExportModes.All), 
     'confirm_leave_situation_for_work':Tunable(description='\n            Sims in situations who go to work will automatically be pulled out\n            of the situation. If this is enabled, a dialog will show for\n            playable Sims, asking player to confirm going to work, decline\n            going, or take PTO (if Sim has any).\n            \n            Dialog that shows up is tunable at:\n            careers.career_tuning -> Career -> Leave_Event_Confirmation\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SPECIAL_CASES), 
     'participating_npcs_should_ignore_work':Tunable(description='\n            If checked, any NPC Sims running this situation job will continue\n            to do so instead of leaving for work when the time comes.\n            ',
       tunable_type=bool,
       default=False,
       tuning_group=GroupNames.SPECIAL_CASES), 
     'should_revalidate_sim_on_load':Tunable(description='\n            If true we will revalidate the sim infos in the situation on\n            load.  This means that if something happened to cause the sims to\n            become invalidated then they will be counted as a no show on load.\n            This is mostly to protect if someone messes with the sim in manage\n            households to a point where they can no longer recover the\n            situation.  Set this to false if the sitaution should continue with\n            them under all circumstances.\n            Ex: During the birthday party that sim who ages up may become\n            invalid to age after they end up aging up.\n            ',
       tunable_type=bool,
       default=True,
       tuning_group=GroupNames.SPECIAL_CASES), 
     'blacklist_info':TunableList(description='\n            Allows a sim to be blacklisted from being available for future jobs\n            for the specified duration and job type(s).\n            ',
       tunable=TunableTuple(blacklist_time=Tunable(description='\n                    When a Sim is removed from a situation, they are added to the\n                    blacklist for this time duration in hours.\n                    ',
       tunable_type=int,
       default=8),
       blacklist_tag=TunableEnumEntry(description='\n                    When a Sim is removed from a situation, they are added to the\n                    blacklist with this tag. This allows a sim to be blacklisted\n                    for some job types, but not others.\n                    ',
       tunable_type=Tag,
       default=(Tag.INVALID))))}

    @staticmethod
    def get_spawn_action(job):
        if SituationJob._job_to_weighted_spawn_action_list is not None:
            if job in SituationJob._job_to_weighted_spawn_action_list:
                if random.random() < SituationJob.ALTERNATIVE_SPAWN_BEHAVIOR.chance_of_using_instance_spawn_action:
                    return job.sim_spawn_action
                weighted_action_list = SituationJob._job_to_weighted_spawn_action_list[job]
                return weighted_random_item(weighted_action_list)
        return job.sim_spawn_action

    @classmethod
    def _verify_tuning_callback(cls):
        messages = []
        if cls.died_or_left_action == situations.situation_types.JobHolderDiedOrLeftAction.REPLACE_THEM:
            messages.append('Died Or Left Action == REPLACE_THEM')
        if cls.churn is not None:
            messages.append('Sim Churn')
        if cls.sim_shifts is not None:
            messages.append('Sim Shifts')
        if len(messages) > 1:
            message = ', and '.join(messages)
            logger.error('Situation job :{} must use only one of {}', cls, message)
        tuned_tags = list()
        for bi in cls.blacklist_info:
            if bi.blacklist_time is 0:
                logger.error('Situation job :{} has a tuned blacklist time of 0.', cls)
            if bi.blacklist_tag == Tag.INVALID:
                logger.error('Situation job :{} has an untuned blacklist tag. INVALID is not a valid choice.', cls)
            tuned_tags.append(bi.blacklist_tag)

        if tuned_tags:
            if len(tuned_tags) != len(set(tuned_tags)):
                logger.error('Situation job :{} has blacklist data with duplicate tags.', cls)

    @classmethod
    def get_score--- This code section failed: ---

 L.1327         0  LOAD_FAST                'event'
                2  LOAD_GLOBAL              event_testing
                4  LOAD_ATTR                test_variants
                6  LOAD_ATTR                TestEvent
                8  LOAD_ATTR                InteractionComplete
               10  COMPARE_OP               ==
               12  POP_JUMP_IF_FALSE   208  'to 208'

 L.1330        14  LOAD_FAST                'resolver'
               16  LOAD_METHOD              get_participant
               18  LOAD_GLOBAL              ParticipantType
               20  LOAD_ATTR                TargetSim
               22  CALL_METHOD_1         1  '1 positional argument'
               24  STORE_FAST               'target'

 L.1331        26  LOAD_FAST                'target'
               28  LOAD_CONST               None
               30  COMPARE_OP               is-not
               32  POP_JUMP_IF_FALSE    42  'to 42'

 L.1333        34  LOAD_FAST                'target'
               36  LOAD_METHOD              get_sim_instance
               38  CALL_METHOD_0         0  '0 positional arguments'
               40  STORE_FAST               'target'
             42_0  COME_FROM            32  '32'

 L.1335        42  SETUP_LOOP          254  'to 254'
               44  LOAD_FAST                'cls'
               46  LOAD_ATTR                interaction_scoring
               48  GET_ITER         
             50_0  COME_FROM           194  '194'
               50  FOR_ITER            204  'to 204'
               52  STORE_FAST               'score_list'

 L.1338        54  LOAD_FAST                'score_list'
               56  LOAD_ATTR                role_tags
               58  LOAD_CONST               None
               60  COMPARE_OP               is-not
               62  POP_JUMP_IF_FALSE   186  'to 186'

 L.1339        64  LOAD_FAST                'target'
               66  LOAD_CONST               None
               68  COMPARE_OP               is
               70  POP_JUMP_IF_FALSE    74  'to 74'

 L.1340        72  CONTINUE             50  'to 50'
             74_0  COME_FROM            70  '70'

 L.1345        74  LOAD_CONST               False
               76  STORE_FAST               'should_apply_score'

 L.1346        78  SETUP_LOOP          180  'to 180'
               80  LOAD_GLOBAL              services
               82  LOAD_METHOD              get_zone_situation_manager
               84  CALL_METHOD_0         0  '0 positional arguments'
               86  LOAD_METHOD              get_situations_sim_is_in
               88  LOAD_FAST                'target'
               90  CALL_METHOD_1         1  '1 positional argument'
               92  GET_ITER         
             94_0  COME_FROM           172  '172'
             94_1  COME_FROM           160  '160'
               94  FOR_ITER            178  'to 178'
               96  STORE_FAST               'situation'

 L.1347        98  LOAD_FAST                'situation'
              100  LOAD_METHOD              get_role_tags_for_sim
              102  LOAD_FAST                'target'
              104  CALL_METHOD_1         1  '1 positional argument'
              106  STORE_FAST               'role_tags'

 L.1350       108  LOAD_FAST                'score_list'
              110  LOAD_ATTR                role_tags
              112  LOAD_ATTR                blacklist
              114  LOAD_FAST                'role_tags'
              116  BINARY_AND       
              118  POP_JUMP_IF_FALSE   126  'to 126'

 L.1351       120  LOAD_CONST               False
              122  STORE_FAST               'should_apply_score'

 L.1352       124  BREAK_LOOP       
            126_0  COME_FROM           118  '118'

 L.1356       126  LOAD_FAST                'score_list'
              128  LOAD_ATTR                role_tags
              130  LOAD_ATTR                whitelist
              132  LOAD_CONST               None
              134  COMPARE_OP               is
              136  POP_JUMP_IF_FALSE   144  'to 144'

 L.1357       138  LOAD_CONST               True
              140  STORE_FAST               'should_apply_score'
              142  JUMP_BACK            94  'to 94'
            144_0  COME_FROM           136  '136'

 L.1362       144  LOAD_FAST                'score_list'
              146  LOAD_ATTR                role_tags
              148  LOAD_ATTR                whitelist
              150  LOAD_FAST                'situation'
              152  LOAD_METHOD              get_role_tags_for_sim
              154  LOAD_FAST                'target'
              156  CALL_METHOD_1         1  '1 positional argument'
              158  BINARY_AND       
              160  POP_JUMP_IF_FALSE    94  'to 94'

 L.1363       162  LOAD_CONST               True
              164  STORE_FAST               'should_apply_score'

 L.1364       166  LOAD_FAST                'score_list'
              168  LOAD_ATTR                role_tags
              170  LOAD_ATTR                blacklist
              172  POP_JUMP_IF_TRUE     94  'to 94'

 L.1365       174  BREAK_LOOP       
              176  JUMP_BACK            94  'to 94'
              178  POP_BLOCK        
            180_0  COME_FROM_LOOP       78  '78'

 L.1368       180  LOAD_FAST                'should_apply_score'
              182  POP_JUMP_IF_TRUE    186  'to 186'

 L.1369       184  CONTINUE             50  'to 50'
            186_0  COME_FROM           182  '182'
            186_1  COME_FROM            62  '62'

 L.1370       186  LOAD_FAST                'resolver'
              188  LOAD_FAST                'score_list'
              190  LOAD_ATTR                affordance_list
              192  CALL_FUNCTION_1       1  '1 positional argument'
              194  POP_JUMP_IF_FALSE    50  'to 50'

 L.1371       196  LOAD_FAST                'score_list'
              198  LOAD_ATTR                score
              200  RETURN_VALUE     
              202  JUMP_BACK            50  'to 50'
              204  POP_BLOCK        
              206  JUMP_FORWARD        254  'to 254'
            208_0  COME_FROM            12  '12'

 L.1372       208  LOAD_FAST                'event'
              210  LOAD_GLOBAL              event_testing
              212  LOAD_ATTR                test_variants
              214  LOAD_ATTR                TestEvent
              216  LOAD_ATTR                ItemCrafted
              218  COMPARE_OP               ==
              220  POP_JUMP_IF_FALSE   254  'to 254'

 L.1373       222  SETUP_LOOP          254  'to 254'
              224  LOAD_FAST                'cls'
              226  LOAD_ATTR                crafted_object_scoring
              228  GET_ITER         
            230_0  COME_FROM           242  '242'
              230  FOR_ITER            252  'to 252'
              232  STORE_FAST               'score_list'

 L.1374       234  LOAD_FAST                'resolver'
              236  LOAD_FAST                'score_list'
              238  LOAD_ATTR                object_list
              240  CALL_FUNCTION_1       1  '1 positional argument'
              242  POP_JUMP_IF_FALSE   230  'to 230'

 L.1375       244  LOAD_FAST                'score_list'
              246  LOAD_ATTR                score
              248  RETURN_VALUE     
              250  JUMP_BACK           230  'to 230'
              252  POP_BLOCK        
            254_0  COME_FROM_LOOP      222  '222'
            254_1  COME_FROM           220  '220'
            254_2  COME_FROM           206  '206'
            254_3  COME_FROM_LOOP       42  '42'

 L.1376       254  LOAD_CONST               0
              256  RETURN_VALUE     
               -1  RETURN_LAST      

Parse error at or near `COME_FROM_LOOP' instruction at offset 180_0

    @classmethod
    def get_auto_invite(cls):
        if cls.churn is not None:
            interval = cls.churn.get_auto_populate_interval()
        else:
            if cls.sim_shifts is not None:
                return cls.sim_shifts.get_shift_staffing()
                if cls.sim_auto_invite.upper_bound > 0:
                    interval = AutoPopulateInterval(min=(cls.sim_auto_invite.lower_bound), max=(cls.sim_auto_invite.upper_bound))
            else:
                return 0
        auto_invite = random.randrange(interval.min, interval.max + 1)
        return auto_invite

    @classmethod
    def get_location_based_filter_terms(cls):
        if cls.filter is TunableSimFilter.BLANK_FILTER:
            return ()
        combined_terms = ()
        for filter_terms in cls.location_based_filter_terms:
            combined_terms += filter_terms.get_filter_terms()

        return combined_terms

    @classmethod
    def can_sim_be_given_job(cls, sim_id, requesting_sim_info, gsi_source_fn=None):
        if cls.filter is None:
            return True

        def get_sim_filter_gsi_name():
            return 'Request to check if {} matches filter from {}'.format(sim_id, cls)

        return services.sim_filter_service().does_sim_match_filter(sim_id, sim_filter=(cls.filter),
          requesting_sim_info=requesting_sim_info,
          additional_filter_terms=(cls.get_location_based_filter_terms()),
          gsi_source_fn=(gsi_source_fn or get_sim_filter_gsi_name))