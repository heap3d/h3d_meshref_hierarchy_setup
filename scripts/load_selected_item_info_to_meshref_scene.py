#!/usr/bin/python
# ================================
# (C)2025 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# EMAG
# modo python
# load items info from file to meshref scene

import os

import modo
import modo.constants as c
from modo import dialogs

from h3d_utilites.scripts.h3d_utils import item_set_position, item_set_rotation, item_set_scale

from scripts.save_meshref_info_from_host import POS, ROT, SCL
from scripts.load_item_info_to_meshref_scene import load_info_lines, decode_info


def main():
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    filename = dialogs.fileOpen('text', path=os.path.dirname(modo.Scene().filename))
    if not filename:
        return

    info_lines = load_info_lines(filename)

    item_infos = dict()
    for info_line in info_lines:
        if not info_line:
            continue
        info_items = info_line.strip().split('::')
        key, value = list(decode_info(info_items).items())[0]
        if info_items[0] not in item_infos:
            item_infos[info_items[0]] = dict()
        item_infos[info_items[0]][key] = value

    for name in item_infos:
        try:
            item = modo.Scene().item(name)
        except LookupError:
            continue

        if item not in selected:
            continue

        item_set_position(item, item_infos[name][POS])
        item_set_rotation(item, item_infos[name][ROT])
        item_set_scale(item, item_infos[name][SCL])


if __name__ == '__main__':
    main()
