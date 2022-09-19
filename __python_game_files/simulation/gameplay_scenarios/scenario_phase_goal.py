# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gameplay_scenarios\scenario_phase_goal.py
# Compiled at: 2022-08-26 18:13:12
# Size of source mod 2**32: 6321 bytes
import services, sims4
from filters.tunable import TunableSimFilter
from interactions.utils.loot import LootActions
from interactions.utils.tunable_icon import TunableIcon
from sims4.tuning.tunable import TunableTuple, TunableEnumEntry, Tunable, HasTunableFactory, AutoFactoryInit, TunableReference, TunableList
from sims4.tuning.tunable_base import GroupNames, ExportModes

class ScenarioPhaseGoal(HasTunableFactory, AutoFactoryInit):
    FACTORY_TUNABLES = {'goal': TunableTuple(description='\n            Data containing the SituationGoal and any additional data about that goal specific to the scenario.\n            ',
               situation_goal=TunableReference(description='\n                A SituationGoal.\n                ',
               manager=(services.get_instance_manager(sims4.resources.Types.SITUATION_GOAL)),
               export_modes=(ExportModes.ServerXML)),
               outcome_header_icon=TunableIcon(description='\n                The icon that sits next to the header text for each goal\n                in the ScenarioLivePanel.\n                ',
               export_modes=(ExportModes.ServerXML),
               allow_none=True,
               tuning_group=(GroupNames.UI)),
               required_pack=TunableEnumEntry(description='\n                The pack that the goal may require.\n                ',
               tunable_type=(sims4.common.Pack),
               default=(sims4.common.Pack.BASE_GAME)),
               mandatory=Tunable(description='\n                If checked, the goal must be completed in order to complete the phase.\n                ',
               tunable_type=bool,
               default=True,
               export_modes=(ExportModes.ServerXML)),
               hidden=Tunable(description='\n                If checked, this goal will not appear until it has been completed. The\n                goal must still be marked as visible to appear once it has been completed.\n                ',
               tunable_type=bool,
               default=False,
               export_modes=(ExportModes.ServerXML)),
               goal_loot=TunableList(description='\n                A list of loots to apply as a scenario outcome.\n                ',
               tunable=TunableTuple(description='\n                A collection of loot actions. Use loot_with_scenario_role for actions requiring actor as subject.\n                    ',
               scenario_loot=TunableTuple(description='\n                        A loot action and a list of targets.              \n                        ',
               loot_action=LootActions.TunableReference(description='\n                            An action that will be applied to everyone in the list of targets.\n                            ',
               pack_safe=True),
               actor_role=TunableReference(description='\n                            The role of main targets for the loot.\n                            Leave this empty when loot subject is something other than Actor.\n                            Loot will be applied to every sim in the scenario with specified role.\n                            Useful for applying loot to the household as a whole by applying it to a role that only one sim \n                            in the household has.\n                            ',
               manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
               class_restrictions=('ScenarioRole', ),
               allow_none=True),
               secondary_actor_role=TunableReference(description='\n                            The role of secondary targets for the loot.\n                            Fill secondary target only for loots requiring pair of sims. Like relationship loots.\n                            Loot will be applied between every pair of sims in the scenario with (actor_role, secondary_actor_role)\n                            ',
               manager=(services.get_instance_manager(sims4.resources.Types.SNIPPET)),
               class_restrictions=('ScenarioRole', ),
               allow_none=True),
               actor_sim_filter=TunableReference(description='\n                            An alternative way(to actor_role) to access sim_info for the tests requiring "Actor". \n                            This will not create a new sim like in situations. \n                            It is just a reference for the sim filter in the scenario_npc_sims.           \n                            ',
               manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
               class_restrictions=TunableSimFilter,
               tuning_group=(GroupNames.SIM_FILTER),
               allow_none=True),
               secondary_actor_sim_filter=TunableReference(description='\n                            An alternative way(to secondary_actor_role) to access sim_info for the loots requiring "Actor". \n                            This will not create a new sim like in situations. \n                            It is just a reference for the sim filter in the scenario_npc_sims.           \n                            ',
               manager=(services.get_instance_manager(sims4.resources.Types.SIM_FILTER)),
               class_restrictions=TunableSimFilter,
               tuning_group=(GroupNames.SIM_FILTER),
               allow_none=True),
               export_class_name='LootWithScenarioRole'),
               export_class_name='ScenarioPhaseGoalLoot')),
               export_class_name='TunableScenarioPhaseGoalData')}