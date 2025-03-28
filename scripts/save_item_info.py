#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# save transform info for selected meshref items to file

from dataclasses import dataclass, field
import os
from typing import Iterable

import modo
import modo.constants as c
from modo import dialogs

from h3d_utilites.scripts.h3d_utils import item_get_scale, item_get_position, item_get_rotation
from scripts.select_meshref_meshes import is_meshref


SCENE = 'scene'
TYPE = 'type'
IS_MESHREF = 'is_meshref'
HIERARCHY = 'hierarchy'
POS = 'pos'
ROT = 'rot'
SCL = 'scl'
NAME_SEPARATOR = r' \/ '


@dataclass
class ItemInfo():
    name = ''
    type = ''
    is_meshref = False
    scene = ''
    parents: list[modo.Item] = field(default_factory=lambda: [])
    pos = modo.Vector3()
    rot = modo.Vector3()
    scl = modo.Vector3()


def main():
    items: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    info_lines: list[str] = list()

    parents = set()
    for item in items:
        item_info = get_item_info(item, include_parents=True)
        info_lines.extend(get_item_lines(item_info))
        parents.update(item_info.parents)

    parents = parents.difference(items)
    for parent in parents:
        item_info = get_item_info(parent, include_parents=False)
        info_lines.extend(get_item_lines(item_info))

    if not info_lines:
        dialogs.alert(title='Nothing to save', message='Please select meshref items.')
        return

    try:
        filename = dialogs.fileSave(
            'text', 'text', fspec='format',
            path=f'{os.path.dirname(modo.Scene().filename)}/{get_meshref_scene_name(items[0])}')
    except TypeError:
        dialogs.alert(title='Can\'t locate the scene path.', message='Please save the scene.')
        return

    if not filename:
        return

    write_info(filename, info_lines)


def get_item_info(item: modo.Item, include_parents: bool) -> ItemInfo:
    item_info = ItemInfo()
    item_info.name = strip_meshref_name(item)
    item_info.type = str(item.type)
    item_info.is_meshref = is_meshref(item)
    item_info.scene = get_meshref_scene_name(item)
    item_info.pos = item_get_position(item)
    item_info.rot = item_get_rotation(item)
    item_info.scl = item_get_scale(item)

    item_info.parents.clear()
    if include_parents:
        item_info.parents.extend(get_item_parents(item))

    return item_info


def get_item_parents(item: modo.Item) -> tuple[modo.Item, ...]:
    if item_parents := item.parents:
        return tuple(item_parents)
    else:
        return tuple()


def get_item_lines(item_info: ItemInfo) -> tuple[str, ...]:
    item_lines = [
        f'{item_info.name}::{SCENE}::{item_info.scene}\n',
        f'{item_info.name}::{TYPE}::{item_info.type}\n'
        f'{item_info.name}::{IS_MESHREF}::{item_info.is_meshref}\n'
        f'{item_info.name}::{HIERARCHY}::{NAME_SEPARATOR.join([parent.name for parent in item_info.parents])}\n',
        f'{item_info.name}::{POS}::{" ".join([str(i) for i in item_info.pos])}\n',
        f'{item_info.name}::{ROT}::{" ".join([str(i) for i in item_info.rot])}\n',
        f'{item_info.name}::{SCL}::{" ".join([str(i) for i in item_info.scl])}\n',
    ]
    return tuple(item_lines)


def write_info(filename: str, info_lines: Iterable[str]):

    with open(filename, 'w') as file:
        file.writelines(info_lines)


def strip_meshref_name(item: modo.Item) -> str:
    if not is_meshref(item):
        return item.name

    scenename = get_meshref_scene_name(item)

    return str(item.name).split(f' ({scenename})')[0]


def get_meshref_scene_name(item: modo.Item) -> str:
    if not is_meshref(item):
        return os.path.splitext(modo.Scene().name)[0]

    return str(item.id).split(':')[0]


if __name__ == '__main__':
    main()
