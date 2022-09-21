# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\sims\change_sim_name_interaction.py
# Compiled at: 2021-02-02 20:26:49
# Size of source mod 2**32: 2012 bytes
from event_testing.resolver import DoubleSimResolver
from interactions.base.immediate_interaction import ImmediateSuperInteraction
from sims4.localization import LocalizationHelperTuning
from ui.ui_dialog_generic import UiDialogTextInputOkCancel
TEXT_INPUT_FIRSTNAME = 'first_name'
TEXT_INPUT_LASTNAME = 'last_name'

class ChangeSimNameInteraction(ImmediateSuperInteraction):
    INSTANCE_TUNABLES = {'rename_dialog': UiDialogTextInputOkCancel.TunableFactory(description='\n            The dialog to select a new Name for the Sim.\n            ',
                        text_inputs=(
                       TEXT_INPUT_FIRSTNAME, TEXT_INPUT_LASTNAME))}

    def _run_interaction_gen(self, timeline):
        target_sim = self.target
        if not target_sim.is_sim:
            return True
        target_sim_info = target_sim.sim_info

        def on_response(dialog_response):
            if not dialog_response.accepted:
                return
            first_name = dialog_response.text_input_responses.get(TEXT_INPUT_FIRSTNAME)
            last_name = dialog_response.text_input_responses.get(TEXT_INPUT_LASTNAME)
            target_sim_info.first_name = first_name
            target_sim_info.last_name = last_name

        text_input_overrides = {TEXT_INPUT_FIRSTNAME: lambda *_, **__: LocalizationHelperTuning.get_raw_text(target_sim_info.first_name), 
         TEXT_INPUT_LASTNAME: lambda *_, **__: LocalizationHelperTuning.get_raw_text(target_sim_info.last_name)}
        dialog = self.rename_dialog(target_sim_info, DoubleSimResolver(self.sim.sim_info, target_sim_info))
        dialog.show_dialog(on_response=on_response, text_input_overrides=text_input_overrides)
        return True
        if False:
            yield None