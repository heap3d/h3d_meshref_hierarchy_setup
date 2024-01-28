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


def reset_hierarchy_info(item: modo.Item) -> None:
    # remove name prefix
    if item.name.startswith(h3dc.ROOT_PREFIX):
        item.name = item.name[len(h3dc.ROOT_PREFIX):]
    if item.name.startswith(h3dc.MESH_PREFIX):
        item.name = item.name[len(h3dc.MESH_PREFIX):]
    # remove description tag from the item
    lx.eval('item.tagRemove DESC')


def is_root_prefix(item: Union[modo.Item, None]) -> bool:
    if not item:
        return False
    if item.name.startswith(h3dc.ROOT_PREFIX):
        return True

    return False


def is_mesh_prefix(item: modo.Item) -> bool:
    if item.name.startswith(h3dc.MESH_PREFIX):
        return True

    return False


def main() -> None:
    roots = set()
    meshes = set()
    if not lx.args():
        locators: set[modo.Item] = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)  # type: ignore
        roots: set[modo.Item] = filter(is_root_prefix, locators)  # type: ignore
        meshes: set[modo.Item] = filter(is_mesh_prefix, locators)  # type: ignore
    elif h3dc.CMD_SELECTED in lx.args():  # type: ignore
        selected: set[modo.Item] = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)  # type: ignore
        roots: set[modo.Item] = filter(is_root_prefix, selected)  # type: ignore
        meshes: set[modo.Item] = filter(is_mesh_prefix, selected)  # type: ignore

    for root in roots:
        reset_hierarchy_info(root)

    for mesh in meshes:
        reset_hierarchy_info(mesh)


if __name__ == '__main__':
    main()
