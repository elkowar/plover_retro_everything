#!/usr/bin/env python
from typing import *
import itertools
import functools

from plover.engine import StenoEngine
from plover.translation import Translator, Stroke, Translation
from plover.formatting import _Context, _Action, _atom_to_action, _translation_to_actions
import os


def flatten(x: List[List]) -> List:
    return list(itertools.chain.from_iterable(x))


def recursively_unfuck_thing(stroke: Stroke, t: Translation) -> List[str]:
    if t.strokes[-1] == stroke:
        return flatten([recursively_unfuck_thing(stroke, subtrans) for subtrans in t.replaced])
    else:
        return [t.english or ""]


def retro_everything(translator: Translator, stroke: Stroke, cmdline: str):
    print("\n\n\nRetro everything invoked with: " + str(stroke) + ", " + cmdline)
    args = cmdline.split("::")
    left_char = args[0]
    right_char = args[1]

    all_translations = translator.get_state().translations

    affected_translation_cnt = len(list(
        itertools.takewhile(
            lambda x: x.strokes[-1] == stroke,
            reversed(all_translations)
        )
    ))

    # translations that _will_ be affected
    affected_translations = all_translations[-(affected_translation_cnt + 1):]

    affected_strokes = flatten([x.strokes or []
                                for x in affected_translations])
    affected_string = " ".join(
        flatten([recursively_unfuck_thing(stroke, t) for t in affected_translations]))

    my_trans = Translation(
        affected_strokes + [stroke], left_char + affected_string + right_char)
    my_trans.replaced = affected_translations

    translator.translate_translation(my_trans)
