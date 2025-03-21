#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# parent selected items to a new locator

from typing import Iterable

import modo
import modo.constants as c

from h3d_utilites.scripts.h3d_utils import parent_items_to, get_parent_index, match_pos_rot

from h3d_meshref_hierarchy_setup.scripts.h3d_kit_constants import PARENT_LOC_SFX


def main():
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    if not selected:
        return

    parent_align_item = selected[0]

    parent_loc = create_parent(selected, parent_align_item)
    parent_loc.select(replace=True)


def create_parent(items: Iterable[modo.Item], head_item: modo.Item) -> modo.Item:
    parent_loc_name = f'{head_item.name} {PARENT_LOC_SFX}'
    parent_loc = modo.Scene().addItem(itype=c.LOCATOR_TYPE, name=parent_loc_name)
    match_pos_rot(parent_loc, head_item)
    parent_items_to([parent_loc,], head_item.parent, get_parent_index(head_item))

    for item in items:
        parent_items_to([item,], parent_loc, get_parent_index(item))

    return parent_loc


if __name__ == '__main__':
    main()
