#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# load items info from file to meshref scene

import os
from typing import Union, Iterable

import modo
import modo.constants as c
from modo import dialogs

from h3d_utilites.scripts.h3d_utils import item_set_position, item_set_rotation, item_set_scale

from scripts.save_item_info import POS, ROT, SCL, SCENE, ItemInfo


def main():
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    filename = dialogs.fileOpen('text', path=os.path.dirname(modo.Scene().filename))
    if isinstance(filename, list):
        filename = filename[0]
    if not filename:
        return

    items_info = load_items_info(filename)
    process_items(selected, items_info)


def load_items_info(filename: str) -> dict:
    if not filename:
        raise ValueError('File name is not specified.')

    info_lines = load_info_lines(filename)

    items_info = dict()
    for info_line in info_lines:
        if not info_line:
            continue
        info_items = info_line.strip().split('::')
        key, value = list(decode_info_line(info_items).items())[0]
        if info_items[0] not in items_info:
            items_info[info_items[0]] = dict()
        items_info[info_items[0]][key] = value

    return items_info


def process_items(items: Iterable[modo.Item], items_info: dict):
    create_hierarchy(items_info)

    for name in items_info:
        try:
            item = get_item_name(name, items_info[name])
        except LookupError:
            continue

        if item not in items:
            continue

        apply_item_info(item, items_info[name])


def load_info_lines(filename: str) -> list[str]:
    with open(filename) as file:
        return file.readlines()


def decode_info_line(infos: list[str]) -> dict[str, Union[str, modo.Vector3]]:
    tag = infos[1]
    if tag == 'scene':
        return {tag: infos[2]}

    return {tag: modo.Vector3(*map(float, infos[2].strip().split(' ')))}


def create_hierarchy(items_info: dict):
    ...


def get_item_name(name: str, item_info: dict) -> modo.Item:
    try:
        return modo.Scene().item(f'{name} ({item_info[SCENE]})')
    except LookupError as e:
        raise LookupError(e)


def get_meshref_name(name: str) -> modo.Item:
    try:
        return modo.Scene().item(name)
    except LookupError as e:
        raise LookupError(e)


def apply_item_info(item: modo.Item, item_info: dict):
    item_set_position(item, item_info[POS])
    item_set_rotation(item, item_info[ROT])
    item_set_scale(item, item_info[SCL])


if __name__ == '__main__':
    main()
