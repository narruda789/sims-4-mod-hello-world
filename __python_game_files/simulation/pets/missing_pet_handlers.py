# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\pets\missing_pet_handlers.py
# Compiled at: 2017-10-03 18:04:54
# Size of source mod 2**32: 1745 bytes
from sims4.gsi.dispatcher import GsiHandler
from sims4.gsi.schema import GsiGridSchema
import services
missing_pet_schema = GsiGridSchema(label='Missing Pets')
missing_pet_schema.add_field('household_id', label='Household Id')
missing_pet_schema.add_field('household', label='Household')
missing_pet_schema.add_field('run_test_absolute', label='Run Tests - Absolute Time')
missing_pet_schema.add_field('run_test_time_left', label='Run Tests - Time Left')
missing_pet_schema.add_field('sim_id', label='Sim Id')
missing_pet_schema.add_field('sim', label='Sim')
missing_pet_schema.add_field('return_time_absolute', label='Return Time - Absolute Time')
missing_pet_schema.add_field('return_time_left', label='Return Time - Time Left')
missing_pet_schema.add_field('cooldown_absolute', label='Cooldown - Absolute Time')
missing_pet_schema.add_field('cooldown_time_left', label='Cooldown - Time Left')
with missing_pet_schema.add_view_cheat('pets.return_pet', label='Return Pet') as (return_pet_cheat):
    return_pet_cheat.add_token_param('household_id')
with missing_pet_schema.add_view_cheat('pets.post_alert', label='Post Alert') as (post_alert_cheat):
    post_alert_cheat.add_token_param('household_id')

@GsiHandler('missing_pets_schema_view', missing_pet_schema)
def generate_missing_pet_view():
    missing_pet_data = []
    for household in services.household_manager().values():
        gsi_data = household.missing_pet_tracker.get_missing_pet_data_for_gsi()
        missing_pet_data.append(gsi_data)

    return missing_pet_data