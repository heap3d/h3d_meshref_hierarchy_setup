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
from typing import Union, Iterable

from h3d_utilites.scripts.h3d_utils import get_description_tag, set_description_tag
import h3d_meshref_hierarchy_setup.scripts.h3d_kit_constants as h3dc
from h3d_meshref_hierarchy_setup.scripts.meshref_hierarchy_reset import is_root_prefix, is_mesh_prefix


MSG_WAS_NOT_REPARENT = 'was not reparent: already processed'


def get_parent_info_by_tag(item: modo.Item) -> str:
    """get item parent info from item's description tag

    Args:
        item (modo.Item): item to get a description tag from

    Returns:
        str: parent info string
    """
    description = get_description_tag(item).splitlines()[0]
    return description


def get_transform_values_by_tag(item: modo.Item) -> tuple:
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

    try:
        pos = tuple(map(float, multiline_desc[1].split()))
        rot = tuple(map(float, multiline_desc[2].split()))
        scl = tuple(map(float, multiline_desc[3].split()))
    except IndexError:
        pos = (0.0, 0.0, 0.0)
        rot = (0.0, 0.0, 0.0)
        scl = (1.0, 1.0, 1.0)

    return tuple((pos, rot, scl))


def is_processed_by_tag(item: modo.Item) -> bool:
    """checks if item has processed mark

    Args:
        item (modo.Item): item to check

    Returns:
        bool: True if item contains the mark, False otherwise
    """
    tag = get_description_tag(item)
    if h3dc.PROCESSED_MARK in tag:
        return True

    return False


def add_processed_mark(item: modo.Item) -> None:
    """Add processed mark to the item

    Args:
        item (modo.Item): Item to proceed
    """
    tag = get_description_tag(item)
    processed_tag = f'{tag}\n{h3dc.PROCESSED_MARK}'
    set_description_tag(item, processed_tag)


def remove_processed_mark(item: modo.Item) -> None:
    tag = get_description_tag(item)
    parts = tag.split(h3dc.PROCESSED_MARK)
    try:
        cleaned_tag = f'{parts[0]}{parts[1]}'.strip()
        set_description_tag(item, cleaned_tag)
    except IndexError:
        print(f'<{item.name}> has no PROCESSED_MARK')


def reparent(mesh: modo.Item) -> None:
    """reparent item to respective root

    Args:
        item (modo.Item): item to reparent
    """
    root = get_mesh_root_by_tag(mesh)

    mesh.setParent(root)

    pos, rot, scl = get_transform_values_by_tag(mesh)

    try:
        mesh.position.set(pos)
        mesh.rotation.set(rot)
        mesh.scale.set(scl)
    except AttributeError:
        print(f'reparent alignment failed for item:<{mesh.name}>')


def get_mesh_root_by_tag(mesh: modo.Item) -> Union[modo.Item, None]:
    """get hierarchy root of the specified mesh item

    Args:
        mesh (modo.Item): mesh item

    Returns:
        modo.Item: hierarchy root item
    """
    if not is_mesh_prefix(mesh):
        return None

    roots = {i for i in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True) if is_root_prefix(i)}
    mesh_info = get_parent_info_by_tag(mesh)
    for root in roots:
        if get_parent_info_by_tag(root) == mesh_info:
            return root

    return None


def get_hierarchy_root_by_root(item: modo.Item) -> Union[modo.Item, None]:
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

    mesh_root = get_mesh_root_by_tag(item)

    if mesh_root:
        hierarchy_roots = mesh_root.parents
    else:
        hierarchy_roots = None
    if not hierarchy_roots:
        return mesh_root
    else:
        return hierarchy_roots[-1]


def get_hierarchy_meshesby_tag(root: Union[modo.Item, None]) -> set[modo.Item]:
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

    root_info = get_parent_info_by_tag(root)

    return {i for i in modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
            if get_parent_info_by_tag(i) == root_info}


def get_hierarchy_members(items: Iterable[modo.Item]) -> set[modo.Item]:
    meshes = set()
    for item in items:
        root = get_hierarchy_root_by_root(item)
        meshes = meshes.union(get_hierarchy_meshesby_tag(root))

    return meshes


def default_action():
    superlocators = modo.Scene().items(itype=c.LOCATOR_TYPE, superType=True)
    meshes = {i for i in superlocators if is_mesh_prefix(i)}
    reparent_meshes(meshes)


def selected_action():
    superlocators = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    meshes = {i for i in superlocators if is_mesh_prefix(i)}
    reparent_meshes(meshes)


def hierarchy_action():
    selected = modo.Scene().selectedByType(itype=c.LOCATOR_TYPE, superType=True)
    meshes = get_hierarchy_members(selected)
    reparent_meshes(meshes)


def reparent_meshes(meshes: Iterable[modo.Item]):
    for mesh in meshes:
        if not is_processed_by_tag(mesh):
            reparent(mesh=mesh)
            add_processed_mark(mesh)
        else:
            print(f'{mesh.name=} {MSG_WAS_NOT_REPARENT}')


def main():
    arg = ''
    if lx.args():
        arg = lx.args()[0]  # type: ignore

    actions = {
        h3dc.CMD_SELECTED: selected_action,
        h3dc.CMD_HIERARCHY: hierarchy_action,
    }

    action = actions.get(arg, default_action)
    action()


if __name__ == '__main__':
    main()
