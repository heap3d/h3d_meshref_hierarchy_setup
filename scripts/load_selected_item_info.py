#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# load items info from file

import os
from typing import Iterable

import lx
import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import (
    item_set_position, item_set_rotation, item_set_scale,
    parent_items_to, get_parent_index,
    get_user_value,
)

from scripts.save_item_info import (
    ItemInfo, POS, ROT, SCL, SCENE, TYPE, IS_MESHREF, HIERARCHY, PARENT_INDEX,
    NAME_SEPARATOR, TAG_SEPARATOR, strip_meshref_name
)
from scripts.select_meshref_meshes import is_meshref


ItemsInfo = dict[str, ItemInfo]
Transforms = tuple[modo.Vector3, modo.Vector3, modo.Vector3]

LOCATOR_SUFFIX = ' loc'
USERVAL_NAME_HIERARCHY = 'h3d_mhs_full_hierarchy'
USERVAL_NAME_TOLERANCE = 'h3d_mhs_tolerance'

TOLERANCE = get_user_value(USERVAL_NAME_TOLERANCE)
FULL_HIERARCHY = get_user_value(USERVAL_NAME_HIERARCHY) == 1


def main():
    selected: list[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    if not selected:
        return

    try:
        path = os.path.dirname(modo.Scene().filename)
    except TypeError:
        path = ''
    filename = modo.dialogs.fileOpen('text', path=path)
    if isinstance(filename, list):
        raise ValueError('Multiple files selected. Please select one file only.')
    if not filename:
        return

    items_info = load_items_info(filename)
    working_items = get_working_items(selected, items_info)
    if not working_items:
        modo.dialogs.alert('Aborted', 'No info for selected items found.')
        return

    process_items(working_items, items_info, FULL_HIERARCHY)

    hierarchy_items: list[modo.Item] = selected[:]
    for selected_item in selected:
        if selected_item.parents:
            hierarchy_items.extend(selected_item.parents)
    meshref_transform_to_locator(hierarchy_items, TOLERANCE)


def load_items_info(filename: str) -> ItemsInfo:
    if not filename:
        raise ValueError('File name is not specified.')

    info_lines = [line.strip() for line in load_info_lines(filename)]

    items_info: ItemsInfo = dict()
    for info_line in info_lines:
        if not info_line:
            continue
        extract_info_line(info_line, items_info)

    return items_info


def get_working_items(items: Iterable[modo.Item], items_info: ItemsInfo) -> tuple[modo.Item, ...]:
    return tuple(i for i in items if strip_meshref_name(i) in items_info)


def process_items(items: Iterable[modo.Item], items_info: ItemsInfo, full_hierarchy: bool):
    for item in items:
        item_set_position(item, items_info[strip_meshref_name(item)].pos)
        item_set_rotation(item, items_info[strip_meshref_name(item)].rot)
        item_set_scale(item, items_info[strip_meshref_name(item)].scl)

        parents: list[modo.Item] = []
        if full_hierarchy:
            hierarchy = items_info[strip_meshref_name(item)].hierarchy
        else:
            hierarchy = items_info[strip_meshref_name(item)].hierarchy[:1]
        for parent_name in hierarchy:
            parents.append(
                get_item(parent_name, items_info[parent_name].scene, items_info[parent_name].itype)
            )

        if not parents:
            continue

        child = item
        for parent in parents:
            parent_items_to(
                (child,),
                parent,
                items_info[strip_meshref_name(child)].parent_index,
                inplace=False
            )
            item_set_position(parent, items_info[strip_meshref_name(parent)].pos)
            item_set_rotation(parent, items_info[strip_meshref_name(parent)].rot)
            item_set_scale(parent, items_info[strip_meshref_name(parent)].scl)
            child = parent


def meshref_transform_to_locator(items: Iterable[modo.Item], tolerance: float):
    for item in items:
        if not is_meshref(item):
            continue

        if is_zero_transforms(item, tolerance):
            continue

        new_loc = modo.Scene().addItem(itype=c.LOCATOR_TYPE, name=f'{item.name}{LOCATOR_SUFFIX}')
        parent_items_to((new_loc,), item, inplace=False)
        parent_items_to((new_loc,), item.parent, get_parent_index(item), inplace=True)
        parent_items_to((item,), new_loc, inplace=True)
        parent_items_to(item.children(), new_loc, index=1, inplace=True)


def load_info_lines(filename: str) -> list[str]:
    with open(filename) as file:
        return file.readlines()


def extract_info_line(info_line: str, items_info: ItemsInfo):
    item_name, data_tag, data_line = info_line.split(TAG_SEPARATOR)
    if item_name not in items_info:
        items_info[item_name] = ItemInfo()
    items_info[item_name].name = item_name
    if data_tag == SCENE:
        items_info[item_name].scene = data_line
    if data_tag == TYPE:
        items_info[item_name].itype = data_line
    if data_tag == IS_MESHREF:
        items_info[item_name].is_meshref = data_line == 'True'
    if data_tag == HIERARCHY:
        if data_line:
            names = data_line.split(NAME_SEPARATOR)
            items_info[item_name].hierarchy.extend(names)
    if data_tag == PARENT_INDEX:
        items_info[item_name].parent_index = int(data_line)
    if data_tag == POS:
        items_info[item_name].pos = modo.Vector3([float(i) for i in data_line.split(' ')])
    if data_tag == ROT:
        items_info[item_name].rot = modo.Vector3([float(i) for i in data_line.split(' ')])
    if data_tag == SCL:
        items_info[item_name].scl = modo.Vector3([float(i) for i in data_line.split(' ')])


def get_item(name: str, meshref_scene: str, itype: str) -> modo.Item:
    if not name:
        raise ValueError('No item name provided.')

    try:
        return get_item_by_meshref_name(name, meshref_scene)
    except LookupError:
        return modo.Scene().addItem(itype, name)


def get_item_by_meshref_name(name: str, meshref_scene: str) -> modo.Item:
    try:
        return modo.Scene().item(f'{name} ({meshref_scene})')
    except LookupError:
        return modo.Scene().item(name)


def get_transforms(item: modo.Item) -> Transforms:
    pos = modo.Vector3()
    pos.x = lx.eval(f'transform.channel pos.X ? item:{{{item.id}}}')
    pos.y = lx.eval(f'transform.channel pos.Y ? item:{{{item.id}}}')
    pos.z = lx.eval(f'transform.channel pos.Z ? item:{{{item.id}}}')
    rot = modo.Vector3()
    rot.x = lx.eval(f'transform.channel rot.X ? item:{{{item.id}}}')
    rot.y = lx.eval(f'transform.channel rot.Y ? item:{{{item.id}}}')
    rot.z = lx.eval(f'transform.channel rot.Z ? item:{{{item.id}}}')
    scl = modo.Vector3()
    scl.x = lx.eval(f'transform.channel scl.X ? item:{{{item.id}}}')
    scl.y = lx.eval(f'transform.channel scl.Y ? item:{{{item.id}}}')
    scl.z = lx.eval(f'transform.channel scl.Z ? item:{{{item.id}}}')

    return (pos, rot, scl)


def is_zero_transforms(item: modo.Item, tolerance: float) -> bool:
    pos, rot, scl = get_transforms(item)

    if not pos.equals(modo.Vector3(), tolerance):
        return False

    if not rot.equals(modo.Vector3(), tolerance):
        return False

    return scl.equals(modo.Vector3(1, 1, 1), tolerance)


def is_transforms_matched(transforms1: Transforms, transfroms2: Transforms, tolerance: float) -> bool:
    return all(v1.equals(v2, tolerance) for v1, v2 in zip(transforms1, transfroms2))


if __name__ == '__main__':
    main()
