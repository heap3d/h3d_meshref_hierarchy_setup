#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# store transform info for selected items

from dataclasses import dataclass
import os

import modo
import modo.constants as c
from modo import dialogs

from h3d_utilites.scripts.h3d_utils import item_get_scale, item_get_position, item_get_rotation
from h3d_meshref_hierarchy_setup.scripts.select_meshref_meshes import is_meshref


@dataclass
class ItemInfo():
    name = ''
    scene = ''
    pos = modo.Vector3()
    rot = modo.Vector3()
    scl = modo.Vector3()


def main():
    items: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    info_lines: list[str] = []

    for item in items:
        if not is_meshref(item):
            continue
        item_info = ItemInfo()
        item_info.name = strip_meshref_name(item)
        item_info.scene = get_meshref_scene_name(item)
        item_info.pos = item_get_position(item)
        item_info.rot = item_get_rotation(item)
        item_info.scl = item_get_scale(item)

        info_lines.extend(get_item_lines(item_info))

    if not info_lines:
        dialogs.alert(title='Nothing to save', message='Please select meshref items.')
        return

    try:
        filename = dialogs.fileSave(
            'text', 'text', fspec='format',
            path=os.path.dirname(modo.Scene().filename)+'/items info')
    except TypeError:
        dialogs.alert(title='Can\'t locate the scene path.', message='Please save the scene.')
        return

    if filename:
        write_info(filename, info_lines)


def get_item_lines(item_info: ItemInfo) -> list[str]:
    item_lines = [
        f'{item_info.name}::scene::{item_info.scene}\n',
        f'{item_info.name}::mov::{" ".join([str(i) for i in item_info.pos])}\n',
        f'{item_info.name}::rot::{" ".join([str(i) for i in item_info.rot])}\n',
        f'{item_info.name}::scl::{" ".join([str(i) for i in item_info.scl])}\n',
    ]
    return item_lines


def write_info(filename: str, info_lines: list[str]):

    with open(filename, 'w') as file:
        file.writelines(info_lines)


def strip_meshref_name(item: modo.Item) -> str:
    if not is_meshref(item):
        return item.name

    scenename = get_meshref_scene_name(item)

    return str(item.name).split(f' ({scenename})')[0]


def get_meshref_scene_name(item: modo.Item) -> str:
    if not is_meshref(item):
        return ''

    return str(item.id).split(':')[0]


if __name__ == '__main__':
    main()
