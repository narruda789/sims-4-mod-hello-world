# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\objects\electronics\pick_channel.py
# Compiled at: 2015-03-12 16:02:52
# Size of source mod 2**32: 3458 bytes
from event_testing.results import TestResult
from interactions.base.picker_interaction import AutonomousPickerSuperInteraction
from interactions.base.picker_strategy import StatePickerEnumerationStrategy
from interactions.base.super_interaction import SuperInteraction
from objects.components.state import TunableStateTypeReference
from sims4.tuning.instances import lock_instance_tunables
from sims4.tuning.tunable import Tunable
import sims4.log
logger = sims4.log.Logger('PickChannel')

class PickChannelAutonomouslySuperInteraction(AutonomousPickerSuperInteraction):
    INSTANCE_TUNABLES = {'state':TunableStateTypeReference(description='\n            The state used in the interaction.\n            '), 
     'push_additional_affordances':Tunable(description="\n            Whether to push affordances specified by the channel. This is used\n            for stereo's turn on and listen to... interaction.\n            ",
       tunable_type=bool,
       default=True)}

    def __init__(self, *args, **kwargs):
        (super().__init__)(args, choice_enumeration_strategy=StatePickerEnumerationStrategy(), **kwargs)

    @classmethod
    def _test(cls, target, context, **kwargs):
        test_result = (super()._test)(target, context, **kwargs)
        if not test_result:
            return test_result
        else:
            return StatePickerEnumerationStrategy.has_valid_choice(target, context, state=(cls.state)) or TestResult(False, 'No valid choice in State Picker Enumeration Strategy.')
        return TestResult.TRUE

    def _run_interaction_gen(self, timeline):
        self._choice_enumeration_strategy.build_choice_list(self, self.state)
        chosen_state = self._choice_enumeration_strategy.find_best_choice(self)
        if chosen_state is None:
            logger.error('{} fail to find a valid chosen state value for state {}'.format(self.__class__.__name__, self.state))
            return False
        chosen_state.activate_channel(interaction=self, push_affordances=(self.push_additional_affordances))
        return True
        if False:
            yield None


class WatchCurrentChannelAutonomouslySuperInteraction(SuperInteraction):
    INSTANCE_TUNABLES = {'state': TunableStateTypeReference(description='\n            The state to use to determine what to autonomously watch.\n            ')}

    def _run_interaction_gen(self, timeline):
        current_state = self.target.get_state(self.state)
        current_state.activate_channel(interaction=self, push_affordances=True)
        return True
        if False:
            yield None


lock_instance_tunables(AutonomousPickerSuperInteraction, allow_user_directed=False,
  basic_reserve_object=None,
  disable_transitions=True)