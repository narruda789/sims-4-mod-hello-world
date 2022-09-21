# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\body_type_level\body_type_level_commands.py
# Compiled at: 2022-07-21 21:49:30
# Size of source mod 2**32: 487 bytes
import services, sims4
from sims4.common import Pack

@sims4.commands.Command('body_type_level.set_acne_enabled', pack=(Pack.EP12), command_type=(sims4.commands.CommandType.Live))
def set_acne_enabled(enabled: bool=True, _connection=None):
    services.sim_info_manager().set_acne_enabled(enabled)
    return True