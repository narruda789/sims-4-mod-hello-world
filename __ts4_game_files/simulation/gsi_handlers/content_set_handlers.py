# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\gsi_handlers\content_set_handlers.py
# Compiled at: 2017-07-14 18:33:22
# Size of source mod 2**32: 2365 bytes
from gsi_handlers.gameplay_archiver import GameplayArchiver
from sims4.gsi.schema import GsiGridSchema, GsiFieldVisualizers
content_set_archive_schema = GsiGridSchema(label='Content Set Generation', sim_specific=True)
content_set_archive_schema.add_field('sim', label='Sim', width=2)
content_set_archive_schema.add_field('super_interaction', label='Super Interaction', width=2)
content_set_archive_schema.add_field('considered_count', label='Considered', type=(GsiFieldVisualizers.INT), width=1)
content_set_archive_schema.add_field('result_count', label='Results', width=1)
content_set_archive_schema.add_field('topics', label='Topics', width=1)
with content_set_archive_schema.add_has_many('Considered', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('selected', label='Selected', width=1)
    sub_schema.add_field('eligible', label='Eligible', width=2)
    sub_schema.add_field('affordance', label='Affordance', width=3)
    sub_schema.add_field('target', label='Target', width=3)
    sub_schema.add_field('test', label='Test Result', width=2)
    sub_schema.add_field('total_score', label='Total Score', type=(GsiFieldVisualizers.INT), width=1)
with content_set_archive_schema.add_has_many('Results', GsiGridSchema) as (sub_schema):
    sub_schema.add_field('result_affordance', label='Affordance', width=3)
    sub_schema.add_field('result_target', label='Target', width=3)
    sub_schema.add_field('result_loc_key', label='Localization Key', width=3)
    sub_schema.add_field('result_target_loc_key', label='Target Loc Key', width=3)
archiver = GameplayArchiver('content_set', content_set_archive_schema, add_to_archive_enable_functions=True)

def archive_content_set(sim, si, considered, results, topics):
    entry = {}
    entry['sim'] = str(sim)
    entry['super_interaction'] = str(si)
    entry['considered_count'] = len(considered)
    entry['result_count'] = len(results)
    entry['topics'] = ', '.join((str(topic) for topic in topics))
    entry['Considered'] = list(considered.values())
    entry['Results'] = list(results.values())
    archiver.archive(data=entry, object_id=(sim.id))