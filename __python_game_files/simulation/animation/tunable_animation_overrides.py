# uncompyle6 version 3.7.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.9 (tags/v3.7.9:13c94747c7, Aug 17 2020, 18:58:18) [MSC v.1900 64 bit (AMD64)]
# Embedded file name: T:\InGame\Gameplay\Scripts\Server\animation\tunable_animation_overrides.py
# Compiled at: 2022-06-13 18:18:17
# Size of source mod 2**32: 24210 bytes
import services, sims4.resources
from animation.animation_constants import InteractionAsmType
from animation.animation_overrides_tuning import TunableRequiredSlotOverride, TunablePostureManifestOverrideValue, TunablePostureManifestOverrideKey, TunableParameterMapping
from animation.animation_utils import AnimationOverrides
from balloon.tunable_balloon import TunableBalloon
from event_testing.tests import TunableTestSet
from interactions import ParticipantTypeReactionlet
from interactions.utils.animation_selector import TunableAnimationSelector
from objects.props.prop_share_override import PropShareOverride
from sims4.tuning.tunable import TunableFactory, OptionalTunable, Tunable, TunableList, TunableTuple, TunableReference, TunableMapping, TunableResourceKey
from sims4.tuning.tunable_base import SourceQueries, SourceSubQueries
from sims4.tuning.tunable_hash import TunableStringHash32
from singletons import DEFAULT, UNSET
from tag import TunableTag
from tunable_utils.tunable_offset import TunableOffset
import sims4.log
logger = sims4.log.Logger('Tunable Animation Overrides')

class TunableAnimationOverrides(TunableFactory):

    @staticmethod
    def verify_tunable_callback(instance_class, tunable_name, source, *, props, **kwargs):
        for key, value in props.items():
            if value.alternative_prop_definitions is None:
                continue
            if value.alternative_prop_definitions.favorite_object_in_inventory and value.alternative_prop_definitions.favorite_object_by_definition:
                logger.error('Only one alternative prop definition can be set at a time in {}', props)

    @staticmethod
    def _factory(*args, manifests, **kwargs):
        if manifests is not None:
            key_name = 'key'
            value_name = 'value'
            manifests_dict = {}
            for item in manifests:
                key = getattr(item, key_name)
                if key in manifests_dict:
                    import sims4.tuning.tunable
                    sims4.tuning.tunable.logger.error('Multiple values specified for {} in manifests in an animation overrides block.', key)
                else:
                    manifests_dict[key] = getattr(item, value_name)

        else:
            manifests_dict = None
        return AnimationOverrides(args, manifests=manifests_dict, **kwargs)

    FACTORY_TYPE = _factory

    def __init__(self, asm_source=None, state_source=None, allow_reactionlets=True, override_animation_context=False, participant_enum_override=DEFAULT, description='Overrides to apply to the animation request.', **kwargs):
        if asm_source is not None:
            asm_source = '../../../' + asm_source
            clip_actor_asm_source = asm_source
            vfx_sub_query = SourceSubQueries.ClipEffectName
            sound_sub_query = SourceSubQueries.ClipSoundName
            if state_source is not None:
                last_slash_index = clip_actor_asm_source.rfind('/')
                clip_actor_state_source = clip_actor_asm_source[:last_slash_index + 1] + state_source
                clip_actor_state_source = '../' + clip_actor_state_source
                clip_actor_state_source = SourceQueries.ASMClip.format(clip_actor_state_source)
        else:
            clip_actor_asm_source = None
            clip_actor_state_source = None
            vfx_sub_query = None
            sound_sub_query = None
        if participant_enum_override is DEFAULT:
            participant_enum_override = (
             ParticipantTypeReactionlet, ParticipantTypeReactionlet.Invalid)
        if allow_reactionlets:
            kwargs['reactionlet'] = OptionalTunable(TunableAnimationSelector(description='\n                Reactionlets are short, one-shot animations that are triggered \n                via x-event.\n                X-events are markers in clips that can trigger an in-game \n                effect that is timed perfectly with the clip. Ex: This is how \n                we trigger laughter at the exact moment of the punchline of a \n                Joke\n                It is EXTREMELY important that only content authored and \n                configured by animators to be used as a Reactionlet gets \n                hooked up as Reactionlet content. If this rule is violated, \n                crazy things will happen including the client and server losing \n                time sync. \n                ',
              interaction_asm_type=(InteractionAsmType.Reactionlet),
              override_animation_context=True,
              participant_enum_override=participant_enum_override))
        (super().__init__)(params=TunableParameterMapping(description='\n                This tuning is used for overriding parameters on the ASM to \n                specific values.\n                These will take precedence over those same settings coming from \n                runtime so be careful!\n                You can enter a number of overrides as key/value pairs:\n                Name is the name of the parameter as it appears in the ASM.\n                Value is the value to set on the ASM.\n                Make sure to get the type right. Parameters are either \n                booleans, enums, or strings.\n                Ex: The most common usage of this field is when tuning the \n                custom parameters on specific objects, such as the objectName \n                parameter. \n                '), 
         vfx=TunableMapping(description="\n                VFX overrides for this animation. The key is the effect's actor\n                name. Please note, this is not the name of the vfx that would\n                normally play. This is the name of the actor in the ASM that is\n                associated to a specific effect.\n                ",
  key_name='original_effect',
  value_name='replacement_effect',
  value_type=TunableTuple(description='\n                    Override data for the specified effect actor.\n                    ',
  effect=OptionalTunable(description='\n                        Override the actual effect that is meant to be played.\n                        It can be left None to stop the effect from playing\n                        ',
  disabled_name='no_effect',
  enabled_name='play_effect',
  tunable=Tunable(tunable_type=str,
  default='')),
  mirrored_effect=OptionalTunable(description="\n                        If enabled and the is_mirrored parameter comes through\n                        as True, we will play this effect instead of the tuned\n                        override. NOTE: if you tune this, the non-mirrored\n                        version must also be tuned in the regular effect\n                        override for it to play. For example, the Bubble Bottle\n                        needs to play mirrored effects for left handed Sims,\n                        but if we don't override the effect and still want to\n                        play a mirrored version, we need to specify the\n                        original effect so we don't play nothing.\n                        ",
  tunable=Tunable(description='\n                            The name of the mirrored effect.\n                            ',
  tunable_type=str,
  default='')),
  effect_joint=OptionalTunable(description='\n                        Overrides the effect joint of the VFX.  Use this\n                        specify a different joint name to attach the effect to.\n                        ',
  disabled_name='no_override',
  enabled_name='override_joint',
  tunable=(TunableStringHash32())),
  target_joint=OptionalTunable(description='\n                        Overrides the target joint of the VFX.  This is used in\n                        case of attractors where we want the effect to target a\n                        different place per object on the same animation\n                        ',
  disabled_name='no_override',
  enabled_name='override_joint',
  tunable=(TunableStringHash32())),
  target_joint_offset=OptionalTunable(description='\n                        Overrides the target joint offset of the VFX.  \n                        This is used in case of point to point VFX where\n                        we want the effect to reach a destination\n                        offset from the target joint.\n                        ',
  disabled_name='no_override',
  enabled_name='override_offset',
  tunable=(TunableOffset())),
  callback_event_id=OptionalTunable(description='\n                        Specifies a callback xevt id we want the vfx to trigger\n                        when it fulfills a contracted duty.\n                        \n                        For example, it can call this xevt on point-to-point vfx\n                        if the effect reaches the target event.\n                        ',
  tunable=(Tunable(int, 0)))),
  key_type=Tunable(str, None, source_location=clip_actor_asm_source,
  source_query=clip_actor_state_source,
  source_sub_query=vfx_sub_query),
  allow_none=True), 
         sounds=TunableMapping(description='The sound overrides.', key_name='original_sound',
  value_name='replacement_sound',
  value_type=OptionalTunable(disabled_name='no_sound', enabled_name='play_sound',
  disabled_value=UNSET,
  tunable=TunableResourceKey(None, (sims4.resources.Types.PROPX,), description='The sound to play.')),
  key_type=Tunable(str, None, source_location=clip_actor_asm_source,
  source_query=clip_actor_state_source,
  source_sub_query=sound_sub_query)), 
         props=TunableMapping(description='\n                The props overrides.\n                ',
  value_type=TunableTuple(definition=TunableReference(description='\n                        The object to create to replace the prop\n                        ',
  manager=(services.definition_manager()),
  pack_safe=True),
  alternative_prop_definitions=OptionalTunable(description='\n                        If enabled, allows tuning other ways to override the prop.\n                        If none of these ways work, the tuned Definition will\n                        be used as a fallback.\n                        ',
  tunable=TunableTuple(description='\n                            Other ways to get a definition ID to override the prop.\n                            ',
  favorite_object_in_inventory=OptionalTunable(description="\n                                If enabled, allows looking for and using a \n                                favorite object in the Sim's inventory.\n                                ",
  tunable=TunableTuple(description='\n                                    ',
  favorite_tag=TunableTag(description="\n                                        If the Sim has a favorite object of this type \n                                        currently in their inventory, it will be used \n                                        as the prop override.\n                                        \n                                        If the Sim doesn't have a favorite of this \n                                        type, or their favorite is not currently in \n                                        their inventory, a random object found in \n                                        their inventory with this tag will be used \n                                        as the prop override.\n                                        \n                                        If there aren't any objects with this tag in \n                                        the Sim's inventory then the prop override \n                                        will fall back to the tuned Definition.\n                                        ",
  filter_prefixes=('Func', )),
  actor_asm_name=Tunable(description="\n                                        The name of the actor in the ASM. This is \n                                        usually 'x' or 'y'.\n                                        ",
  tunable_type=str,
  default='x'),
  random_choice_tests=TunableTestSet(description='\n                                        Objects with the favorite tag to be randomly chosen from inventory\n                                        should pass these tests first.\n                                        '))),
  favorite_object_by_definition=OptionalTunable(description="\n                                If enabled, looks for a favorite object not\n                                necessarily in the Sim's inventory.\n                                ",
  tunable=TunableTuple(description='\n                                    Tuple to hold the favorite tag to search for and the \n                                    actor ASM name.\n                                    ',
  favorite_tag=TunableTag(description='\n                                        If the Sim has a favorite object of this type\n                                        it will be set as the favorite.\n                                        \n                                        If it does not, the tuned definition will be set instead.\n                                        ',
  filter_prefixes=('Func', )),
  actor_asm_name=Tunable(description="\n                                        The name of the actor in the ASM. This is \n                                        usually 'x' or 'y'.\n                                        ",
  tunable_type=str,
  default='x'))))),
  from_actor=Tunable(description='\n                        The actor name inside the asm to copy the state over.\n                        ',
  tunable_type=str,
  default=None),
  states_to_override=TunableList(description='\n                        A list of states that will be transferred from\n                        the specified actor to the overridden prop.\n                        ',
  tunable=TunableReference(description='\n                            The state to apply on the props from the actor listed above.\n                            ',
  manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
  class_restrictions='ObjectState',
  pack_safe=True)),
  special_cases=TunableTuple(description='\n                        Tuning for special case prop overrides.\n                        ',
  set_baby_cloth_from_actor=OptionalTunable(description="\n                            If tuned, will set the baby's outfit based on a \n                            baby that is already an actor in the asm.\n                            ",
  tunable=Tunable(tunable_type=str,
  default=None))),
  sharing=OptionalTunable(description='\n                        If enabled, this prop may be shared across ASMs.\n                        ',
  tunable=(PropShareOverride.TunableFactory())),
  set_as_actor=OptionalTunable(description='\n                        If enabled the prop defined by override will be set\n                        as an actor of the ASM.\n                        This is used in cases like setting the chopsticks prop\n                        on the eat ASM.  In this ASM the chopsticks are set as \n                        an Object actor so they can animate. Currently we do\n                        not support props playing their own animations.  \n                        ',
  tunable=Tunable(description='\n                            Actor name that will be used on the ASM for the \n                            prop animation.\n                            ',
  tunable_type=str,
  default=None),
  enabled_name='actor_name'))), 
         prop_state_values=TunableMapping(description='\n                Tunable mapping from a prop actor name to a list of state\n                values to set. If conflicting data is tuned both here and in\n                the "props" field, the data inside "props" will override the\n                data tuned here.\n                ',
  value_type=TunableList(description='\n                    A list of state values that will be set on the specified\n                    actor.\n                    ',
  tunable=TunableReference(description='\n                        A new state value to apply to prop_actor.\n                        ',
  manager=(services.get_instance_manager(sims4.resources.Types.OBJECT_STATE)),
  class_restrictions='ObjectStateValue'))), 
         manifests=TunableList(description='\n                Manifests is a complex and seldom used override that lets you \n                change entries in the posture manifest from the ASM.\n                You can see how the fields, Actor, Family, Level, Specific, \n                Left, Right, and Surface, match the manifest entries in the \n                ASM. \n                ',
  tunable=TunableTuple(key=TunablePostureManifestOverrideKey(asm_source=asm_source),
  value=TunablePostureManifestOverrideValue(asm_source=asm_source))), 
         required_slots=TunableList(TunableRequiredSlotOverride(asm_source=asm_source), description='Required slot overrides'), 
         balloons=OptionalTunable(TunableList(description='\n                Balloons lets you add thought and talk balloons to animations. \n                This is a great way to put extra flavor into animations and \n                helps us stretch our content by creating combinations.\n                Balloon Animation Target is the participant who should display \n                the balloon.\n                Balloon Choices is a reference to the balloon to display, which \n                is its own tunable type.\n                Balloon Delay (and Random Offset) is how long, in real seconds, \n                to delay this balloon after the animation starts.  Note: for \n                looping animations, the balloon will always play immediately \n                due to a code limitation.\n                Balloon Target is for showing a balloon of a Sim or Object. \n                Set this to the participant type to show. This setting \n                overrides Balloon Choices. \n                ',
  tunable=(TunableBalloon()))), 
         animation_context=Tunable(description="\n                Animation Context - If checked, this animation will get a fresh \n                animation context instead of reusing the animation context of \n                its Interaction.\n                Normally, animation contexts are shared across an entire Super \n                Interaction. This allows mixers to use a fresh animation \n                context.\n                Ex: If a mixer creates a prop, using a fresh animation context \n                will cause that prop to be destroyed when the mixer finishes, \n                whereas re-using an existing animation context will cause the \n                prop to stick around until the mixer's SI is done. \n                ",
  tunable_type=bool,
  default=override_animation_context), 
         description=description, 
         verify_tunable_callback=TunableAnimationOverrides.verify_tunable_callback, **kwargs)


class TunableAnimationObjectOverrides(TunableAnimationOverrides):
    LOCKED_ARGS = {'manifests':None, 
     'required_slots':None, 
     'balloons':None, 
     'reactionlet':None}

    def __init__(self, description='Animation overrides to apply to every ASM to which this object is added.', **kwargs):
        (super().__init__)(locked_args=TunableAnimationObjectOverrides.LOCKED_ARGS, **kwargs)