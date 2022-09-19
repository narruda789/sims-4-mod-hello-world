# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\relationships\relationship_track_tracker.py
# Compiled at: 2020-10-02 23:31:53
# Size of source mod 2**32: 11335 bytes
import itertools
from collections import defaultdict
from event_testing.resolver import DoubleSimResolver
from relationships.global_relationship_tuning import RelationshipGlobalTuning
from relationships.object_relationship_track_tracker import RelationshipTrackTrackerMixin
from relationships.relationship_enums import RelationshipDirection
from relationships.relationship_track import ObjectRelationshipTrack
from relationships.tunable import RelationshipTrackData2dLink
from singletons import DEFAULT
from statistics.base_statistic_tracker import BaseStatisticTracker
import services, sims4.log
logger = sims4.log.Logger('Relationship', default_owner='msantander')

class RelationshipTrackTracker(BaseStatisticTracker, RelationshipTrackTrackerMixin):
    __slots__ = ('_rel_data', 'load_in_progress', '_longterm_tracks_locked', '_can_add_reltrack',
                 '_bit_based_decay_modifiers')

    def __init__(self, rel_data):
        super().__init__()
        self._rel_data = rel_data
        self.load_in_progress = False
        self._longterm_tracks_locked = False
        self._can_add_reltrack = True
        self._bit_based_decay_modifiers = None

    def on_sim_creation(self, sim):
        pass

    def add_statistic(self, stat_type, owner=None, **kwargs):
        if not self._can_add_reltrack:
            return
            if self.is_track_locked(stat_type):
                return
        else:
            if stat_type.species_requirements is not None:
                sim_info_a = services.sim_info_manager().get(self.rel_data.sim_id_a)
                sim_info_b = services.sim_info_manager().get(self.rel_data.sim_id_b)
                if sim_info_a is not None:
                    if sim_info_b is not None:
                        sim_a_species = sim_info_a.species
                        sim_b_species = sim_info_b.species
                        species_list_one = stat_type.species_requirements.species_list_one
                        species_list_two = stat_type.species_requirements.species_list_two
                        if sim_a_species not in species_list_one or sim_b_species not in species_list_two:
                            if not sim_b_species not in species_list_one:
                                if sim_a_species not in species_list_two:
                                    return
                        if not sim_info_a.trait_tracker.hide_relationships:
                            if sim_info_b.trait_tracker.hide_relationships:
                                return
            relationship_track = (super().add_statistic)(stat_type, owner=owner, **kwargs)
            if relationship_track is None:
                return
            relationship_service = services.relationship_service()
            for relationship_multipliers in itertools.chain(relationship_service.get_relationship_multipliers_for_sim(self._rel_data.sim_id_a), relationship_service.get_relationship_multipliers_for_sim(self._rel_data.sim_id_b)):
                for rel_track, multiplier in relationship_multipliers.items():
                    if rel_track is stat_type:
                        relationship_track.add_statistic_multiplier(multiplier)

            if self._bit_based_decay_modifiers is not None:
                for bit, track_modifiers in self._bit_based_decay_modifiers.items():
                    for track, modifiers in track_modifiers.items():
                        for sim_id, modifier in modifiers:
                            if not self.rel_data.relationship.has_bit(sim_id, bit):
                                continue
                            relationship_track.add_decay_rate_modifier(modifier)

            if not self.load_in_progress:
                if relationship_track.tested_initial_modifier is not None:
                    sim_info_a = services.sim_info_manager().get(self.rel_data.sim_id_a)
                    sim_info_b = services.sim_info_manager().get(self.rel_data.sim_id_b)
                    if sim_info_a is None or sim_info_b is None:
                        return relationship_track
                    modified_amount = relationship_track.tested_initial_modifier.get_max_modifier(DoubleSimResolver(sim_info_a, sim_info_b))
                    relationship_track.add_value(modified_amount)
        return relationship_track

    @property
    def can_add_reltrack(self):
        return self._can_add_reltrack

    @can_add_reltrack.setter
    def can_add_reltrack(self, can_add):
        self._can_add_reltrack = can_add

    def set_value(self, stat_type, value, apply_initial_modifier=False, **kwargs):
        modified_amount = 0.0
        if apply_initial_modifier:
            if stat_type.tested_initial_modifier is not None:
                sim_info_a = services.sim_info_manager().get(self.rel_data.sim_id_a)
                sim_info_b = services.sim_info_manager().get(self.rel_data.sim_id_b)
                if sim_info_a is not None:
                    if sim_info_b is not None:
                        modified_amount = stat_type.tested_initial_modifier.get_max_modifier(DoubleSimResolver(sim_info_a, sim_info_b))
        (super().set_value)(stat_type, (value + modified_amount), **kwargs)

    def should_suppress_calculations(self):
        return self.load_in_progress

    def get_statistic(self, stat_type, add=False):
        if stat_type is DEFAULT:
            stat_type = RelationshipGlobalTuning.REL_INSPECTOR_TRACK
        if stat_type is None:
            logger.error('stat_type is None in RelationshipTrackTracker.get_statistic()', owner='jjacobson')
            return
        return super().get_statistic(stat_type, add)

    def trigger_test_event(self, sim_info, event):
        if sim_info is None:
            return
        services.get_event_manager().process_event(event, sim_info=sim_info,
          sim_id=(sim_info.sim_id),
          target_sim_id=(self._rel_data.relationship.find_other_sim_id(sim_info.sim_id)))

    def add_bit_based_decay_modifier(self, track, bit, sim_id, modifier):
        if self._bit_based_decay_modifiers is None:
            self._bit_based_decay_modifiers = defaultdict(lambda : defaultdict(list))
        else:
            self._bit_based_decay_modifiers[bit][track].append((sim_id, modifier))
            return self.rel_data.relationship.has_bit(sim_id, bit) or None
        track = self.get_statistic(track)
        if track is None:
            return
        track.add_decay_rate_modifier(modifier)

    def on_relationship_bit_added(self, bit, sim_id):
        if self._bit_based_decay_modifiers is None:
            return
        if bit in self._bit_based_decay_modifiers:
            for track, modifiers in self._bit_based_decay_modifiers[bit].items():
                track = self.get_statistic(track)
                if track is None:
                    continue
                for modifier_sim_id, modifier in modifiers:
                    if bit.directionality == RelationshipDirection.UNIDIRECTIONAL:
                        if modifier_sim_id != sim_id:
                            continue
                    track.add_decay_rate_modifier(modifier)

    def remove_relationship_bit_decay_modifier(self, track, bit, sim_id, modifier):
        if self._bit_based_decay_modifiers is not None:
            self._bit_based_decay_modifiers[bit][track].remove((sim_id, modifier))
            if not self._bit_based_decay_modifiers[bit][track]:
                del self._bit_based_decay_modifiers[bit][track]
                if not self._bit_based_decay_modifiers[bit]:
                    del self._bit_based_decay_modifiers[bit]
                if not self._bit_based_decay_modifiers:
                    self._bit_based_decay_modifiers = None
        else:
            return self.rel_data.relationship.has_bit(sim_id, bit) or None
        track = self.get_statistic(track)
        if track is None:
            return
        track.remove_decay_rate_modifier(modifier)

    def on_relationship_bit_removed(self, bit, sim_id):
        if self._bit_based_decay_modifiers is None:
            return
        if bit not in self._bit_based_decay_modifiers:
            return
        for track, modifiers in self._bit_based_decay_modifiers[bit].items():
            track = self.get_statistic(track)
            if track is None:
                continue
            for modifier_sim_id, modifier in modifiers:
                if bit.directionality == RelationshipDirection.UNIDIRECTIONAL:
                    if modifier_sim_id != sim_id:
                        continue
                track.remove_decay_rate_modifier(modifier)