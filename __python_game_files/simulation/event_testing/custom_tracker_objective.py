# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\event_testing\custom_tracker_objective.py
# Compiled at: 2019-12-05 17:29:57
# Size of source mod 2**32: 4276 bytes
from event_testing.objective_tuning import BaseObjective
from sims4.tuning.instances import HashedTunedInstanceMetaclass
from sims4.tuning.tunable import HasTunableSingletonFactory, AutoFactoryInit, TunableReference, TunableVariant, Tunable, TunableThreshold, HasTunableFactory
import services, sims4.resources

class TrackCommodity(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'commodity_to_track':TunableReference(description='\n            The commodity that we want to track on the Sim.\n            ',
       manager=services.get_instance_manager(sims4.resources.Types.STATISTIC),
       class_restrictions=('Commodity', )), 
     'threshold':TunableThreshold(description='\n            The threshold that we are trying to reach.\n            ')}

    def __init__(self, event_data_tracker, milestone, objective, **kwargs):
        (super().__init__)(**kwargs)
        self._event_data_tracker = event_data_tracker
        self._owning_milestone = milestone
        self._owning_objective = objective
        self._commodity_tracker_handle = None

    def on_threshold_reached(self, stat_type):
        self._event_data_tracker.tracker_complete(self._owning_milestone, self._owning_objective)

    def setup(self):
        sim_info = self._event_data_tracker.owner_sim_info
        if sim_info is None:
            return False
        if self._commodity_tracker_handle is not None:
            self._commodity_tracker_handle = sim_info.commodity_tracker.create_and_add_listener(self.commodity_to_track, self.threshold, self.on_threshold_reached)
        return True

    def clear(self):
        if self._commodity_tracker_handle is not None:
            sim_info = self._event_data_tracker.owner_sim_info
            sim_info.commodity_tracker.remove_listener(self._commodity_tracker_handle)
        self._commodity_tracker_handle = None
        self._event_data_tracker = None
        self._owning_milestone = None
        self._owning_objective = None


class CustomTrackerObjective(BaseObjective, metaclass=HashedTunedInstanceMetaclass, manager=services.get_instance_manager(sims4.resources.Types.OBJECTIVE)):
    INSTANCE_TUNABLES = {'tracking': TunableVariant(description='\n            The method of tracking that we want to use.\n            ',
                   commodity=(TrackCommodity.TunableFactory()),
                   default='commodity')}

    @classmethod
    def setup_objective(cls, event_data_tracker, milestone):
        tracker = cls.tracking(event_data_tracker, milestone, cls)
        event_data_tracker.add_event_tracker(cls, tracker)

    @classmethod
    def cleanup_objective(cls, event_data_tracker, milestone):
        event_data_tracker.remove_event_tracker(cls)

    @classmethod
    def goal_value(cls):
        return 1