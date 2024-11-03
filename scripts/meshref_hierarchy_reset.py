#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# hierarchy reset tool. Clean up all hierarchy info tags
# usage:
# 1. select items if needed
# 2. run Reset Hierarchy Info command or SHIFT + Reset Selected to process selected items only

import modo
import modo.constants as c
import lx
from typing import Union

import h3d_meshref_hierarchy_setup.scripts.h3d_kit_constants as h3dc
from h3d_utilites.scripts.h3d_debug import fn_in, fn_out, prints


def reset_hierarchy_info(item: modo.Item) -> None:
    # remove name prefix
    try:
        if item.name.startswith(h3dc.ROOT_PREFIX):
            item.name = item.name[len(h3dc.ROOT_PREFIX):]
        if item.name.startswith(h3dc.MESH_PREFIX):
            item.name = item.name[len(h3dc.MESH_PREFIX):]
    except RuntimeError:
        prints(f'Failed to reset item name: <{item.name}>')

    # remove description tag from the item
    try:
        item.select(replace=True)
        lx.eval('item.tagRemove DESC')
    except RuntimeError:
        prints(f'Failed to remove description tag: <{item.name}>')


def is_root_prefix(item: Union[modo.Item, None]) -> bool:
    fn_in(f'<{item.name=}> : <{item}>')  # type: ignore

    prints(item)
    if not item:
        fn_out('not item: False')
        return False
    if item.name.startswith(h3dc.ROOT_PREFIX):
        fn_out(f'item.name.startswith({h3dc.ROOT_PREFIX=}): return True')
        return True

    fn_out('return False')
    return False


def is_mesh_prefix(item: modo.Item) -> bool:
    if item.name.startswith(h3dc.MESH_PREFIX):
        return True

    return False


def main() -> None:
    roots = set()
    meshes = set()
    if not lx.args():
        locators: set[modo.Item] = set(modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True))
        prints(locators)
        roots: set[modo.Item] = set(filter(is_root_prefix, locators))
        prints(roots)
        meshes: set[modo.Item] = set(filter(is_mesh_prefix, locators))
        prints(meshes)
    elif h3dc.CMD_SELECTED in lx.args():  # type: ignore
        selected: set[modo.Item] = set(modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True))
        prints(selected)
        roots: set[modo.Item] = set(filter(is_root_prefix, selected))
        prints(roots)
        meshes: set[modo.Item] = set(filter(is_mesh_prefix, selected))
        prints(meshes)

    for root in roots:
        reset_hierarchy_info(root)

    for mesh in meshes:
        reset_hierarchy_info(mesh)


if __name__ == '__main__':
    main()
