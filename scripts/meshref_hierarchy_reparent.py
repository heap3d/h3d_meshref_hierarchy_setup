#!/usr/bin/python
# ================================
# (C)2024 Dmytro Holub
# heap3d@gmail.com
# --------------------------------
# modo python
# EMAG
# hierarchy reparent tool to restore hierarchy from early saved scenes
# usage:
# 1. load a locators hierarchy scene into the current scene
# 2. load a geometry scene into the current scene
# 3. run Reparent All Meshes
# OR
# 3. select one of the loaded items and run CTRL + Reparent Selected Hierarchy command
# OR
# 3. select loaded items and run SHIFT + Reparent Selected Meshes command

import modo
import lx
import modo.constants as c
from typing import Union

from h3d_utilites.scripts.h3d_debug import H3dDebug
from h3d_utilites.scripts.h3d_utils import replace_file_ext, get_description_tag
import h3d_meshref_hierarchy_setup.scripts.h3d_kit_constants as h3dc
from h3d_meshref_hierarchy_setup.scripts.meshref_hierarchy_reset import is_root_prefix, is_mesh_prefix


def get_parent_info(item: modo.Item) -> str:
    """get item parent info from item's description tag

    Args:
        item (modo.Item): item to get a description tag from

    Returns:
        str: parent info string
    """
    description = get_description_tag(item).splitlines()[0]
    return description


def get_transform_values(item: modo.Item) -> tuple:
    """get transform values from item's description tag

    Args:
        item (modo.Item): item to get a description tag from

    Returns:
        tuple ((px, py, pz), (rx, ry, rz), (sx, sy, sz))
        where
        (px, py, pz): position values
        (rx, ry, rz): rotation values
        (sx, sy, sz): scale values
    """
    multiline_desc = get_description_tag(item).splitlines()

    pos = tuple(map(float, multiline_desc[1].split()))
    h3dd.print_debug(f'pos: {pos}')
    rot = tuple(map(float, multiline_desc[2].split()))
    h3dd.print_debug(f'rot: {rot}')
    scl = tuple(map(float, multiline_desc[3].split()))
    h3dd.print_debug(f'scl: {scl}')

    return tuple((pos, rot, scl))


def reparent(mesh: modo.Item) -> None:
    """reparent item to respective root

    Args:
        item (modo.Item): item to reparent
    """
    root = get_mesh_root(mesh)

    mesh.setParent(root)

    pos, rot, scl = get_transform_values(mesh)

    mesh.position.set(pos)
    mesh.rotation.set(rot)
    mesh.scale.set(scl)


def get_mesh_root(mesh: modo.Item) -> Union[modo.Item, None]:
    """get hierarchy root of the specified mesh item

    Args:
        mesh (modo.Item): mesh item

    Returns:
        modo.Item: hierarchy root item
    """
    if not is_mesh_prefix(mesh):
        return None

    roots = {i for i in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True) if is_root_prefix(i)}
    mesh_info = get_parent_info(mesh)
    for root in roots:
        if get_parent_info(root) == mesh_info:
            return root

    return None


def get_hierarchy_root(item: modo.Item) -> Union[modo.Item, None]:
    """gets hierarchy root of the specified item

    Args:
        item (modo.Item): item for hierarchy root search

    Returns:
        modo.Item: hierarchy root item
    """
    if is_root_prefix(item):
        parents = item.parents
        if parents:
            return parents[-1]
        else:
            return item
    elif not is_mesh_prefix(item):
        return None

    mesh_root = get_mesh_root(item)

    if mesh_root:
        hierarchy_roots = mesh_root.parents
    else:
        hierarchy_roots = None
    if not hierarchy_roots:
        return mesh_root
    else:
        return hierarchy_roots[-1]


def get_hierarchy_meshes(root: Union[modo.Item, None]) -> set[modo.Item]:
    """get meshes set belong to the hierarchy root

    Args:
        root (modo.Item): hierarchy root to search mesh children

    Returns:
        set[modo.Item]: set of mesh items, children of hierarchy root
    """
    if not root:
        return set()

    if not is_root_prefix(root):
        return set()

    root_info = get_parent_info(root)

    return {i for i in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
            if get_parent_info(i) == root_info}


def main():
    if not lx.args():
        superlocators = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
        meshes = {i for i in superlocators if is_mesh_prefix(i)}
        for mesh in meshes:
            reparent(mesh=mesh)
    elif h3dc.CMD_SELECTED:
        superlocators = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
        meshes = {i for i in superlocators if is_mesh_prefix(i)}
        for mesh in meshes:
            reparent(mesh=mesh)
    elif h3dc.CMD_HIERARCHY:
        selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
        meshes = set()
        for item in selected:
            root = get_hierarchy_root(item)
            meshes = meshes.union(get_hierarchy_meshes(root))
        for mesh in meshes:
            reparent(mesh=mesh)


h3dd = H3dDebug(enable=False, file=replace_file_ext(modo.Scene().filename, '.log'))

if __name__ == '__main__':
    main()
