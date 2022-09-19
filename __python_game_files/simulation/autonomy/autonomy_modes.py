# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\autonomy\autonomy_modes.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 186593 bytes
from _collections import defaultdict
from _functools import reduce
from _weakrefset import WeakSet
import collections, itertools, operator, random, time, weakref
from animation.posture_manifest_constants import PostureConstants
from autonomy.autonomy_gsi_enums import AutonomyStageLabel, GSIDataKeys
from autonomy.autonomy_interaction_priority import AutonomyInteractionPriority
from autonomy.autonomy_mixer_provider import _MixerProvider, _MixerProviderType
from autonomy.autonomy_mixer_provider_scoring import _MixerProviderScoring
from autonomy.autonomy_preference import AutonomyPreferenceType
from autonomy.autonomy_request import AutonomyDistanceEstimationBehavior, AutonomyPostureBehavior
from caches import cached
from clock import ClockSpeedMode
from event_testing.resolver import SingleSimResolver
from event_testing.results import TestResult
from interactions.aop import AffordanceObjectPair
from interactions.context import InteractionContext, InteractionSource
from objects.components.inventory_type_tuning import InventoryTypeTuning
from sims4.tuning.geometric import TunableWeightedUtilityCurve, TunableCurve
from sims4.tuning.tunable import Tunable, TunableInterval, TunableSimMinute, TunableMapping, TunableEnumEntry, TunableReference, TunableRealSecond, TunedInterval
from singletons import DEFAULT
from statistics.base_statistic import StatisticChangeDirection
from tag import Tag
import autonomy.autonomy_exceptions, autonomy.autonomy_util, autonomy.settings, clock, date_and_time, element_utils, elements, gsi_handlers, interactions, objects.components.types, services, sims4.log, sims4.random, sims4.reload, sims4.repr_utils, sims4.resources, singletons
logger = sims4.log.Logger('Autonomy', default_owner='rez')
timeslice_logger = sims4.log.Logger('AutonomyTimeslice', default_owner='rez')
gsi_logger = sims4.log.Logger('AutonomyGSI', default_owner='iobaid')
ScoredInteractionData = collections.namedtuple('ScoredInteractionData', ['score', 'route_time', 'multitasking_percentage', 'interaction'])
_DeferredAopData = collections.namedtuple('_DeferredAopData', ['aop', 'inventory_type', 'outside_multiplier'])

class AutonomyMode:
    FULL_AUTONOMY_DELAY = TunableInterval(TunableSimMinute,
      15, 30, minimum=0, description='\n                                  Amount of time, in sim minutes, between full autonomy runs.  System will randomize between \n                                  min and max each time')
    FULL_AUTONOMY_DELAY_WITH_NO_PRIMARY_SIS = TunableInterval(TunableSimMinute,
      1.5, 2.5, minimum=0, description="\n                                                      The amount of time, in sim minutes, to wait before running autonomy if a sim \n                                                      is not in any primary SI's and hasn't run a user-directed action since \n                                                      AUTONOMY_DELAY_AFTER_USER_INTERACTION.")
    FULL_AUTONOMY_DELAY_WITH_NO_RESULT = TunableInterval(description="\n                                                The amount of time, in sim minutes, to wait before running autonomy if a sim's \n                                                autonomy returned None.\n                                                ",
      tunable_type=TunableSimMinute,
      default_lower=20,
      default_upper=30,
      minimum=1)
    AUTONOMY_DELAY_AFTER_USER_INTERACTION = TunableSimMinute(25,
      description='\n                                                    The amount of time, in sim minutes, before a sim that performs a user-direction \n                                                    interaction will run autonomy.')
    MAX_REAL_SECONDS_UNTIL_TIMESLICING_IS_REMOVED = TunableRealSecond(description='\n                                                        The amount of time before autonomy stops timeslicing and forces the autonomy request to \n                                                        run unimpeded.',
      default=1)
    FULL_AUTONOMY_STATISTIC_SCORE_VARIANCE = Tunable(float,
      0.9, description='\n                                                     The percentage variance that a statistic can have from the top stat before it is \n                                                     not considered for the first round of scoring.')
    FULL_AUTONOMY_OPTIMISTIC_SCORE_THRESHOLD = Tunable(float,
      0.5, description="\n                                                     Before computing the routing distance to an object, we calculate an 'optimistic' score,\n                                                     which assumes that an object is right next to a Sim and won't invalidate any of their\n                                                     current interactions.  If the optimistic score is lower than this fraction of the best\n                                                     scoring affordance so far the Sim will not bother estimating routing distance.")
    FULL_AUTONOMY_MULTIPLIER_FOR_SOLVING_THE_SAME_STAT = Tunable(float,
      0.25, description='\n                                                     If a sim is currently solving a motive, this value will be multiplied into the \n                                                     commodity score of any other interactions.  This will force sims to live with \n                                                     their decisions rather than always looking for the best thing.')
    FULL_AUTONOMY_DESIRE_TO_JOIN_PLAYER_PARTIES = Tunable(float,
      0, description='\n                                                          This weight is multiplied with the affordance score if the target party has \n                                                          any sims that are not autonomous.')
    FULL_AUTONOMY_ATTENTION_COST = TunableWeightedUtilityCurve(description='\n                                                             A curve that maps the total attention cost with a score multiplier.  This value will be \n                                                             multiplied with the typical autonomy score to account for multi-tasking costs.')
    FULL_AUTONOMY_MULTITASKING_PERCENTAGE_BONUS = TunableCurve(description='\n                                                             A curve that maps the commodity desire score with a percentage bonus applied to the \n                                                             base multitasking chance.')
    FULL_AUTONOMY_INTERACTION_PRIORITY_RANKING = TunableMapping(description='\n        Mapping to decide the order autonomous interaction will be chosen for\n        full autonomy ping.\n        ',
      key_type=TunableEnumEntry(AutonomyInteractionPriority,
      (AutonomyInteractionPriority.INVALID),
      invalid_enums=(
     AutonomyInteractionPriority.INVALID,)),
      value_type=(Tunable(int, 0)))
    OFF_LOT_OBJECT_SCORE_MULTIPLIER = Tunable(description='\n                                                The autonomy score multiplier for off-lot object when a sim \n                                                is on the active lot.\n                                                ',
      tunable_type=float,
      default=0.5)
    SUBACTION_AUTONOMY_CONTENT_SCORE_UTILITY_CURVE = TunableWeightedUtilityCurve(description='\n                                                             A curve that maps the content score to the provided utility.')
    SUBACTION_MOTIVE_UTILITY_FALLBACK_SCORE = Tunable(float,
      0.1, description='\n                                                      If score for sub-action motive utility is zero, use this value as the best score.')
    SUBACTION_GROUP_UNTUNED_WEIGHT = 1
    SUBACTION_GROUP_WEIGHTING = TunableMapping(description='\n                                    Mapping of mixer interaction group tags to scores.  This is used by subaction autonomy\n                                    to decide which set of mixers to run.  See the mixer_group entry in the sub_action tunable\n                                    on any mixer for details as to how the system works.\n                                    ',
      key_type=TunableEnumEntry((interactions.MixerInteractionGroup),
      (interactions.MixerInteractionGroup.DEFAULT),
      description='\n                                        The mixer group this score applies to.\n                                        '),
      value_type=Tunable(int,
      SUBACTION_GROUP_UNTUNED_WEIGHT,
      description='\n                                        The weight of this group.\n                                        '))
    POSTURE_CHANGE_OPPORTUNITY_COST_MULTIPLIER = Tunable(float,
      1.5, description='\n                                                        Multiplier to apply to the total opportunity cost of an aop when choosing that aop would\n                                                        force the Sim to change postures.  This makes the concept of changing postures less \n                                                        attractive to Sims.')
    AUTOMATED_RANDOMIZATION_LIST = TunableMapping(description='\n        A mapping of the commodities used for determinisitc randomization.  This is used by the automation\n        system in the min spec perf tests.\n        ',
      key_type=TunableReference(description='\n            The statistic we are operating on.',
      manager=(services.get_instance_manager(sims4.resources.Types.STATISTIC))),
      value_type=Tunable(description='\n            The number of times per loop to assign this to a Sim.',
      tunable_type=int,
      default=1))
    NUMBER_OF_DUPLICATE_AFFORDANCE_TAGS_TO_SCORE = Tunable(description='\n                                                        If an affordance is tuned with duplicate_affordance_group set to anything \n                                                        except INVALID, this is the number of affordances that share this tag that\n                                                        will be scored. \n                                                        ',
      tunable_type=int,
      default=3)
    _full_autonomy_delay_override = None
    _autonomy_delay_after_user_interaction_override = None
    _disable_autonomous_multitasking_if_user_directed_override = singletons.DEFAULT
    _MINIMUM_SCORE = 1e-05

    def __init__(self, request):
        self._request = request
        self._motive_scores = None
        self._process_start_time = None

    def __str__(self):
        return 'Unknown Mode'

    @property
    def _sim(self):
        return self._request.sim

    def run_gen(self, timeline, timeslice):
        self._motive_scores = self._score_motives()
        self._request.create_autonomy_ping_request_record()
        result = yield from self._run_gen(timeline, timeslice)
        self._request.add_record_to_profiling_data()
        return result
        if False:
            yield None

    def _run_gen(self, timeline, timeslice):
        raise NotImplementedError
        yield

    @classmethod
    def toggle_disable_autonomous_multitasking_if_user_directed(cls, to_enabled):
        if cls._disable_autonomous_multitasking_if_user_directed_override is singletons.DEFAULT:
            is_enabled = False
        else:
            is_enabled = cls._disable_autonomous_multitasking_if_user_directed_override
        if to_enabled is None:
            cls._disable_autonomous_multitasking_if_user_directed_override = not is_enabled
        else:
            cls._disable_autonomous_multitasking_if_user_directed_override = to_enabled
        return cls._disable_autonomous_multitasking_if_user_directed_override

    @classmethod
    def get_autonomy_delay_after_user_interaction(cls):
        return clock.interval_in_sim_minutes(cls._get_autonomy_delay_after_user_interaction_in_sim_minutes())

    @classmethod
    def _get_autonomy_delay_after_user_interaction_in_sim_minutes(cls):
        if cls._autonomy_delay_after_user_interaction_override is not None:
            return cls._autonomy_delay_after_user_interaction_override
        return cls.AUTONOMY_DELAY_AFTER_USER_INTERACTION

    @classmethod
    def get_autonomous_delay_time(cls):
        return clock.interval_in_sim_minutes(cls._get_autonomous_delay_time_in_sim_minutes())

    @classmethod
    def _get_autonomous_delay_time_in_sim_minutes(cls):
        raise NotImplementedError

    @classmethod
    def get_autonomous_update_delay_with_no_primary_sis(cls):
        return clock.interval_in_sim_minutes(cls._get_autonomous_update_delay_with_no_primary_sis_in_sim_minutes())

    @classmethod
    def _get_autonomous_update_delay_with_no_primary_sis_in_sim_minutes(cls):
        return cls.FULL_AUTONOMY_DELAY_WITH_NO_PRIMARY_SIS.random_float()

    @classmethod
    def get_no_result_delay_time(cls):
        return clock.interval_in_sim_minutes(cls.FULL_AUTONOMY_DELAY_WITH_NO_RESULT.random_float())

    @classmethod
    def override_full_autonomy_delay(cls, lower_bound, upper_bound):
        if lower_bound > upper_bound:
            logger.error('lower_bound > upper_bound in override_full_autonomy_delay()')
        else:
            cls._full_autonomy_delay_override = TunedInterval(lower_bound=lower_bound, upper_bound=upper_bound)

    @classmethod
    def clear_full_autonomy_delay_override(cls):
        cls._full_autonomy_delay_override = None

    @classmethod
    def override_full_autonomy_delay_after_user_action(cls, delay):
        cls._autonomy_delay_after_user_interaction_override = delay

    @classmethod
    def clear_full_autonomy_delay_after_user_action(cls):
        cls._autonomy_delay_after_user_interaction_override = None

    @classmethod
    def test(cls, sim):
        return True

    @classmethod
    def is_silent_mode(cls):
        return False

    def set_process_start_time(self):
        self._process_start_time = time.clock()

    @classmethod
    def allows_routing(cls):
        return False

    def _allow_autonomous(self, aop):
        if self._request.ignore_user_directed_and_autonomous:
            return TestResult.TRUE
        else:
            affordance = aop.affordance
            if self._request.context.source == InteractionContext.SOURCE_AUTONOMY:
                if not affordance.allow_autonomous:
                    if self._request.record_test_result is not None:
                        self._request.record_test_result(aop, 'allow_autonomous', None)
                    return TestResult(False, 'allow_autonomous is False.')
                if affordance.is_super:
                    if not affordance.commodity_flags:
                        if self._request.record_test_result is not None:
                            self._request.record_test_result(aop, 'allow_autonomous', None)
                        return TestResult(False, 'No commodities were advertised.')
            if self._request.context.source == InteractionContext.SOURCE_PIE_MENU and not affordance.allow_user_directed:
                if self._request.record_test_result is not None:
                    self._request.record_test_result(aop, 'allow_user_directed', None)
                return TestResult(False, 'allow_user_directed is False.')
        return TestResult.TRUE

    def _is_available(self, obj):
        context = self._request.context
        if context.source != context.SOURCE_AUTONOMY:
            if not context.always_check_in_use:
                return self._get_object_result(obj, success=True, reason='Scored')
        if not self._request.ignore_lockouts:
            if self._sim.has_lockout(obj):
                if self._request.record_test_result is not None:
                    self._request.record_test_result(None, '_is_available', sims4.utils.Result(False, 'Sim has lockout.'))
                return self._get_object_result(obj, success=False, reason='Sim has lockout for this object')
        return self._get_object_result(obj, success=True, reason='Scored')

    def _get_object_result(self, obj, success: bool, reason: str):
        return success

    def _score_motives(self):
        motive_scores = None
        motive_scores = {stat.stat_type:ScoredStatistic(stat, self._sim) for stat in tuple(self._sim.scored_stats_gen())}
        if self._request.has_commodities:
            for stat in self._request.all_commodities:
                stat_type = stat.stat_type
                if stat_type not in motive_scores:
                    statistic_instance = self._sim.get_stat_instance(stat_type, add=False) or stat_type
                    motive_scores[stat_type] = ScoredStatistic(statistic_instance, self._sim)

        return motive_scores

    @classmethod
    def _should_log(cls, active_sim):
        if not cls.is_silent_mode():
            if active_sim is not None:
                return services.autonomy_service().should_log(active_sim)
            return False


class _MixerAutonomy(AutonomyMode):

    def __init__(self, request):
        super().__init__(request)
        self._mixer_provider_scoring = None
        self._mixer_provider_and_group_to_scored_mixer_aops = {}
        self._gsi_mixer_scoring = None
        self._run_gen_call_count = 0

    def _cache_mixer_provider_scoring(self, gsi_enabled_at_start):
        if self._mixer_provider_scoring is not None:
            return
        self._mixer_provider_scoring = _MixerProviderScoring(gsi_enabled_at_start=gsi_enabled_at_start)
        for mixer_provider in self._mixer_providers_gen():
            if not mixer_provider.has_mixers():
                continue
            mixer_providing_score, gsi_mixer_provider_data = self._score_mixer_provider(mixer_provider, gsi_enabled_at_start)
            self._mixer_provider_scoring.add_mixer_provider(mixer_providing_score, mixer_provider, gsi_mixer_provider_data)

    def _run_gen(self, timeline, timeslice):
        gsi_enabled_at_start = gsi_handlers.autonomy_handlers.archiver.enabled
        if gsi_enabled_at_start:
            if self._gsi_mixer_scoring is None:
                self._gsi_mixer_scoring = []
        self._cache_mixer_provider_scoring(gsi_enabled_at_start)
        self._run_gen_call_count += 1
        scored_mixers_aops = None
        while self._mixer_provider_scoring.is_valid():
            chosen_mixer_provider = self._mixer_provider_scoring.get_mixer_provider()
            if chosen_mixer_provider is None:
                return
            else:
                interaction_mixer_group_weight = []
                for mixer_interaction_group in chosen_mixer_provider.mixer_interaction_groups():
                    if not self._mixer_provider_scoring.is_mixer_group_valid(chosen_mixer_provider, mixer_interaction_group):
                        continue
                    if mixer_interaction_group in self.SUBACTION_GROUP_WEIGHTING:
                        interaction_mixer_group_weight.append((self.SUBACTION_GROUP_WEIGHTING[mixer_interaction_group], mixer_interaction_group))
                    else:
                        logger.error('Untuned weight for mixer group: {}', mixer_interaction_group)
                        interaction_mixer_group_weight.append((self.SUBACTION_GROUP_UNTUNED_WEIGHT, mixer_interaction_group))

                mixer_interaction_group = None
                if interaction_mixer_group_weight:
                    mixer_interaction_group = sims4.random.weighted_random_item(interaction_mixer_group_weight)
                else:
                    self._mixer_provider_scoring.remove_invalid_mixer_provider(chosen_mixer_provider)
            if mixer_interaction_group is None:
                continue
            scored_mixers_aops = self._mixer_provider_and_group_to_scored_mixer_aops.get((chosen_mixer_provider, mixer_interaction_group), None)
            if scored_mixers_aops is not None:
                break

            def _aop_pre_tests(aop):
                return self._allow_autonomous(aop)

            mixer_aops = chosen_mixer_provider.get_mixers((self._request), mixer_interaction_group, aop_pre_tests=_aop_pre_tests)
            if mixer_aops is None:
                self._mixer_provider_scoring.invalidate_group_for_mixer_provider(chosen_mixer_provider, mixer_interaction_group)
                if self._gsi_mixer_scoring is not None:
                    self._mixer_provider_scoring.add_mixer_provider_mixer_result_to_gsi(chosen_mixer_provider, mixer_interaction_group, 'No Mixers Available', self._run_gen_call_count)
                    continue
            scored_mixers_aops = self._create_and_score_mixers(chosen_mixer_provider, mixer_aops, self._gsi_mixer_scoring)
            if scored_mixers_aops is None:
                self._mixer_provider_scoring.invalidate_group_for_mixer_provider(chosen_mixer_provider, mixer_interaction_group)
                if self._gsi_mixer_scoring is not None:
                    self._mixer_provider_scoring.add_mixer_provider_mixer_result_to_gsi(chosen_mixer_provider, mixer_interaction_group, 'No Mixers Scored', self._run_gen_call_count)
                    continue
                self._mixer_provider_and_group_to_scored_mixer_aops[(chosen_mixer_provider, mixer_interaction_group)] = scored_mixers_aops
                if self._gsi_mixer_scoring is not None:
                    self._mixer_provider_scoring.add_mixer_provider_mixer_result_to_gsi(chosen_mixer_provider, mixer_interaction_group, 'Scored', self._run_gen_call_count)
            break

        if scored_mixers_aops is None:
            return
        valid_interactions = ValidInteractions()
        for interaction_score, mixer_aop in scored_mixers_aops.values():
            if self._request.skipped_affordance_list:
                if mixer_aop.affordance in self._request.skipped_affordance_list:
                    continue
                mixer_result = mixer_aop.interaction_factory(self._request.context)
                if not mixer_result:
                    continue
                mixer_interaction = mixer_result.interaction
                if mixer_interaction is not None:
                    valid_interactions.add(ScoredInteractionData(interaction_score, 0, 1, mixer_interaction))

        self._request.valid_interactions = valid_interactions
        if gsi_enabled_at_start:
            if not self._request.gsi_data:
                self._request.gsi_data = {GSIDataKeys.AFFORDANCE_KEY: [], 
                 GSIDataKeys.PROBABILITY_KEY: [], 
                 GSIDataKeys.OBJECTS_KEY: [], 
                 GSIDataKeys.COMMODITIES_KEY: self._motive_scores.values(), 
                 GSIDataKeys.MIXER_PROVIDER_KEY: self._mixer_provider_scoring.gsi_mixer_provider_data, 
                 GSIDataKeys.MIXERS_KEY: self._gsi_mixer_scoring, 
                 GSIDataKeys.REQUEST_KEY: self._request.get_gsi_data()}
        return valid_interactions
        if False:
            yield None

    @classmethod
    def test(cls, sim):
        autonomy_state = sim.get_autonomy_state_setting()
        if autonomy_state <= autonomy.settings.AutonomyState.DISABLED:
            return False
        return True

    @classmethod
    def _get_autonomous_delay_time_in_sim_minutes(cls):
        return cls.SUB_ACTION_AUTONOMY_DELAY

    def _mixer_providers_gen(self):
        raise NotImplementedError
        yield

    def _score_mixer_provider(self, mixer_provider, gsi_enabled_at_start=False):
        scored_commodity = mixer_provider.get_scored_commodity(self._motive_scores)
        motive_utility = None
        if scored_commodity:
            motive_utility = self._motive_scores.get(scored_commodity)
        elif motive_utility is None:
            motive_utility = self.SUBACTION_MOTIVE_UTILITY_FALLBACK_SCORE
        else:
            motive_utility = max(motive_utility, self.SUBACTION_MOTIVE_UTILITY_FALLBACK_SCORE)
        score = motive_utility * mixer_provider.get_subaction_weight()
        gsi_mixer_provider_data = None
        if gsi_enabled_at_start is not None:
            score_detail_string = 'Weight: {}; ScoredCommodity: {} Commodity Score: {}'.format(mixer_provider.get_subaction_weight(), scored_commodity, motive_utility)
            gsi_mixer_provider_data = gsi_handlers.autonomy_handlers.GSIMixerProviderData(str(mixer_provider), mixer_provider.target_string, score, score_detail_string)
        return (score, gsi_mixer_provider_data)

    def _create_and_score_mixers(self, mixer_provider, mixer_aops, gsi_mixer_scoring):
        mixer_scores = None
        content_set_score = 1
        mixer_provider_is_social = mixer_provider.is_social
        for mixer_weight, mixer_aop, _ in mixer_aops:
            mixer_aop_affordance = mixer_aop.affordance
            mixer_aop_target = mixer_aop.target
            if mixer_provider_is_social:
                if mixer_aop_affordance.target_type & interactions.TargetType.TARGET:
                    if mixer_aop_target.is_sim:
                        if mixer_aop_target.disallow_as_mixer_target:
                            continue
                elif mixer_provider_is_social:
                    content_set_score = self._get_subaction_content_set_utility_score(mixer_aop.content_score)
                    score = mixer_weight * content_set_score
                    club_service = services.get_club_service()
                    if club_service is not None:
                        club_score_multiplier = club_service.get_interaction_score_multiplier(mixer_aop, sim=(self._sim))
                        score *= club_score_multiplier
                else:
                    score = mixer_weight
                if score <= self._MINIMUM_SCORE:
                    score = 0
                if mixer_scores is None:
                    mixer_scores = {}
                mixer_scores[mixer_aop_affordance] = (
                 score, mixer_aop)
                if gsi_mixer_scoring is not None:
                    score_detail_string = 'Weight: {}; Content Score: {}; Group: {}'.format(mixer_weight, content_set_score, mixer_aop_affordance.sub_action.mixer_group)
                    gsi_mixer_scoring.append((score,
                     str(mixer_provider),
                     str(mixer_aop_affordance),
                     str(mixer_aop_target),
                     score_detail_string))

        return mixer_scores

    def _get_subaction_content_set_utility_score(self, content_score):
        if content_score is None:
            return self.SUBACTION_MOTIVE_UTILITY_FALLBACK_SCORE
        utility = self.SUBACTION_AUTONOMY_CONTENT_SCORE_UTILITY_CURVE.get(content_score)
        if utility == 0:
            return self.SUBACTION_MOTIVE_UTILITY_FALLBACK_SCORE
        return utility


class SubActionAutonomy(_MixerAutonomy):

    def __str__(self):
        return 'SubActionAutonomy'

    def _mixer_providers_gen(self):
        super_affordance_mixer_override = False
        for si in self._sim.si_state:
            if not si.only_use_mixers_from_si:
                continue
            super_affordance_mixer_override = True
            if not si.has_affordances():
                continue
            mixer_provider = _MixerProvider(si, _MixerProviderType.SI)
            yield mixer_provider

        if not super_affordance_mixer_override:
            for si in self._sim.si_state:
                if not si.has_affordances():
                    continue
                mixer_provider = _MixerProvider(si, _MixerProviderType.SI)
                yield mixer_provider

            for buff in self._sim.Buffs:
                if buff.interactions is None:
                    continue
                mixer_provider = _MixerProvider(buff, _MixerProviderType.BUFF)
                yield mixer_provider


class SocialAutonomy(_MixerAutonomy):

    def __init__(self, *args, **kwargs):
        (super().__init__)(*args, **kwargs)

    def __str__(self):
        return 'SocialAutonomy'

    def _run_gen(self, timeline, timeslice):
        if not self._validate_request():
            return
        result = yield from super()._run_gen(timeline, timeslice)
        return result
        if False:
            yield None

    def _validate_request(self):
        if not self._request.static_commodity_list:
            logger.error('Failed to run SocialAutonomy: no static commodities listed.')
            return False
        else:
            self._request.object_list or logger.error('Failed to run SocialAutonomy: no objects listed.')
            return False
        return True

    def _mixer_providers_gen(self):
        for target_sim in self._request.objects_to_score_gen(self._request.static_commodity_list):
            if not target_sim.is_sim:
                continue
            if not self._is_available(target_sim):
                continue
            for affordance in target_sim.super_affordances():
                for static_commodity in self._request.static_commodity_list:
                    if static_commodity in affordance.static_commodities:
                        break
                else:
                    continue

                aop = AffordanceObjectPair(affordance, target_sim, affordance, None)
                execute_result = aop.interaction_factory(self._request.context)
                if not execute_result:
                    logger.error('Failed to create interaction: '.format(aop))
                    continue
                interaction = execute_result.interaction
                incompatible_sis = self._sim.si_state.get_incompatible(interaction)
                if incompatible_sis:
                    interaction.invalidate()
                    continue
                else:
                    target_interaction, test_result = interaction.get_target_si()
                    if not test_result:
                        interaction.invalidate()
                        continue
                    elif target_interaction is None:
                        target_context = self._request.context.clone_for_sim(target_sim)
                        target_sim_si_state = target_sim.si_state
                        target_sim_si_state.is_compatible(interaction, (interaction.priority), group_id=(interaction.group_id),
                          context=target_context,
                          check_constraints=False) or incompatible_sis.add(interaction)
                    else:
                        incompatible_sis = target_sim.si_state.get_incompatible(target_interaction)
                if incompatible_sis:
                    interaction.invalidate()
                    continue
                self._request.interactions_to_invalidate.append(interaction)
                yield _MixerProvider(interaction, _MixerProviderType.SI)


class _SuperInteractionAutonomy(AutonomyMode):
    UNREACHABLE_DESTINATION_COST = 1000000

    def __init__(self, request):
        super().__init__(request)
        self._actively_scored_motives = None
        self._formerly_scored_motives = set()

    def _test_aop(self, aop):
        context = self._request.context
        test_result = aop.test(context)
        if not test_result:
            if self._request.record_test_result is not None:
                self._request.record_test_result(aop, '_test_aop', test_result)
            return test_result
        return TestResult.TRUE

    def _has_available_part(self, interaction):
        if interaction.target is None:
            return True
        else:
            return interaction.target.parts or True
        for part in interaction.target.parts:
            reservation_handler = interaction.get_interaction_reservation_handler(target=part)
            if reservation_handler is None:
                return True
                if reservation_handler.may_reserve():
                    return True

        return False

    def _calculate_route_time_and_opportunity(self, timeline, interaction):
        request = self._request
        if interaction.disable_distance_estimation_and_posture_checks:
            return (
             0, 0, False, set())
        else:
            ignore_included_sis = request.posture_behavior == AutonomyPostureBehavior.IGNORE_SI_STATE
            if request.distance_estimation_behavior == AutonomyDistanceEstimationBehavior.FINAL_PATH:
                estimated_distance, must_change_posture, included_sis = yield from interaction.estimate_final_path_distance(timeline, ignore_included_sis)
            else:
                if ignore_included_sis:
                    estimated_distance, must_change_posture, included_sis = interaction.estimate_distance_ignoring_other_sis()
                else:
                    estimated_distance, must_change_posture, included_sis = interaction.estimate_distance()
        if request.distance_estimation_behavior == AutonomyDistanceEstimationBehavior.ALLOW_UNREACHABLE_LOCATIONS and estimated_distance is None:
            estimated_distance = _SuperInteractionAutonomy.UNREACHABLE_DESTINATION_COST
        else:
            if request.distance_estimation_behavior == AutonomyDistanceEstimationBehavior.IGNORE_DISTANCE:
                if estimated_distance is not None:
                    estimated_distance = 0
        route_time = None
        if estimated_distance is not None:
            route_time = estimated_distance * date_and_time.REAL_MILLISECONDS_PER_SIM_SECOND / date_and_time.TICKS_PER_REAL_WORLD_SECOND
        return (
         route_time, estimated_distance, must_change_posture, included_sis)
        if False:
            yield None

    def _satisfies_active_desire(self, aop):
        commodity_flags = aop.affordance.commodity_flags
        if commodity_flags & self._formerly_scored_motives:
            return False
        else:
            return self._actively_scored_motives or True
        if commodity_flags & self._actively_scored_motives:
            return True
        return False

    @staticmethod
    def _is_valid_interaction(interaction):
        if not interaction.affordance.autonomy_can_overwrite_similar_affordance:
            if interaction.sim.si_state.is_affordance_active_for_actor(interaction.affordance):
                return TestResult(False, 'Sim is already running the same affordance.')
        return TestResult.TRUE

    def _get_object_result(self, obj, success: bool, reason: str):
        if success:
            return ObjectResult.Success(obj, relevant_desires=(self._actively_scored_motives))
        return ObjectResult.Failure(obj, relevant_desires=(self._actively_scored_motives), reason=reason)

    @classmethod
    def allows_routing(cls):
        return True


class ValidInteractions:

    def __init__(self):
        self._data = {}
        self._refs = {}
        self._counts = {}

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return sims4.repr_utils.standard_angle_repr(self, self._data)

    def __bool__(self):
        if self._data:
            return True
        return False

    def __contains__(self, affordance):
        return affordance.get_affordance_key_for_autonomy() in self._data

    def __getitem__(self, affordance):
        return self._data[affordance.get_affordance_key_for_autonomy()]

    def add(self, scored_interaction_data):
        interaction = scored_interaction_data.interaction
        affordance_key = interaction.affordance.get_affordance_key_for_autonomy()
        self._counts[affordance_key] = 1
        return self._add_internal(interaction, affordance_key, scored_interaction_data)

    def maybe_add(self, scored_interaction_data):
        interaction = scored_interaction_data.interaction
        affordance_key = interaction.affordance.get_affordance_key_for_autonomy()
        previous_data = self._data.get(affordance_key, None)
        if previous_data is None or previous_data.score < scored_interaction_data.score:
            self._counts[affordance_key] = 1
            return self._add_internal(interaction, affordance_key, scored_interaction_data)
        if previous_data.score > scored_interaction_data.score:
            return interaction
        c = self._counts[affordance_key]
        c += 1
        self._counts[affordance_key] = c
        if random.random() < 1 / c:
            return self._add_internal(interaction, affordance_key, scored_interaction_data)
        return interaction

    def _add_internal(self, interaction, affordance_key, scored_interaction_data):
        previous_data = self._data.get(affordance_key)
        self._data[affordance_key] = scored_interaction_data
        if interaction.target is not None:

            def callback(_, self_ref=weakref.ref(self)):
                self = self_ref()
                if self is not None:
                    del self._data[affordance_key]
                    del self._refs[affordance_key]

            self._refs[affordance_key] = interaction.target.ref(callback)
        else:
            self._refs[affordance_key] = None
        if previous_data is not None:
            return previous_data.interaction

    def has_score_for_aop(self, aop):
        affordance_key = aop.affordance.get_affordance_key_for_autonomy()
        if affordance_key not in self._data:
            return False
        scored_interaction_data = self._data[affordance_key]
        return scored_interaction_data.interaction.aop.is_equivalent_to(aop)

    def get_result_scores(self):
        return tuple(self._data.values())


def _dont_timeslice_gen(timeline):
    return False
    if False:
        yield None


class FullAutonomy(_SuperInteractionAutonomy):
    _GSI_IGNORES_NON_AUTONOMOUS_AFFORDANCES = True

    def __init__(self, request):
        super().__init__(request)
        self._relationship_object_value = 0
        self._found_valid_interaction = False
        self._inventory_posture_score_cache = {}
        self._motives_being_solved = None
        self._found_motives = set()
        self._scored_shared_inventory_types = set()
        self._valid_interactions = defaultdict(ValidInteractions)
        self._limited_affordances = defaultdict(list)
        self._gsi_objects = None
        self._gsi_interactions = None
        self._timestamp_when_timeslicing_was_removed = None

    def _clean_up(self):
        for i in AutonomyInteractionPriority:
            if i not in self._valid_interactions:
                continue
            for scored_interaction_data in self._valid_interactions[i].get_result_scores():
                if not scored_interaction_data.interaction.is_super:
                    continue
                scored_interaction_data.interaction.invalidate()

    def __str__(self):
        return 'FullAutonomy'

    def _run_gen(self, timeline, timeslice):
        if self._should_log(self._sim):
            logger.debug('Processing {}', self._sim)
        else:
            gsi_enabled_at_start = gsi_handlers.autonomy_handlers.archiver.enabled
            if gsi_enabled_at_start:
                if self._gsi_objects is None:
                    self._gsi_objects = []
                elif self._gsi_interactions is None:
                    self._gsi_interactions = []
                else:
                    self._actively_scored_motives, motives_to_score = self._get_motives_to_score()
                    return self._actively_scored_motives or self._request.object_list or None
                self._motives_being_solved = self._get_all_motives_currently_being_solved()
                if timeslice is None:
                    timeslice_if_needed_gen = _dont_timeslice_gen
            else:
                start_time = time.clock()

            def timeslice_if_needed_gen(timeline):
                nonlocal start_time
                time_now = time.clock()
                elapsed_time = time_now - start_time
                if elapsed_time < timeslice:
                    return False
                else:
                    if self._timestamp_when_timeslicing_was_removed is not None:
                        enable_long_slice = False
                    else:
                        total_elapsed_time = time_now - self._process_start_time
                        if total_elapsed_time > self.MAX_REAL_SECONDS_UNTIL_TIMESLICING_IS_REMOVED:
                            timeslice_logger.debug('Autonomy request for {} took too long; timeslicing is removed.', self._sim)
                            self._timestamp_when_timeslicing_was_removed = time_now
                            enable_long_slice = False
                        else:
                            enable_long_slice = True
                    start_time_now = time.time()
                    if enable_long_slice:
                        sleep_element = element_utils.sleep_until_next_tick_element()
                    else:
                        sleep_element = elements.SleepElement(date_and_time.TimeSpan(0))
                yield timeline.run_child(sleep_element)
                self._request.on_end_of_time_slicing(start_time_now)
                if not (self._sim is None or self._request.valid):
                    self._clean_up()
                    raise autonomy.autonomy_exceptions.AutonomyExitException()
                start_time = time.clock()
                return True

        best_threshold = None
        while 1:
            self._inventory_posture_score_cache = {}
            self._scored_shared_inventory_types.clear()
            objects_to_score = WeakSet(self._request.objects_to_score_gen(self._actively_scored_motives))
            while True:
                yield from timeslice_if_needed_gen(timeline)
                try:
                    obj = objects_to_score.pop()
                except KeyError:
                    break

                object_result, best_threshold = yield from self._score_object_interactions_gen(timeline, obj, timeslice_if_needed_gen, None, best_threshold)
                if self._gsi_objects is not None:
                    self._gsi_objects.append(object_result.get_log_data())
                inventory_component = obj.is_sim or obj.inventory_component
                if self._should_score_object_inventory(inventory_component):
                    best_threshold = yield from self._score_object_inventory_gen(timeline, inventory_component, timeslice_if_needed_gen, best_threshold)

            for aop_list in self._limited_affordances.values():
                valid_aop_list = [aop_data for aop_data in aop_list if aop_data.aop.target is not None]
                num_aops = len(valid_aop_list)
                if num_aops > self.NUMBER_OF_DUPLICATE_AFFORDANCE_TAGS_TO_SCORE:
                    final_aop_list = []
                    for aop_data in valid_aop_list:
                        autonomy_preference = aop_data.aop.affordance.autonomy_preference
                        if autonomy_preference is not None and self._sim.get_autonomy_preference_type((autonomy_preference.preference.tag), (aop_data.aop.target), True, allow_test=False) >= AutonomyPreferenceType.USE_PREFERENCE:
                            final_aop_list.append(aop_data)

                    num_final_aops = len(final_aop_list)
                    if num_final_aops < self.NUMBER_OF_DUPLICATE_AFFORDANCE_TAGS_TO_SCORE:
                        non_preferred_aops = [aop_data for aop_data in valid_aop_list if aop_data not in final_aop_list]
                        if non_preferred_aops:
                            final_aop_list.extend(random.sample(non_preferred_aops, self.NUMBER_OF_DUPLICATE_AFFORDANCE_TAGS_TO_SCORE - num_final_aops))
                        else:
                            final_aop_list = valid_aop_list
                    if self._gsi_interactions is not None:
                        for aop_data in valid_aop_list:
                            if aop_data not in final_aop_list:
                                self._gsi_interactions.append(InteractionResult.Failure((aop_data.aop),
                                  (AutonomyStageLabel.BEFORE_TESTS), (self._actively_scored_motives), reason=('Randomly discarded due to limited autonomy for {}'.format(aop_data.aop.affordance.duplicate_affordance_group))))

                    for aop_data in final_aop_list:
                        interaction_result, interaction, route_time = yield from self._create_and_score_interaction(timeline, aop_data.aop, aop_data.inventory_type, best_threshold, aop_data.outside_multiplier)
                        if not interaction_result:
                            if self._request.record_test_result is not None:
                                self._request.record_test_result(aop_data.aop, '_create_and_score_interaction', interaction_result)
                            if self._gsi_interactions is not None:
                                self._gsi_interactions.append(interaction_result)
                                continue
                            _, best_threshold = self._process_scored_interaction(aop_data.aop, interaction, interaction_result, route_time, best_threshold)

                    self._limited_affordances.clear()
                    if not motives_to_score:
                        break
                    self._formerly_scored_motives.update(self._actively_scored_motives)
                    variance_score = self._motive_scores[motives_to_score[0]]
                    for motive in self._found_motives:
                        variance_score = max(variance_score, self._motive_scores[motive])

                    variance_score *= AutonomyMode.FULL_AUTONOMY_STATISTIC_SCORE_VARIANCE
                    self._actively_scored_motives = {stat.stat_type for stat in itertools.takewhile(lambda desire: self._motive_scores[desire] >= variance_score, motives_to_score)}
                    if not self._actively_scored_motives:
                        break
                    if self._found_valid_interaction:
                        motives_to_score = []
                else:
                    motives_to_score = motives_to_score[len(self._actively_scored_motives):]

        final_valid_interactions = None
        for i in AutonomyInteractionPriority:
            if i not in self._valid_interactions:
                continue
            valid_interactions = self._valid_interactions[i]
            if valid_interactions:
                final_valid_interactions = valid_interactions
                break

        self._request.valid_interactions = final_valid_interactions
        if self._gsi_interactions is not None:
            self._request.gsi_data = {GSIDataKeys.COMMODITIES_KEY: self._motive_scores.values(), 
             GSIDataKeys.AFFORDANCE_KEY: self._gsi_interactions, 
             GSIDataKeys.PROBABILITY_KEY: [], 
             GSIDataKeys.OBJECTS_KEY: self._gsi_objects, 
             GSIDataKeys.MIXER_PROVIDER_KEY: None, 
             GSIDataKeys.MIXERS_KEY: [], 
             GSIDataKeys.REQUEST_KEY: self._request.get_gsi_data()}
        return final_valid_interactions
        if False:
            yield None

    @classmethod
    def _get_autonomous_delay_time_in_sim_minutes(cls):
        if cls._full_autonomy_delay_override is None:
            return cls.FULL_AUTONOMY_DELAY.random_float()
        return random.uniform(cls._full_autonomy_delay_override.lower_bound, cls._full_autonomy_delay_override.upper_bound)

    @classmethod
    def test(cls, sim):
        if services.game_clock_service().clock_speed == ClockSpeedMode.SUPER_SPEED3:
            return TestResult(False, 'In or has super speed three request')
            if sim.get_autonomy_state_setting() <= autonomy.settings.AutonomyState.LIMITED_ONLY:
                return TestResult(False, 'Limited autonomy and below can never run full autonomy')
            if sim.get_autonomy_state_setting() == autonomy.settings.AutonomyState.MEDIUM:
                if sim.si_state.has_user_directed_si():
                    return TestResult(False, 'Medium Autonomy but has a user directed interaction in si state.')
            if sim.queue is None:
                logger.warn('sim.queue is None in FullAutonomy.test()', owner='rez')
                return TestResult(False, 'Sim Partially destroyed.')
            result = cls._test_pending_interactions(sim)
            if not result:
                return result
            if sim.is_player_active():
                return TestResult(False, 'Sim actively being played.')
        else:
            master = sim.routing_master
            if master is not None:
                if master.is_sim:
                    slave_data = master.get_formation_data_for_slave(sim)
                    master_path = master.routing_component.current_path
                    if master_path is not None:
                        if slave_data.should_slave_for_path(master_path):
                            return TestResult(False, 'Slaved to {}, who is routing.'.format(master))
                    if master.transition_controller is not None:
                        transition_spec = master.transition_controller.get_transition_spec(master)
                        if transition_spec is not None and transition_spec.path is not None:
                            if slave_data.should_slave_for_path(transition_spec.path):
                                return TestResult(False, 'Slaved to {}, who wants to route somewhere.'.format(master))
        return TestResult.TRUE

    def _is_available(self, obj):
        super_result = super()._is_available(obj)
        if not super_result:
            return super_result
        if self._request.radius_to_consider_squared > 0:
            delta = obj.intended_position - self._sim.intended_position
            if delta.magnitude_squared() > self._request.radius_to_consider_squared:
                return self._get_object_result(obj, success=False, reason='Target object is too far away from the sim.')
        context = self._request.context
        if obj.is_sim:
            if context.source == context.SOURCE_AUTONOMY:
                for interaction in tuple(obj.si_state):
                    if interaction.disallows_full_autonomy(self._disable_autonomous_multitasking_if_user_directed_override):
                        return self._get_object_result(obj, success=False, reason='Target sim is running an interaction that disallows multi tasking.')

        return super_result

    @cached
    def _get_outside_score_modifications(self, obj, sim):
        if self._request.context.source != InteractionSource.AUTONOMY:
            return (False, 1.0)
        else:
            if obj.is_in_sim_inventory(sim):
                return (False, 1.0)
            if obj.is_outside:
                return sim.sim_info.get_outside_object_score_modification()
            if obj.is_sim and sim.is_outside:
                return obj.sim_info.get_outside_object_score_modification()
        return (False, 1.0)

    def _should_score_object_inventory(self, inventory_component):
        if inventory_component is None:
            return False
        else:
            if not inventory_component.should_score_contained_objects_for_autonomy:
                return False
            inventory_type = inventory_component.inventory_type
            if InventoryTypeTuning.is_shared_between_objects(inventory_type) and inventory_type in self._scored_shared_inventory_types:
                return False
        return True

    def _score_object_inventory_gen(self, timeline, inventory_component, timeslice_if_needed_gen, best_threshold):
        inventory_type = inventory_component.inventory_type
        for inventory_obj in inventory_component.get_items_for_autonomy_gen(motives=(self._actively_scored_motives)):
            object_result, best_threshold = yield from self._score_object_interactions_gen(timeline, inventory_obj, timeslice_if_needed_gen, inventory_type, best_threshold)
            if self._gsi_objects is not None:
                self._gsi_objects.append(object_result.get_log_data())

        if InventoryTypeTuning.is_shared_between_objects(inventory_type):
            self._scored_shared_inventory_types.add(inventory_type)
        return best_threshold
        if False:
            yield None

    def _get_potential_interactions(self, obj):
        return tuple((obj.potential_interactions)((self._request.context), **(self._request).kwargs))

    def _score_object_interactions_gen(self, timeline, obj, timeslice_if_needed_gen, inventory_type, best_threshold):
        context = self._request.context
        obj_ref = obj.ref()
        is_available = self._is_available(obj)
        if not is_available:
            return (
             is_available, best_threshold)
        potential_interactions = self._get_potential_interactions(obj)
        is_outside_supressed, object_outside_multiplier = self._get_outside_score_modifications(obj, self._sim)
        for aop in potential_interactions:
            yielded_due_to_timeslice = yield from timeslice_if_needed_gen(timeline)
            if yielded_due_to_timeslice:
                if obj_ref() is None:
                    return (
                     ObjectResult.Failure(obj, self._actively_scored_motives, 'Object deleted.'), best_threshold)
            if not aop.affordance.is_super:
                if context.sim is not self._sim:
                    logger.error('A non-super interaction was returned from potential_interactions(): {}', aop, owner='rez')
                    continue
                outside_multiplier = object_outside_multiplier
                if is_outside_supressed or outside_multiplier != 1.0:
                    if not aop.affordance.counts_as_inside:
                        if is_outside_supressed:
                            if self._gsi_interactions is not None:
                                self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_TESTS), (self._actively_scored_motives), reason='Sim has an outside lock which prevents it from running interaction'))
                                continue
            else:
                outside_multiplier = 1.0
            if self._request.affordance_list is not None:
                if aop.affordance not in self._request.affordance_list:
                    continue
            if aop.affordance.target_type == interactions.TargetType.ACTOR:
                if self._sim is not obj:
                    continue
            if not self._satisfies_active_desire(aop):
                if self._request.record_test_result is not None:
                    self._request.record_test_result(aop, '_satisfies_desire', None)
                if self._gsi_interactions is not None:
                    self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_TESTS), (self._actively_scored_motives), reason='Failed to satisfy relevant desires: {}',
                      reason_args=(
                     aop.affordance.commodity_flags,)))
                    continue
                test_result = self._allow_autonomous(aop)
                if not test_result:
                    if self._GSI_IGNORES_NON_AUTONOMOUS_AFFORDANCES or self._request.record_test_result is not None:
                        self._request.record_test_result(aop, '_allow_autonomous', None)
            if self._gsi_interactions is not None:
                self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_TESTS), (self._actively_scored_motives), reason="aop doesn't advertise to autonomy."))
                continue
            if self._valid_interactions[aop.affordance.scoring_priority].has_score_for_aop(aop):
                continue
            if self._request.skipped_affordance_list:
                if aop.affordance in self._request.skipped_affordance_list:
                    if self._request.record_test_result is not None:
                        self._request.record_test_result(aop, 'skipped_affordance_list', None)
                    if self._gsi_interactions is not None:
                        self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_TESTS), (self._actively_scored_motives), reason='Affordance in skipped_affordance_list'))
                        continue
            if self._request.skipped_static_commodities:
                if self._satisfies_desire(self._request.skipped_static_commodities, aop):
                    if self._request.record_test_result is not None:
                        self._request.record_test_result(aop, '_satisfies_desire', None)
                    if self._gsi_interactions is not None:
                        self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_TESTS), (self._actively_scored_motives), reason='AOP satisfies explicitly skipped commodity'))
                        continue
            if self._request.constraint is not None:
                aop_constraint = aop.constraint_intersection((self._sim), target=obj, posture_state=None)
                if aop_constraint is not None:
                    aop_constraint = aop_constraint.intersect(self._request.constraint)
                    if not aop_constraint.valid:
                        if self._request.record_test_result is not None:
                            self._request.record_test_result(aop, 'invalid_constraint', None)
                        if self._gsi_interactions is not None:
                            self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_TESTS), (self._actively_scored_motives), reason='Failed constraint intersection'))
                            continue
            self._relationship_object_value = 0
            if obj.has_component(objects.components.types.CRAFTING_COMPONENT):
                crafter_id = obj.get_crafting_process().crafter_sim_id
                if crafter_id is not None:
                    relationship_track = self._sim.sim_info.relationship_tracker.get_relationship_track(crafter_id)
                    if relationship_track:
                        relationship_score = relationship_track.get_value()
                        logger.assert_log(relationship_track.relationship_obj_prefence_curve is not None, 'Error: Tuning for RelationshipTrack: {}, Relationship Object Preference Curve is not tuned.'.format(type(relationship_track).__name__))
                        self._relationship_object_value = relationship_track.relationship_obj_prefence_curve.get(relationship_score)
            test_result = self._test_aop(aop)
            if not test_result:
                if self._request.record_test_result is not None:
                    self._request.record_test_result(aop, '_test_aop', None)
                if self._gsi_interactions is not None:
                    self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_TESTS), (self._actively_scored_motives), reason=(test_result.reason)))
                    continue
            if obj.check_affordance_for_suppression(self._sim, aop, False):
                if self._request.record_test_result is not None:
                    self._request.record_test_result(aop, 'check_affordance_for_suppression', None)
                if self._gsi_interactions is not None:
                    self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_TESTS), (self._actively_scored_motives), reason='aop is being supressed by something'))
                    continue
                duplicate_affordance_group = aop.affordance.duplicate_affordance_group
                if duplicate_affordance_group != Tag.INVALID:
                    self._limited_affordances[duplicate_affordance_group].append(_DeferredAopData(aop, inventory_type, outside_multiplier))
                    continue
            interaction_result, interaction, route_time = yield from self._create_and_score_interaction(timeline, aop, inventory_type, best_threshold, outside_multiplier)
            if not interaction_result:
                if self._request.record_test_result is not None:
                    self._request.record_test_result(aop, '_create_and_score_interaction', interaction_result)
                if self._gsi_interactions is not None:
                    self._gsi_interactions.append(interaction_result)
                    continue
                _, best_threshold = self._process_scored_interaction(aop, interaction, interaction_result, route_time, best_threshold)

        return (
         ObjectResult.Success(obj, relevant_desires=(self._actively_scored_motives)), best_threshold)
        if False:
            yield None

    def _create_and_score_interaction(self, timeline, aop, inventory_type, best_threshold, outside_multiplier):
        execute_result = aop.interaction_factory(self._request.context)
        if not execute_result:
            return (
             InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_POSTURE_SEARCH), (self._actively_scored_motives), reason='Failed to execute aop!'), None, 0)
        interaction = execute_result.interaction
        self._request.on_interaction_created(interaction)
        test_result = self._is_valid_interaction(interaction)
        if not test_result:
            if self._request.record_test_result is not None:
                self._request.record_test_result(aop, '_is_valid_aop', test_result)
            return (
             InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_POSTURE_SEARCH), (self._actively_scored_motives), reason=(test_result.reason)), None, 0)
        posture_result_tuple = None
        if inventory_type is not None:
            posture_result_tuple = self._inventory_posture_score_cache.get(inventory_type)
        sim = self._sim
        autonomy_preference = aop.affordance.autonomy_preference
        preference_type = AutonomyPreferenceType.ALLOWED
        if autonomy_preference is not None and not autonomy_preference.preference.is_scoring:
            preference_type = self._sim.get_autonomy_preference_type(autonomy_preference.preference.tag, aop.target, True)
            if preference_type == AutonomyPreferenceType.DISALLOWED:
                if self._request.context.source != InteractionContext.SOURCE_PIE_MENU:
                    return (InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_POSTURE_SEARCH), (self._actively_scored_motives), reason='Disallowed by autonomy preference'), None, 0)
            if posture_result_tuple is None:
                if best_threshold is not None:
                    if preference_type == AutonomyPreferenceType.ALLOWED:
                        best_scoring_rank, target_score = best_threshold
                        if self.FULL_AUTONOMY_INTERACTION_PRIORITY_RANKING.get(interaction.scoring_priority, 0) < best_scoring_rank:
                            return (
                             InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_POSTURE_SEARCH), (self._actively_scored_motives), reason='Already found an affordance with a higher scoring priority (ours is {})',
                               reason_args=(
                              interaction.scoring_priority,)), None, 0)
                        optimistic_score, _optimistic_multitask_percentage = self._calculate_interaction_score(interaction, 0, 0, False, None, True, outside_multiplier)
                        if optimistic_score < target_score:
                            return (
                             InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_POSTURE_SEARCH), (self._actively_scored_motives), reason='Optimistic score of {:02f} less than current target of {:02f}\nScore Details\n{}',
                               reason_args=(
                              optimistic_score, target_score, optimistic_score)), None, 0)
            if posture_result_tuple is None:
                rt_start = None
                if self._request.autonomy_ping_request_record is not None:
                    rt_start = time.time()
                try:
                    with autonomy.autonomy_util.AutonomyAffordanceTimes.profile(interaction.affordance.__name__):
                        posture_result_tuple = yield from self._calculate_route_time_and_opportunity(timeline, interaction)
                except Exception as exception:
                    try:
                        logger.exception('Posture graph threw an exception while being queried by autonomy:', exc=exception,
                          level=(sims4.log.LEVEL_ERROR))
                        return (InteractionResult.Failure(aop, (AutonomyStageLabel.BEFORE_POSTURE_SEARCH), (self._actively_scored_motives), reason='Posture Graph Threw Exception'), None, 0)
                    finally:
                        exception = None
                        del exception

                self._request.on_end_of_calculate_route_time(rt_start)
                if inventory_type is not None:
                    self._inventory_posture_score_cache[inventory_type] = posture_result_tuple
            logger.assert_raise(posture_result_tuple is not None, "Couldn't get posture score for {}".format(aop))
            route_time, estimated_distance, must_change_posture, included_sis = posture_result_tuple
            if route_time is None:
                reason = 'Failed to plan a path that would satisfy all required SIs!'
                return (
                 InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_POSTURE_SEARCH), (self._actively_scored_motives), reason=reason), None, 0)
        if must_change_posture:
            if not self._request.is_script_request:
                for si in sim.si_state.all_guaranteed_si_gen(priority=(self._request.context.priority), group_id=(interaction.group_id)):
                    if not (sim.posture_state.is_source_interaction(si) or si.apply_autonomous_posture_change_cost):
                        continue
                    return (
                     InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_POSTURE_SEARCH), (self._actively_scored_motives), reason="Can't change posture while in guaranteed SI!"), None, 0)

        affordance_score, multitask_percentage = self._calculate_interaction_score(interaction, route_time, estimated_distance, must_change_posture, included_sis, False, outside_multiplier)
        return (
         InteractionResult.Success(interaction, (self._actively_scored_motives), score=affordance_score, multitask_percentage=multitask_percentage), interaction, route_time)
        if False:
            yield None

    def _calculate_interaction_score(self, interaction, route_time, estimated_distance, must_change_posture, included_sis, optimistic, outside_multiplier):
        if self._gsi_interactions is not None:
            gsi_commodity_scores = []
        else:
            gsi_commodity_scores = None
        affordance = interaction.affordance
        interaction_score = 0
        approximate_duration = affordance.approximate_duration
        efficiency = approximate_duration / (approximate_duration + route_time)
        autonomy_scoring_preference = self._get_autonomy_scoring_preference(interaction)
        no_stat_ops = True
        for stat_op_list in self._applicable_stat_ops_gen(interaction, include_hidden_false_ads=True, gsi_commodity_scores=gsi_commodity_scores):
            no_stat_ops = False
            fulfillment_rate = stat_op_list.get_fulfillment_rate(interaction)
            already_solving_motive_multiplier = self.FULL_AUTONOMY_MULTIPLIER_FOR_SOLVING_THE_SAME_STAT if stat_op_list.stat in self._motives_being_solved else 1
            object_stat_use_multiplier = self._calculate_object_stat_use_multiplier(interaction.target, stat_op_list.stat, fulfillment_rate >= 0)
            modified_desire = self._motive_scores.get(stat_op_list.stat, stat_op_list.stat.autonomous_desire)
            op_score = fulfillment_rate * object_stat_use_multiplier * already_solving_motive_multiplier * efficiency * autonomy_scoring_preference * modified_desire * stat_op_list.stat.autonomy_weight
            interaction_score += op_score
            commodity_value = stat_op_list.get_value(interaction)
            if gsi_commodity_scores is not None:
                gsi_commodity_scores.append(InteractionCommodityScore(op_score, (stat_op_list.stat), advertise=True, commodity_value=commodity_value, interval=(commodity_value / fulfillment_rate if fulfillment_rate else None),
                  fulfillment_rate=fulfillment_rate,
                  object_stat_use_multiplier=object_stat_use_multiplier,
                  already_solving_motive_multiplier=already_solving_motive_multiplier,
                  modified_desire=modified_desire))

        for static_commodity_data in interaction.affordance.static_commodities_data:
            static_commodity = static_commodity_data.static_commodity
            if not static_commodity.is_scored:
                if gsi_commodity_scores is not None:
                    gsi_commodity_scores.append(InteractionCommodityScore(0, static_commodity, advertise=False))
                    continue
            if static_commodity not in self._motive_scores:
                if gsi_commodity_scores is not None:
                    gsi_commodity_scores.append(InteractionCommodityScore(0, static_commodity, advertise=True))
                    continue
                no_stat_ops = False
                op_score = static_commodity.ad_data * static_commodity_data.desire * efficiency * autonomy_scoring_preference
                interaction_score += op_score
                if gsi_commodity_scores is not None:
                    gsi_commodity_scores.append(InteractionCommodityScore(op_score, static_commodity, advertise=True, commodity_value=(static_commodity_data.desire),
                      interval=1,
                      fulfillment_rate=(static_commodity_data.desire),
                      modified_desire=(static_commodity.ad_data)))

        if no_stat_ops:
            interaction_score = efficiency
            if gsi_commodity_scores is not None:
                gsi_commodity_scores.append(InteractionCommodityScore(score=efficiency, commodity=None, advertise=True))
        outside_multiplier_override = interaction.get_outside_score_multiplier_override()
        if outside_multiplier_override is not None:
            outside_multiplier = outside_multiplier_override
        else:
            interaction_score *= outside_multiplier
            interaction_params = interaction.interaction_parameters
            join_target_ref = interaction_params.get('join_target_ref')
            if join_target_ref is not None:
                target_sim = join_target_ref()
            else:
                target_sim = interaction.target if (interaction.target is not None and interaction.target.is_sim) else None
        rel_utility_score = 1
        group_utility_score = 1
        buff_utility_score = 1
        tested_relationship_utility_score = 1
        situation_type_utility_score = 1
        if affordance.relationship_scoring:
            if target_sim is not None:
                final_rel_score = 0
                final_rel_count = 0
                rel_tracker = self._sim.sim_info.relationship_tracker
                target_sims = set((target_sim,))
                for social_group in target_sim.get_groups_for_sim_gen():
                    for sim in social_group:
                        target_sims.add(sim)

                for sim in target_sims:
                    aggregate_track_score = [track.autonomous_desire for track in rel_tracker.relationship_tracks_gen(sim.id) if track.is_scored]
                    track_score = sum(aggregate_track_score) / len(aggregate_track_score) if aggregate_track_score else 1
                    bit_score = 1
                    for bit in rel_tracker.get_all_bits(sim.id):
                        bit_score *= bit.autonomy_multiplier

                    rel_score = track_score * bit_score
                    final_rel_score += rel_score
                    final_rel_count += 1

                rel_utility_score = final_rel_score / final_rel_count if final_rel_count > 0 else 1
                target_main_group = target_sim.get_main_group()
                if target_main_group:
                    group_utility_score = affordance.get_affordance_weight_from_group_size(len(target_main_group))
                    for group_member in target_main_group:
                        if group_member is target_sim:
                            continue
                        if group_member.is_player_active():
                            group_utility_score *= AutonomyMode.FULL_AUTONOMY_DESIRE_TO_JOIN_PLAYER_PARTIES
                            break

                relationship_score_multipliers_for_buffs = self._sim.sim_info.get_relationship_score_multiplier_for_buff_on_target()
                if relationship_score_multipliers_for_buffs is not None:
                    for buff_type, multipliers in relationship_score_multipliers_for_buffs.items():
                        if target_sim.has_buff(buff_type):
                            buff_utility_score *= reduce(operator.mul, multipliers, 1)

                tested_relationship_score_multipliers = self._sim.sim_info.get_tested_relationship_score_multipliers()
                if tested_relationship_score_multipliers is not None:
                    resolver = SingleSimResolver(self._sim.sim_info)
                    for tested_multiplier in tested_relationship_score_multipliers:
                        if tested_multiplier.tests.run_tests(resolver):
                            tested_relationship_utility_score *= tested_multiplier.multiplier

                situation_type_social_score_multiplier = self._sim.sim_info.get_situation_type_social_score_multiplier()
                if situation_type_social_score_multiplier is not None:
                    situation_manager = services.get_zone_situation_manager()
                    situations_sim_is_in = situation_manager.get_situations_sim_is_in(self._sim)
                    for situation_type, multipliers in situation_type_social_score_multiplier.items():
                        for situation in situations_sim_is_in:
                            if type(situation) == situation_type and target_sim in situation.all_sims_in_situation_gen():
                                situation_type_utility_score *= reduce(operator.mul, multipliers, 1)

        interaction_score *= rel_utility_score * group_utility_score * buff_utility_score * situation_type_utility_score * tested_relationship_utility_score
        waiting_in_line_multiplier = 1
        if interaction.waiting_line is not None:
            if interaction.target is not None:
                waiting_in_line_multiplier = interaction.target.get_waiting_line_autonomy_multiplier(interaction)
                interaction_score *= waiting_in_line_multiplier
            interaction_score_modifier_multiplier = 1
            for interaction_score_modifier in self._sim.sim_info.get_interaction_score_modifier(interaction):
                if interaction.interaction_category_tags & interaction_score_modifier.interaction_category_tags:
                    interaction_score_modifier_multiplier = interaction_score_modifier.modifier
                    break
                affordance = type(interaction)
                if affordance in interaction_score_modifier.affordances:
                    interaction_score_modifier_multiplier = interaction_score_modifier.modifier
                    break
                if any((affordance in affordances for affordances in interaction_score_modifier.affordance_lists)):
                    interaction_score_modifier_multiplier = interaction_score_modifier.modifier
                    break

            interaction_score *= interaction_score_modifier_multiplier
            distance_to_object_multiplier = self._sim.sim_info.get_distance_to_object_based_multiplier(interaction)
            interaction_score *= distance_to_object_multiplier
            interaction_score *= 1 + self._relationship_object_value
            apply_penalty = False
            if interaction.target is not None:
                apply_penalty = True
                tolerance = self._sim.get_off_lot_autonomy_rule().tolerance
                sim_on_active_lot = self._sim.is_on_active_lot(tolerance=tolerance)
                if sim_on_active_lot:
                    target_on_lot = interaction.target.is_on_active_lot(tolerance=tolerance)
                    if target_on_lot:
                        apply_penalty = False
            else:
                sim_on_active_lot = self._sim.is_on_active_lot()
                if not sim_on_active_lot:
                    apply_penalty = False
        else:
            apply_penalty = False
        if apply_penalty:
            interaction_score *= self.OFF_LOT_OBJECT_SCORE_MULTIPLIER
        canceled_si_opportunity_costs = {}
        if optimistic:
            canceled_sis = []
        else:
            total_opportunity_cost = 0
            canceled_sis = [si for si in self._sim.si_state if si not in included_sis]
            if self._request.apply_opportunity_cost:
                affordance_is_active_on_actor = self._sim.si_state.is_affordance_active_for_actor(affordance)
                for canceled_si in canceled_sis:
                    if not canceled_si.canceling_incurs_opportunity_cost:
                        continue
                    if affordance_is_active_on_actor:
                        if canceled_si.autonomy_can_overwrite_similar_affordance:
                            continue
                    if canceled_si.is_finishing:
                        continue
                    canceled_si_score = self._calculate_stat_op_score_for_running_si(canceled_si)
                    final_si_opportunity_cost = canceled_si_score * canceled_si.opportunity_cost_multiplier
                    canceled_si_opportunity_costs[canceled_si] = final_si_opportunity_cost
                    total_opportunity_cost += final_si_opportunity_cost

                if must_change_posture:
                    if interaction.apply_autonomous_posture_change_cost:
                        if self._sim.si_state.has_visible_si():
                            total_opportunity_cost *= self.POSTURE_CHANGE_OPPORTUNITY_COST_MULTIPLIER
                interaction_score -= total_opportunity_cost
            sit_posture_transition_penalty = 1.0
            if must_change_posture:
                if type(self._sim.posture_state.body) is PostureConstants.SIT_POSTURE_TYPE:
                    modifiers = self._sim.sim_info.get_sit_posture_transition_penalties()
                    sit_posture_transition_penalty *= reduce(operator.mul, modifiers, 1)
            else:
                interaction_score *= sit_posture_transition_penalty
                remaining_sis_score = self._score_current_si_state(skip_sis=canceled_sis, gsi_commodity_scores=gsi_commodity_scores)
                interaction_score += remaining_sis_score
                club_service = services.get_club_service()
                if club_service is not None:
                    club_rule_multiplier = club_service.get_interaction_score_multiplier(interaction)
                    interaction_score *= club_rule_multiplier
                else:
                    club_rule_multiplier = 1.0
            attention_cost_scores = {}
            bonus_multitasking_percentage = 0
            attention_cost_bonus_scores = {}
            penalty_multitasking_percentage = 0
            attention_cost_penalty_scores = {}
            if optimistic:
                base_multitasking_percentage = 0
                final_multitasking_percentage = 0
            else:
                attention_cost = 0
                if not interaction.target is None:
                    attention_cost = interaction.target.is_sim or self._calculate_attention_cost_for_current_si_state((self._sim), skip_sis=canceled_sis, attention_cost_scores=attention_cost_scores)
                else:
                    actor_attention_cost_scores = {}
                    target_attention_cost_scores = {}
                    actor_cost = self._calculate_attention_cost_for_current_si_state((self._sim), skip_sis=canceled_sis, attention_cost_scores=actor_attention_cost_scores)
                    target_cost = self._calculate_attention_cost_for_current_si_state((interaction.target), attention_cost_scores=target_attention_cost_scores)
                    if actor_cost <= target_cost:
                        attention_cost = actor_cost
                        attention_cost_scores.update(actor_attention_cost_scores)
                    else:
                        attention_cost = target_cost
                        attention_cost_scores.update(target_attention_cost_scores)
                interaction_attention_cost = interaction.get_attention_cost() if attention_cost != 0 else 0
                attention_cost += interaction_attention_cost
                attention_cost_scores[interaction] = (interaction_attention_cost, True)
                base_multitasking_percentage = self.FULL_AUTONOMY_ATTENTION_COST.get(attention_cost)
                if not no_stat_ops:
                    for stat_op_list in self._applicable_stat_ops_gen(interaction):
                        modified_desire = self._motive_scores.get(stat_op_list.stat, stat_op_list.stat.autonomous_desire)
                        bonus = self.FULL_AUTONOMY_MULTITASKING_PERCENTAGE_BONUS.get(modified_desire)
                        bonus_multitasking_percentage += bonus
                        attention_cost_bonus_scores[stat_op_list.stat] = (modified_desire, bonus)

                for static_commodity_data in interaction.affordance.static_commodities_data:
                    static_commodity = static_commodity_data.static_commodity
                    if static_commodity not in self._motive_scores:
                        continue
                    modified_desire = static_commodity.ad_data
                    bonus = self.FULL_AUTONOMY_MULTITASKING_PERCENTAGE_BONUS.get(modified_desire)
                    bonus_multitasking_percentage += bonus
                    attention_cost_bonus_scores[static_commodity] = (modified_desire, bonus)

                for si in included_sis:
                    for stat_op_list in self._applicable_stat_ops_gen(si):
                        modified_desire = self._motive_scores.get(stat_op_list.stat, stat_op_list.stat.autonomous_desire)
                        penalty = self.FULL_AUTONOMY_MULTITASKING_PERCENTAGE_BONUS.get(modified_desire)
                        penalty_multitasking_percentage += penalty
                        attention_cost_penalty_scores[stat_op_list.stat] = (modified_desire, penalty)

                final_multitasking_percentage = base_multitasking_percentage + bonus_multitasking_percentage - penalty_multitasking_percentage
            ensemble_multiplier = 1
            if affordance.ensemble_scoring:
                ensemble_multiplier = services.ensemble_service().get_ensemble_multiplier(interaction.sim, interaction.target)
                interaction_score *= ensemble_multiplier
            else:
                final_score = interaction_score
                if final_score <= self._MINIMUM_SCORE:
                    final_score = 0
                if gsi_commodity_scores is not None:
                    interaction_score = InteractionScore(final_score, interaction,
                      gsi_commodity_scores,
                      efficiency,
                      approximate_duration,
                      autonomy_scoring_preference,
                      rel_utility_score,
                      (self._relationship_object_value),
                      group_utility_score,
                      opportunity_costs=canceled_si_opportunity_costs,
                      must_change_posture=must_change_posture,
                      base_multitasking_percentage=base_multitasking_percentage,
                      bonus_multitasking_percentage=bonus_multitasking_percentage,
                      penalty_multitasking_percentage=penalty_multitasking_percentage,
                      attention_cost_scores=attention_cost_scores,
                      attention_cost_bonus_scores=attention_cost_bonus_scores,
                      attention_cost_penalty_scores=attention_cost_penalty_scores,
                      outside_multiplier=outside_multiplier,
                      waiting_in_line_multiplier=waiting_in_line_multiplier,
                      club_rule_multiplier=club_rule_multiplier,
                      buff_utility_score=buff_utility_score,
                      situation_type_utility_score=situation_type_utility_score,
                      sit_posture_transition_penalty=sit_posture_transition_penalty,
                      estimated_distance=estimated_distance,
                      route_time=route_time,
                      tested_relationship_utility_score=tested_relationship_utility_score,
                      off_lot_object_score_multiplier=(1 if apply_penalty is False else self.OFF_LOT_OBJECT_SCORE_MULTIPLIER),
                      remaining_sis_score=remaining_sis_score,
                      interaction_score_modifier_multiplier=interaction_score_modifier_multiplier,
                      ensemble_multiplier=ensemble_multiplier,
                      minimum_score=(self._MINIMUM_SCORE))
                else:
                    interaction_score = final_score
            return (
             interaction_score, final_multitasking_percentage)

    def _process_scored_interaction(self, aop, interaction, interaction_result, route_time, best_threshold):
        if not self._has_available_part(interaction):
            if self._request.record_test_result is not None:
                self._request.record_test_result(aop, '_has_available_part', None)
        else:
            if self._gsi_interactions is not None:
                self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_SCORING), (self._actively_scored_motives), reason="Object doesn't have an available part"))
            return (
             False, best_threshold)
            interaction_to_shutdown = None
            invalidate_interaction = True
            try:
                if aop.target is None or aop.target.parts is None:
                    if interaction.target is None or interaction.target.parts is None:
                        handler = self._request.is_script_request or interaction.get_interaction_reservation_handler(sim=(self._sim))
                        if handler is not None and not handler.may_reserve():
                            if self._request.record_test_result is not None:
                                self._request.record_test_result(aop, '_is_available', None)
                            if self._gsi_interactions is not None:
                                self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_SCORING), (self._actively_scored_motives), reason='Interaction cannot reserve object.'))
                    else:
                        interaction_to_shutdown = interaction
                        return (False, best_threshold)
                interaction_score = interaction_result.score
                scored_interaction_data = ScoredInteractionData(interaction_score, route_time, interaction_result.multitask_percentage, interaction)
                context = self._request.context
                if context.source == context.SOURCE_AUTONOMY and not self._request.consider_scores_of_zero:
                    if interaction_score <= 0:
                        if self._request.record_test_result is not None:
                            self._request.record_test_result(aop, 'score_below_zero', None)
                        if self._gsi_interactions is not None:
                            self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_SCORING), (self._actively_scored_motives), reason='Scored below zero ({})',
                              reason_args=(
                             interaction_score,)))
                        interaction_to_shutdown = interaction
                        return (False, best_threshold)
                    if self._actively_scored_motives:
                        self._found_motives.update(self._actively_scored_motives & aop.affordance.commodity_flags)
                    if not interaction.use_best_scoring_aop:
                        if interaction.affordance not in self._request.similar_aop_cache:
                            self._request.similar_aop_cache[interaction.affordance] = []
                        self._request.similar_aop_cache[interaction.affordance].append(scored_interaction_data)
                        invalidate_interaction = False
                    force_replace = False
                    valid_interactions_at_priority = self._valid_interactions[interaction.scoring_priority]
                    if aop.affordance in valid_interactions_at_priority:
                        scored_interaction_data_to_compare = valid_interactions_at_priority[aop.affordance]
                        autonomy_preference = aop.affordance.autonomy_preference
                        if autonomy_preference is not None:
                            tag = autonomy_preference.preference.is_scoring or autonomy_preference.preference.tag
                            if self._sim.get_autonomy_preference_type(tag, (aop.target), True, allow_test=False) >= AutonomyPreferenceType.USE_PREFERENCE:
                                force_replace = True
                else:
                    if self._sim.get_autonomy_preference_type(tag, (scored_interaction_data_to_compare.interaction.target), True, allow_test=False) < AutonomyPreferenceType.USE_PREFERENCE:
                        if self._gsi_interactions is not None:
                            self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_SCORING), (self._actively_scored_motives), reason='There is another scored interaction with use preference: {}\n{}',
                              reason_args=(
                             scored_interaction_data_to_compare.interaction, interaction_result.score.details)))
                        interaction_to_shutdown = interaction
                        return (False, best_threshold)
                    elif not force_replace:
                        if interaction_score < scored_interaction_data_to_compare.score:
                            if self._request.record_test_result is not None:
                                self._request.record_test_result(aop, 'score_below_similar_aop', None)
                            elif self._gsi_interactions is not None:
                                if interaction.use_best_scoring_aop:
                                    self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_SCORING), (self._actively_scored_motives), reason='Score <= another affordance that has been scored ({} < {})',
                                      reason_args=(
                                     interaction_score, scored_interaction_data_to_compare.score)))
                                else:
                                    self._gsi_interactions.append(InteractionResult.Success(aop, self._actively_scored_motives, interaction_score, interaction_result.multitask_percentage))
                            interaction_to_shutdown = interaction
                            return (False, best_threshold)
                        if interaction_score == 0:
                            if interaction_score == scored_interaction_data_to_compare.score:
                                if route_time > scored_interaction_data_to_compare.route_time:
                                    if self._request.record_test_result is not None:
                                        self._request.record_test_result(aop, 'zero_scoring_aop_is_further_away', None)
                                    if self._gsi_interactions is not None:
                                        self._gsi_interactions.append(InteractionResult.Failure(aop, (AutonomyStageLabel.AFTER_SCORING), (self._actively_scored_motives), reason='Score == 0, but is further away than another affordance that has been scored ({} further than {})',
                                          reason_args=(
                                         route_time, scored_interaction_data_to_compare.route_time)))
                                    interaction_to_shutdown = interaction
                                    return (False, best_threshold)
                        if force_replace:
                            interaction_to_shutdown = valid_interactions_at_priority.add(scored_interaction_data)
                    else:
                        interaction_to_shutdown = valid_interactions_at_priority.maybe_add(scored_interaction_data)
                    self._found_valid_interaction = True
                    if self._gsi_interactions is not None:
                        self._gsi_interactions.append(interaction_result)
            finally:
                if invalidate_interaction:
                    if interaction_to_shutdown is not None:
                        interaction_to_shutdown.invalidate()

            candidate_score = interaction_result.score * AutonomyMode.FULL_AUTONOMY_OPTIMISTIC_SCORE_THRESHOLD
            priority_rank = self.FULL_AUTONOMY_INTERACTION_PRIORITY_RANKING.get(interaction.scoring_priority, 0)
            current_threshold = (priority_rank, candidate_score)
            if best_threshold is None:
                best_threshold = current_threshold
            else:
                best_threshold = max(best_threshold, current_threshold)
        return (
         True, best_threshold)

    def _calculate_stat_op_score_for_running_si(self, si):
        final_op_score = 0
        for stat_op_list in self._applicable_stat_ops_gen(si):
            stat_inst = self._sim.get_tracker(stat_op_list.stat).get_statistic(stat_op_list.stat, False)
            if not stat_inst:
                continue
            commodity_score = stat_op_list.get_fulfillment_rate(si)
            autonomy_scoring_preference = self._get_autonomy_scoring_preference(si)
            motive_score = self._motive_scores.get(stat_op_list.stat, stat_inst.autonomous_desire)
            op_score = commodity_score * autonomy_scoring_preference * motive_score * stat_inst.autonomy_weight
            final_op_score += op_score

        for static_commodity_data in si.affordance.static_commodities_data:
            static_commodity = static_commodity_data.static_commodity
            if not static_commodity.is_scored:
                continue
            if static_commodity not in self._motive_scores:
                continue
            final_op_score += static_commodity.ad_data * static_commodity_data.desire

        return final_op_score

    def _applicable_stat_ops_gen(self, interaction, include_hidden_false_ads=False, gsi_commodity_scores=None):
        for stat_op_list in interaction.affordance.autonomy_ads_gen(target=(interaction.target), include_hidden_false_ads=include_hidden_false_ads):
            if not stat_op_list.stat.add_if_not_in_tracker:
                if stat_op_list.stat not in self._motive_scores:
                    if gsi_commodity_scores is not None:
                        gsi_commodity_scores.append(InteractionCommodityScore(0, (stat_op_list.stat), advertise=False))
                        continue
            if not stat_op_list.is_valid(interaction):
                if gsi_commodity_scores is not None:
                    gsi_commodity_scores.append(InteractionCommodityScore(0, (stat_op_list.stat), advertise=False))
                    continue
                yield stat_op_list

    @staticmethod
    def _get_autonomy_scoring_preference(interaction):
        autonomy_preference = interaction.affordance.autonomy_preference
        if autonomy_preference is not None:
            preference = autonomy_preference.preference
            if preference.is_scoring:
                if interaction.sim.is_object_scoring_preferred(preference.tag, interaction.target):
                    return preference.autonomy_score
        return 1.0

    def _get_all_motives_currently_being_solved(self):
        motive_set = set()
        for si in self._sim.si_state:
            motive_set |= set([stat_op_list.stat for stat_op_list in self._applicable_stat_ops_gen(si)])

        return frozenset(motive_set)

    def _get_motives_to_score(self):
        motives_to_score = frozenset()
        motives_not_yet_scored = []
        stats = self._request.has_commodities or self._request.affordance_list or [stat.stat_type for stat in self._sim.scored_stats_gen()]
        if not stats:
            logger.debug('No scorable stats on Sim: {}', self._request.sim)

        def _get_stat_score(stat_type):
            scored_stat = self._motive_scores.get(stat_type)
            if scored_stat is None:
                scored_stat = ScoredStatistic(stat_type, self._sim)
                self._motive_scores[stat_type] = scored_stat
            return scored_stat

        stats.sort(key=_get_stat_score, reverse=True)
        if not stats:
            return ((), ())
            variance_score = self._motive_scores[stats[0]] * AutonomyMode.FULL_AUTONOMY_STATISTIC_SCORE_VARIANCE
            motives_to_score = frozenset((stat.stat_type for stat in itertools.takewhile(lambda desire: self._motive_scores[desire] >= variance_score, stats)))
            motives_not_yet_scored = stats[len(motives_to_score):]
        else:
            if self._request.has_commodities:
                motives_to_score = frozenset((stat.stat_type for stat in self._request.all_commodities))
        return (
         motives_to_score, motives_not_yet_scored)

    def _calculate_object_stat_use_multiplier(self, game_object, stat_type, fulfillment_rate_is_increasing: bool) -> float:
        if game_object is None:
            return 1
        final_multiplier = 1
        for autonomy_modifier in game_object.autonomy_modifiers:
            if not autonomy_modifier.statistic_multipliers:
                continue
            stat_use_multiplier = autonomy_modifier.statistic_multipliers.get(stat_type)
            if stat_use_multiplier is not None:
                if stat_use_multiplier.apply_direction == StatisticChangeDirection.BOTH or fulfillment_rate_is_increasing and stat_use_multiplier.apply_direction == StatisticChangeDirection.INCREASE or fulfillment_rate_is_increasing or stat_use_multiplier.apply_direction == StatisticChangeDirection.DECREASE:
                    final_multiplier *= stat_use_multiplier.multiplier

        return final_multiplier

    def _score_current_si_state(self, skip_sis=None, gsi_commodity_scores=None) -> float:
        base_score = 0
        for si in self._sim.si_state:
            if skip_sis is not None:
                if si in skip_sis:
                    continue
            base_score += self._calculate_stat_op_score_for_running_si(si)

        attention_cost = self._calculate_attention_cost_for_current_si_state((self._sim), skip_sis=skip_sis)
        normalized_attention_cost = self.FULL_AUTONOMY_ATTENTION_COST.get(attention_cost)
        final_score = base_score * normalized_attention_cost
        return final_score

    def _calculate_attention_cost_for_current_si_state(self, sim, skip_sis=None, attention_cost_scores=None):
        total_attention_cost = 0
        for si in sim.si_state:
            if not si.visible:
                continue
            else:
                if si.is_finishing:
                    continue
                if skip_sis is not None and si in skip_sis:
                    continue
            attention_cost = si.get_attention_cost()
            if attention_cost_scores is not None:
                attention_cost_scores[si] = (
                 attention_cost, sim is self._sim)
            total_attention_cost += attention_cost

        return total_attention_cost

    def _get_debug_incompatability_reason(self, interaction, reason):
        if interaction.context.source != InteractionSource.PIE_MENU:
            if not interactions.si_state.SIState.test_compatibility(interaction, force_concrete=True):
                si_list = ', '.join((str(si) for si in interaction.sim.si_state.all_guaranteed_si_gen()))
                reason = 'Interaction is not compatible with a guaranteed SI: {}'.format(si_list)
        return reason

    @classmethod
    def _test_pending_interactions(cls, sim):
        for interaction in sim.queue:
            if interaction is None:
                logger.error('interaction queue iterator returned None in FullAutonomy::_test_pending_interactions()')
                continue
            if interaction.pipeline_progress >= interactions.PipelineProgress.RUNNING:
                if interaction.disallows_full_autonomy(AutonomyMode._disable_autonomous_multitasking_if_user_directed_override):
                    return TestResult(False, 'None - {} in queue is disallowing autonomous multitasking.', interaction)
                    continue
            if interaction.source == InteractionContext.SOURCE_SOCIAL_ADJUSTMENT or interaction.source == InteractionContext.SOURCE_BODY_CANCEL_AOP or interaction.source == InteractionContext.SOURCE_VEHICLE_CANCEL_AOP or interaction.source == InteractionContext.SOURCE_GET_COMFORTABLE:
                continue
            return TestResult(False, 'None - {} is pending.', interaction)

        for interaction in tuple(sim.si_state):
            if interaction.disallows_full_autonomy(AutonomyMode._disable_autonomous_multitasking_if_user_directed_override):
                return TestResult(False, 'None - {} in si_state is disallowing autonomous multitasking.', interaction)

        return TestResult.TRUE


class PrerollAutonomy(FullAutonomy):

    def _get_potential_interactions(self, obj):
        return (obj.potential_preroll_interactions)((self._request.context), **(self._request).kwargs)


class ObjectResult:

    class Success:
        __slots__ = ('obj', 'relevant_desires')

        def __init__(self, obj, relevant_desires):
            self.obj = obj
            self.relevant_desires = relevant_desires

        def __bool__(self):
            return True

        def __str__(self):
            return 'Not skipped'

        def get_log_data(self):
            return (
             str(self.obj),
             ', '.join([desire.__name__ for desire in self.relevant_desires]),
             'Scored')

    class Failure:
        __slots__ = ('obj', 'relevant_desires', 'reason')

        def __init__(self, obj, relevant_desires, reason):
            self.obj = obj
            self.relevant_desires = relevant_desires
            self.reason = reason

        def __bool__(self):
            return False

        def __str__(self):
            return 'Skipped because {}'.format(self.reason)

        def get_log_data(self):
            return (
             str(self.obj),
             ', '.join([desire.__name__ for desire in self.relevant_desires]),
             self.reason)


class InteractionResult:

    class Success:
        __slots__ = ('interaction', 'relevant_desires', 'score', 'multitask_percentage')

        def __init__(self, interaction, relevant_desires, score, multitask_percentage):
            self.interaction = interaction
            self.relevant_desires = relevant_desires
            self.score = score
            self.multitask_percentage = multitask_percentage

        def __bool__(self):
            return True

        def __str__(self):
            return 'Scored {:f}'.format(self.score)

    class Failure:
        __slots__ = ('interaction', 'stage', 'relevant_desires', '_reason', '_reason_args')

        def __init__(self, interaction, stage, relevant_desires, reason, reason_args=None):
            self.interaction = interaction
            self.stage = stage
            self.relevant_desires = relevant_desires
            self._reason = reason
            self._reason_args = reason_args

        @property
        def reason(self):
            if self._reason_args:
                if self._reason:
                    self._reason = (self._reason.format)(*self._reason_args)
                    self._reason_args = ()
            return self._reason

        def __bool__(self):
            return False

        def __str__(self):
            return 'Skipped because {}'.format(self.reason)


class InteractionScore(float):
    HAS_SHOWN_GSI_OUT_OF_DATE_ERROR = False

    def __new__(cls, score, *args, **kwargs):
        return float.__new__(cls, score)

    def __init__(self, score, interaction, commodity_scores=None, efficiency=None, duration=None, autonomy_scoring_preference=None, rel_utility_score=None, relationship_object_value=None, party_score=None, opportunity_costs=None, must_change_posture=None, base_multitasking_percentage=None, bonus_multitasking_percentage=None, penalty_multitasking_percentage=None, attention_cost_scores=None, attention_cost_bonus_scores=None, attention_cost_penalty_scores=None, outside_multiplier=None, waiting_in_line_multiplier=None, club_rule_multiplier=None, off_lot_object_score_multiplier=None, ensemble_multiplier=None, buff_utility_score=1.0, situation_type_utility_score=1.0, sit_posture_transition_penalty=1.0, estimated_distance=0, route_time=0, tested_relationship_utility_score=1.0, remaining_sis_score=1.0, interaction_score_modifier_multiplier=1.0, minimum_score=0.0):
        self.interaction = interaction
        self.opportunity_costs = opportunity_costs
        self.commodity_scores = commodity_scores
        self.efficiency = None if efficiency is None else float(efficiency)
        self.duration = None if duration is None else float(duration)
        self.autonomy_scoring_preference = None if autonomy_scoring_preference is None else float(autonomy_scoring_preference)
        self.rel_utility_score = None if rel_utility_score is None else float(rel_utility_score)
        self.relationship_object_value = None if relationship_object_value is None else float(relationship_object_value)
        self.party_score = None if party_score is None else float(party_score)
        self.must_change_posture = must_change_posture
        self.base_multitasking_percentage = base_multitasking_percentage
        self.bonus_multitasking_percentage = bonus_multitasking_percentage
        self.penalty_multitasking_percentage = penalty_multitasking_percentage
        self.attention_cost_scores = attention_cost_scores
        self.attention_cost_bonus_scores = attention_cost_bonus_scores
        self.attention_cost_penalty_scores = attention_cost_penalty_scores
        self.outside_multiplier = outside_multiplier
        self.waiting_in_line_multiplier = waiting_in_line_multiplier
        self.club_rule_multiplier = club_rule_multiplier
        self.buff_utility_score = buff_utility_score
        self.tested_relationship_utility_score = tested_relationship_utility_score
        self.situation_type_utility_score = situation_type_utility_score
        self.sit_posture_transition_penalty = sit_posture_transition_penalty
        self.route_time = route_time
        self.estimated_distance = estimated_distance
        self.remaining_sis_score = remaining_sis_score
        self.interaction_score_modifier_multiplier = interaction_score_modifier_multiplier
        self.off_lot_object_score_multiplier = off_lot_object_score_multiplier
        self.ensemble_multiplier = ensemble_multiplier
        if not InteractionScore.HAS_SHOWN_GSI_OUT_OF_DATE_ERROR:
            commodity_scores_sum = 0
            if self.commodity_scores:
                for commodity_score in self.commodity_scores:
                    commodity_scores_sum += commodity_score.score

        else:
            commodity_scores_sum = self.efficiency
        verify_final_score = commodity_scores_sum * outside_multiplier * rel_utility_score * party_score * buff_utility_score * situation_type_utility_score * tested_relationship_utility_score * waiting_in_line_multiplier * interaction_score_modifier_multiplier * (1 + relationship_object_value) * off_lot_object_score_multiplier
        verify_final_score -= sum(self.opportunity_costs.values()) * (AutonomyMode.POSTURE_CHANGE_OPPORTUNITY_COST_MULTIPLIER if self.must_change_posture else 1)
        verify_final_score *= sit_posture_transition_penalty
        verify_final_score += remaining_sis_score
        verify_final_score *= club_rule_multiplier * ensemble_multiplier
        if verify_final_score <= minimum_score:
            verify_final_score = 0
        if not sims4.math.almost_equal(verify_final_score, score):
            gsi_logger.error('Autonomy Scoring was changed in _calculate_interaction_score and GSI wasn\'t updated Please update! For interaction "{}" was expecting score "{}" to be almost equal to calculated "{}"', interaction, score, verify_final_score)
            InteractionScore.HAS_SHOWN_GSI_OUT_OF_DATE_ERROR = True

    @property
    def details(self):
        return self.__str__()

    def __str__(self):
        commodity_scores_sum = 0
        if self.commodity_scores:
            for commodity_score in self.commodity_scores:
                commodity_scores_sum += commodity_score.score

        else:
            commodity_scores_sum = self.efficiency
        commodity_score_str = '\n'.join(map(str, self.commodity_scores))
        opportunity_costs_str = '\n'.join(('        {si.super_affordance.__name__} on {si.target}:\n            Cost: {cost}'.format(si=si, cost=cost) for si, cost in self.opportunity_costs.items())) if self.opportunity_costs else '        None'
        commodity_score_sum = ' + '.join(['({score.modified_desire} * {score.commodity_value} / {score.interval})'.format(score=com_score) for com_score in self.commodity_scores]) if self.commodity_scores else '0'
        efficiency_details = ''
        if self.duration is not None:
            if self.efficiency is not None:
                efficiency_details = ' = {duration} / ({duration} + {route_time})'.format(duration=(self.duration), route_time=(self.route_time))
        change_posture_cost = AutonomyMode.POSTURE_CHANGE_OPPORTUNITY_COST_MULTIPLIER if self.must_change_posture else 1
        change_posture_cost_str = '{} -> {}'.format(self.must_change_posture, change_posture_cost)
        total_opportunity_cost = sum(self.opportunity_costs.values()) * change_posture_cost
        base_multitasking_percentage = str(self.base_multitasking_percentage) if self.base_multitasking_percentage is not None else 'None'
        bonus_multitasking_percentage = str(self.bonus_multitasking_percentage) if self.bonus_multitasking_percentage is not None else 'None'
        penalty_multitasking_percentage = str(self.penalty_multitasking_percentage) if self.penalty_multitasking_percentage is not None else 'None'
        final_multitasking_percentage = str(self.base_multitasking_percentage + self.bonus_multitasking_percentage - self.penalty_multitasking_percentage) if (self.base_multitasking_percentage is not None and self.bonus_multitasking_percentage is not None and self.penalty_multitasking_percentage is not None) else 'None'
        attention_cost_scores_str = '\n'.join(('        {target_prefix}{si.super_affordance.__name__} on {si.target}:\n            Base Attention Cost: {attention}'.format(si=si, attention=(attention_sim_pair[0]), target_prefix=('(target) ' if not attention_sim_pair[1] else '')) for si, attention_sim_pair in self.attention_cost_scores.items())) if self.attention_cost_scores else '            None'
        attention_cost_bonus_scores_str = '\n'.join(('        {stat_type.__name__}:\n            Modified Desire: {modified_desire}\n            Attention Bonus: {attention_bonus}'.format(stat_type=stat_type, modified_desire=(float(attention_score_tuple[0])), attention_bonus=(attention_score_tuple[1])) for stat_type, attention_score_tuple in self.attention_cost_bonus_scores.items())) if self.attention_cost_bonus_scores else '            None'
        attention_cost_penalty_scores_str = '\n'.join(('        {stat_type.__name__}:\n            Modified Desire: {modified_desire}\n            Attention Penalty: {attention_penalty}'.format(stat_type=stat_type, modified_desire=(float(attention_score_tuple[0])), attention_penalty=(attention_score_tuple[1])) for stat_type, attention_score_tuple in self.attention_cost_penalty_scores.items())) if self.attention_cost_penalty_scores else '            None'
        club_rule_multiplier_str = str(self.club_rule_multiplier) if self.club_rule_multiplier is not None else 'None'
        return 'TLDR: Interaction Score {self:.8f}\n\nInteraction {self.interaction.affordance.__name__} on target {self.interaction.target}:\n    Duration: {self.duration}\n    Estimated Distance: {self.estimated_distance}\n    Route Time: {self.route_time} = estimated distance * real_milliseconds_per_sim_second({milliseconds_per_sim_second}) / TICKS_PER_REAL_WORLD_SECOND({ticks_per_real_world_second})\n    Efficiency: {self.efficiency}{efficiency_details} time_overhead /(time_overhead + route_time)\n    Object Preference: {self.autonomy_scoring_preference}\n\n{commodity_score_str}\n\nOutside multiplier:\t\t\t\t{self.outside_multiplier}\nRelationship Score:\t\t\t\t{self.rel_utility_score}\nParty Score:\t\t\t\t\t{self.party_score}\nBuff Utility Multiplier:\t\t\t\t{self.buff_utility_score}\nSituation Type Multiplier:\t\t\t{self.situation_type_utility_score}\nTested Relationship Utility Multiplier:\t{self.tested_relationship_utility_score}\nWaiting In Line Multiplier:\t\t\t{self.waiting_in_line_multiplier}\nInteraction Score Multiplier:\t\t\t{self.interaction_score_modifier_multiplier}\nCrafted Object Relationship Score:\t{self.relationship_object_value}\nOff Lot Object Multiplier:\t\t\t{self.off_lot_object_score_multiplier}\nTotal Opportunity Costs:\t\t\t{total_opportunity_cost}\n{opportunity_costs}\n    Changing Posture Cost: {change_posture_cost}\nSit Posture Transition Penalty:\t\t{self.sit_posture_transition_penalty}\nRemain in SI Score:\t\t\t\t{self.remaining_sis_score}\nClub Rule Multiplier:\t\t\t\t{club_rule_multiplier}\nEnsemble Multiplier:\t\t\t\t{self.ensemble_multiplier}\n\nAttention Cost:\n    Base Cost:\n  {attention_cost_scores}\n    Stat Bonuses:\n  {attention_cost_bonus_scores}\n    Stat Penalties:\n  {attention_cost_penalty_scores}\n    Final Attention Cost:\n        final multitasking percentage = base + bonus - penalty\n        {final_multitasking_percentage} = {base_multitasking_percentage} + {bonus_multitasking_percentage} - {penalty_multitasking_percentage}\n\nInteraction Score Equation : \nscore = (Commodities | Efficiency if no commodities) * Outside Multiplier * Relationship Multiplier * Party Multiplier * Buff Utility Multiplier * Situation Type Multiplier * Tested Relationship Utility Multiplier * Waiting In Line Multiplier * Interaction Score Modifier * Crafting Object Relationship Multiplier * Off Lot Object Multiplier\nscore -= Total Opportunity Cost\nscore *= Sit Posture Transition Penalty Multiplier\nscore += Remain in SI Score\nscore *= Club Rule Multiplier * Ensemble Multiplier\n\n{self:.8f} = ((({commodity_scores_sum} * {self.outside_multiplier} * {self.rel_utility_score} * {self.party_score} * {self.buff_utility_score} * {self.situation_type_utility_score} * {self.tested_relationship_utility_score} * {self.waiting_in_line_multiplier} * {self.interaction_score_modifier_multiplier} * (1 + {self.relationship_object_value}) * {self.off_lot_object_score_multiplier}) - {total_opportunity_cost} * {self.sit_posture_transition_penalty}) + {self.remaining_sis_score}) * {self.club_rule_multiplier} * {self.ensemble_multiplier}\n\nInteraction Score: {self:.8f}\nFinal MultiTasking Percentage : {final_multitasking_percentage}'.format(self=self,
          milliseconds_per_sim_second=(date_and_time.REAL_MILLISECONDS_PER_SIM_SECOND),
          ticks_per_real_world_second=(date_and_time.TICKS_PER_REAL_WORLD_SECOND),
          efficiency_details=efficiency_details,
          commodity_score_str=commodity_score_str,
          opportunity_costs=opportunity_costs_str,
          change_posture_cost=change_posture_cost_str,
          total_opportunity_cost=total_opportunity_cost,
          commodity_score_sum=commodity_score_sum,
          base_multitasking_percentage=base_multitasking_percentage,
          bonus_multitasking_percentage=bonus_multitasking_percentage,
          penalty_multitasking_percentage=penalty_multitasking_percentage,
          final_multitasking_percentage=final_multitasking_percentage,
          attention_cost_scores=attention_cost_scores_str,
          attention_cost_bonus_scores=attention_cost_bonus_scores_str,
          attention_cost_penalty_scores=attention_cost_penalty_scores_str,
          club_rule_multiplier=club_rule_multiplier_str,
          commodity_scores_sum=commodity_scores_sum)


class InteractionCommodityScore:
    __slots__ = ('score', 'commodity', 'advertise', 'commodity_value', 'interval',
                 'fulfillment_rate', 'object_stat_use_multiplier', 'already_solving_motive_multiplier',
                 'modified_desire')

    def __init__(self, score, commodity, advertise: bool, commodity_value=None, interval=None, fulfillment_rate=None, object_stat_use_multiplier=None, already_solving_motive_multiplier=None, modified_desire=None):
        self.score = score
        self.commodity = commodity
        self.advertise = advertise
        self.commodity_value = None if commodity_value is None else float(commodity_value)
        self.interval = None if interval is None else float(interval)
        self.fulfillment_rate = None if fulfillment_rate is None else float(fulfillment_rate)
        self.object_stat_use_multiplier = object_stat_use_multiplier
        self.already_solving_motive_multiplier = None if already_solving_motive_multiplier is None else float(already_solving_motive_multiplier)
        self.modified_desire = None if modified_desire is None else float(modified_desire)

    def __str__(self):
        if self.advertise:
            stat_name = 'No Commodity' if self.commodity is None else self.commodity.__name__
            return '    Commodity: {stat_name}\n        Commodity Value : {self.commodity_value}\n        Interval        : {self.interval}\n        Fulfillment Rate: {self.fulfillment_rate} = {self.commodity_value} / {self.interval}\n        Object Stat Use : {self.object_stat_use_multiplier}\n        Already Solving : {self.already_solving_motive_multiplier}\n        Desire Weight   : {self.autonomy_weight}\n        Modified Desire : {self.modified_desire}\n        Score           : {score} = {self.fulfillment_rate} * {self.object_stat_use_multiplier} * {self.already_solving_motive_multiplier} * {self.modified_desire} * {self.autonomy_weight}'.format(self=self,
              score=(float(self.score)),
              stat_name=stat_name)
        return '    Commodity: {self.commodity}\n        Not advertising'.format(self=self)

    @property
    def details(self):
        return self.__str__()

    @property
    def autonomy_weight(self):
        if self.commodity is not None:
            return self.commodity.autonomy_weight
        return 1


class ScoredStatistic(float):
    __slots__ = ('_stat_type', 'autonomous_desire', 'stat_value', 'score_multiplier')

    def __new__(cls, stat, sim):
        scored_value = stat.autonomous_desire * sim.get_score_multiplier(stat.stat_type)
        return float.__new__(cls, scored_value)

    def __init__(self, stat, sim):
        self._stat_type = stat.stat_type
        self.autonomous_desire = stat.autonomous_desire
        self.score_multiplier = sim.get_score_multiplier(self.stat_type)
        self.stat_value = stat.get_value()

    def __repr__(self):
        return '{self.stat_type} ({self.score})'.format(self=self)

    def __str__(self):
        weighted_score = float(self) * self.autonomy_weight
        return '    Commodity: {self._stat_type}\n        Score            : {score}\n        Weighted Score   : {weighted_score}\n        Value            : {self.stat_value}\n        Autonomous Desire: {self.autonomous_desire}\n        Multiplier       : {self.score_multiplier}        Autonomy Weight  : {self.autonomy_weight}'.format(self=self,
          score=(float(self)),
          weighted_score=weighted_score)

    @property
    def details(self):
        return self.__str__()

    @property
    def stat_type(self):
        return self._stat_type

    @property
    def score(self):
        return float(self)

    @property
    def autonomy_weight(self):
        return self._stat_type.autonomy_weight